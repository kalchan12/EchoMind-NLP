"""
Natural Language Processing Module
=================================

This module handles text processing and response generation for the EchoMind-NLP assistant.
It provides a simple but extensible interface for text analysis and response generation.

Current Features:
- Basic command recognition (/help, /clear, etc.)
- Echo responses with context awareness
- Text analysis and statistics
- Extensible architecture for future NLP enhancements

Future Enhancements:
- Integration with spaCy for NER and text analysis
- Transformers-based response generation
- OpenAI API integration for enhanced responses
- Intent classification and entity extraction
"""

from typing import Dict, List, Optional, Any
import re
from datetime import datetime
from loguru import logger


class NLPProcessor:
    """
    Natural Language Processing processor for EchoMind-NLP.
    
    This class handles text analysis, command recognition, and response generation.
    It's designed to be easily extensible with more sophisticated NLP capabilities.
    
    Attributes:
        commands: Dictionary of recognized commands and their handlers
        response_templates: Templates for generating responses
    """
    
    def __init__(self) -> None:
        """Initialize the NLP processor with commands and templates."""
        self.commands = {
            "/help": self._handle_help,
            "help": self._handle_help,
            "/clear": self._handle_clear,
            "clear": self._handle_clear,
            "/status": self._handle_status,
            "status": self._handle_status,
            "/time": self._handle_time,
            "time": self._handle_time,
            "/echo": self._handle_echo,
            "echo": self._handle_echo,
        }
        
        self.response_templates = {
            "welcome": "Hello! I'm EchoMind, your voice and text assistant. How can I help you today?",
            "empty_input": "Please say something or type a message to begin our conversation.",
            "context_available": "I have context from our previous conversation to help provide better responses.",
            "command_processed": "Command processed successfully.",
        }
    
    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate a response based on user input and conversation context.
        
        Args:
            prompt: User's input text
            context: Optional conversation context from previous turns
        
        Returns:
            Generated response text
        """
        # Clean and validate input
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            return self.response_templates["empty_input"]
        
        # Check for commands first
        if self._is_command(cleaned_prompt):
            return self._process_command(cleaned_prompt)
        
        # Generate contextual response
        return self._generate_contextual_response(cleaned_prompt, context)
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and extract useful information.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary containing analysis results
        """
        cleaned_text = text.strip()
        
        analysis = {
            "length": len(cleaned_text),
            "word_count": len(cleaned_text.split()),
            "character_count": len(cleaned_text),
            "is_empty": not bool(cleaned_text),
            "is_command": self._is_command(cleaned_text),
            "has_question": "?" in cleaned_text,
            "has_exclamation": "!" in cleaned_text,
            "lowercase": cleaned_text.lower(),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Add sentiment analysis (basic)
        analysis["sentiment"] = self._analyze_sentiment(cleaned_text)
        
        # Add language detection hints
        analysis["language_hints"] = self._detect_language_hints(cleaned_text)
        
        return analysis
    
    def _is_command(self, text: str) -> bool:
        """Check if text is a recognized command."""
        return text.lower() in self.commands
    
    def _process_command(self, command: str) -> str:
        """Process a recognized command."""
        command_lower = command.lower()
        if command_lower in self.commands:
            return self.commands[command_lower]()
        return f"Unknown command: {command}"
    
    def _generate_contextual_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate a contextual response based on user input and conversation history.
        
        Args:
            prompt: User's input text
            context: Optional conversation context
        
        Returns:
            Contextual response
        """
        # Basic echo response with context awareness
        response_parts = [f"You said: \"{prompt}\""]
        
        if context:
            response_parts.append(self.response_templates["context_available"])
        
        # Add some variety to responses
        if len(prompt) > 50:
            response_parts.append("That's quite a detailed message!")
        elif len(prompt) < 10:
            response_parts.append("Short and sweet!")
        
        return " ".join(response_parts)
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis."""
        text_lower = text.lower()
        
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy", "love", "like"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "sad", "angry", "frustrated"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _detect_language_hints(self, text: str) -> List[str]:
        """Detect language hints based on text patterns."""
        hints = []
        
        # Basic language detection patterns
        if re.search(r'[а-яё]', text, re.IGNORECASE):
            hints.append("russian")
        if re.search(r'[ñáéíóúü]', text, re.IGNORECASE):
            hints.append("spanish")
        if re.search(r'[àâäéèêëïîôöùûüÿç]', text, re.IGNORECASE):
            hints.append("french")
        if re.search(r'[äöüß]', text, re.IGNORECASE):
            hints.append("german")
        
        return hints
    
    # Command handlers
    def _handle_help(self) -> str:
        """Handle help command."""
        help_text = """
**EchoMind-NLP Assistant Help**

**Available Commands:**
- `/help` or `help` - Show this help message
- `/clear` or `clear` - Clear conversation history
- `/status` or `status` - Show system status
- `/time` or `time` - Show current time
- `/echo` or `echo` - Echo mode (default)

**Features:**
- Text chat with conversation memory
- Voice input/output (coming soon)
- Context-aware responses
- Configurable settings

**Tips:**
- Just type naturally to chat
- Use commands for system operations
- Your conversation history is automatically saved
        """
        return help_text.strip()
    
    def _handle_clear(self) -> str:
        """Handle clear command."""
        return "Conversation history cleared. Starting fresh!"
    
    def _handle_status(self) -> str:
        """Handle status command."""
        return f"EchoMind-NLP is running. Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    def _handle_time(self) -> str:
        """Handle time command."""
        return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    def _handle_echo(self) -> str:
        """Handle echo command."""
        return "Echo mode activated. I'll repeat what you say with some context!"


