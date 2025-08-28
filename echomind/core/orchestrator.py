"""
Assistant Orchestrator
=====================

This module orchestrates the interaction between different components of the EchoMind-NLP assistant.
It manages conversation flow, memory, and coordinates between NLP processing and user interface.

Responsibilities:
- Manage conversation state and memory
- Coordinate between NLP processor and memory
- Handle text input/output flow
- Provide conversation statistics and management
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from loguru import logger

from echomind.core.memory import ConversationMemory
from echomind.core.nlp import NLPProcessor
from echomind.config import settings

# Import speech processing modules
try:
    from echomind.speech.stt_fasterwhisper import FasterWhisperSTT
    from echomind.speech.tts_pyttsx3 import Pyttsx3TTS
    from echomind.speech.audio_utils import AudioUtils
    SPEECH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Speech modules not available: {e}")
    SPEECH_AVAILABLE = False


class AssistantOrchestrator:
    """
    Main orchestrator for the EchoMind-NLP assistant.
    
    This class coordinates all the components of the assistant, managing
    conversation flow, memory, and response generation.
    
    Attributes:
        memory: Conversation memory manager
        nlp: Natural language processor
        conversation_start: Timestamp when conversation started
        total_turns: Total number of conversation turns processed
    """
    
    def __init__(self) -> None:
        """
        Initialize the assistant orchestrator.
        
        Sets up memory management, NLP processing, and speech processing
        with configuration from settings.
        """
        self.memory = ConversationMemory(max_turns=settings.max_conversation_turns)
        self.nlp = NLPProcessor()
        self.conversation_start = datetime.now()
        self.total_turns = 0
        
        # Initialize speech processing if available
        self.stt_processor = None
        self.tts_processor = None
        self.speech_enabled = SPEECH_AVAILABLE
        
        if self.speech_enabled:
            try:
                self.stt_processor = FasterWhisperSTT(
                    model_size=settings.whisper_model_size,
                    language=settings.stt_language
                )
                self.tts_processor = Pyttsx3TTS()
                logger.info("Speech processing initialized")
            except Exception as e:
                logger.error(f"Failed to initialize speech processing: {e}")
                self.speech_enabled = False
        
        logger.info(f"Assistant orchestrator initialized (speech: {self.speech_enabled})")
    
    def handle_text(self, user_text: str) -> str:
        """
        Process user text input and generate a response.
        
        This is the main entry point for text processing. It:
        1. Analyzes the input text
        2. Retrieves relevant context from memory
        3. Generates a contextual response
        4. Stores the interaction in memory
        
        Args:
            user_text: User's input text
        
        Returns:
            Generated response text
        """
        if not user_text.strip():
            return "Please provide some text to process."
        
        try:
            # Get conversation context
            context = self._get_context()
            
            # Generate response using NLP processor
            reply = self.nlp.generate(user_text, context=context)
            
            # Store the interaction in memory
            self.memory.add_turn(user_text, reply)
            self.total_turns += 1
            
            logger.debug(f"Processed turn {self.total_turns}: {len(user_text)} chars -> {len(reply)} chars")
            
            return reply
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return f"I encountered an error processing your message: {str(e)}"
    
    def handle_voice_input(self, audio_data: bytes) -> str:
        """
        Process voice input using speech-to-text.
        
        Args:
            audio_data: Raw audio data
        
        Returns:
            Generated response text
        """
        if not self.speech_enabled or not self.stt_processor:
            return "Speech processing is not available. Please use text input."
        
        try:
            # Transcribe audio to text
            transcribed_text = self.stt_processor.transcribe(audio_data)
            
            if not transcribed_text.strip():
                return "I couldn't hear anything. Please try speaking again."
            
            logger.info(f"Transcribed: '{transcribed_text}'")
            
            # Process the transcribed text
            return self.handle_text(transcribed_text)
            
        except Exception as e:
            logger.error(f"Voice processing failed: {e}")
            return f"Sorry, I had trouble processing your voice input: {str(e)}"
    
    def synthesize_response(self, text: str) -> bytes:
        """
        Convert text response to speech using text-to-speech.
        
        Args:
            text: Text to convert to speech
        
        Returns:
            Audio data as bytes
        """
        if not self.speech_enabled or not self.tts_processor:
            return b""
        
        try:
            audio_data = self.tts_processor.synthesize(text)
            logger.info(f"Synthesized {len(text)} characters to {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return b""
    
    def get_speech_info(self) -> Dict[str, Any]:
        """
        Get information about speech processing capabilities.
        
        Returns:
            Dictionary containing speech processing information
        """
        info = {
            "speech_enabled": self.speech_enabled,
            "stt_available": self.stt_processor is not None,
            "tts_available": self.tts_processor is not None,
        }
        
        if self.stt_processor:
            info["stt_info"] = self.stt_processor.get_model_info()
        
        if self.tts_processor:
            info["tts_info"] = self.tts_processor.get_engine_info()
        
        return info
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get conversation statistics and metadata.
        
        Returns:
            Dictionary containing conversation statistics
        """
        return {
            "total_turns": self.total_turns,
            "memory_turns": self.memory.count(),
            "conversation_duration": str(datetime.now() - self.conversation_start),
            "conversation_start": self.conversation_start.isoformat(),
            "memory_max_turns": self.memory.max_turns,
            "is_memory_empty": self.memory.is_empty(),
        }
    
    def get_recent_context(self, turns: int = 3) -> str:
        """
        Get recent conversation context for analysis or debugging.
        
        Args:
            turns: Number of recent turns to include
        
        Returns:
            Formatted recent conversation context
        """
        return self.memory.get_recent_context(turns)
    
    def clear_conversation(self) -> str:
        """
        Clear the conversation history and reset statistics.
        
        Returns:
            Confirmation message
        """
        self.memory.clear()
        self.conversation_start = datetime.now()
        self.total_turns = 0
        
        logger.info("Conversation cleared and reset")
        return "Conversation history cleared. Starting fresh!"
    
    def export_conversation(self, filepath: str) -> str:
        """
        Export conversation history to a file.
        
        Args:
            filepath: Path where to save the conversation
        
        Returns:
            Success/error message
        """
        try:
            self.memory.save_to_file(filepath)
            logger.info(f"Conversation exported to {filepath}")
            return f"Conversation exported successfully to {filepath}"
        except Exception as e:
            logger.error(f"Failed to export conversation: {e}")
            return f"Failed to export conversation: {str(e)}"
    
    def import_conversation(self, filepath: str) -> str:
        """
        Import conversation history from a file.
        
        Args:
            filepath: Path to the conversation file to import
        
        Returns:
            Success/error message
        """
        try:
            self.memory.load_from_file(filepath)
            logger.info(f"Conversation imported from {filepath}")
            return f"Conversation imported successfully from {filepath}"
        except Exception as e:
            logger.error(f"Failed to import conversation: {e}")
            return f"Failed to import conversation: {str(e)}"
    
    def _get_context(self) -> Optional[str]:
        """
        Get relevant context from conversation memory.
        
        Returns:
            Formatted context string or None if no context available
        """
        if self.memory.is_empty():
            return None
        
        # Get the last few turns for context
        return self.memory.get_recent_context(turns=3)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status information.
        
        Returns:
            Dictionary containing system status
        """
        stats = self.get_conversation_stats()
        speech_info = self.get_speech_info()
        
        return {
            **stats,
            "system_info": {
                "config": {
                    "whisper_model_size": settings.whisper_model_size,
                    "stt_language": settings.stt_language,
                    "max_conversation_turns": settings.max_conversation_turns,
                    "theme": settings.theme,
                },
                "capabilities": {
                    "text_processing": True,
                    "voice_processing": self.speech_enabled,
                    "memory_management": True,
                    "context_awareness": True,
                },
                "speech": speech_info
            }
        }


