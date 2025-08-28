"""
pyttsx3 Text-to-Speech Implementation
====================================

This module provides text-to-speech functionality using pyttsx3,
which is a cross-platform TTS library that uses system voices.
"""

import io
from typing import List
from loguru import logger

from .tts_base import TTSProcessor


class Pyttsx3TTS(TTSProcessor):
    """
    pyttsx3 implementation of text-to-speech processing.
    
    This class provides TTS functionality using system voices
    through the pyttsx3 library. It works offline and uses
    the voices installed on the system.
    """
    
    def __init__(self, voice: str = "default", speed: float = 1.0) -> None:
        """
        Initialize the pyttsx3 TTS processor.
        
        Args:
            voice: Voice to use for speech synthesis
            speed: Speech rate (1.0 = normal speed)
        """
        super().__init__(voice, speed)
        self.engine = None
        
    def initialize(self) -> None:
        """
        Initialize the pyttsx3 engine.
        
        Loads the TTS engine and prepares it for synthesis.
        """
        try:
            import pyttsx3
            
            logger.info("Initializing pyttsx3 TTS engine")
            
            # Initialize the TTS engine
            self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', int(200 * self.speed))  # Speed (words per minute)
            self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Set voice if specified
            if self.voice != "default":
                voices = self.engine.getProperty('voices')
                for v in voices:
                    if self.voice in v.name.lower():
                        self.engine.setProperty('voice', v.id)
                        break
            
            self.is_initialized = True
            logger.info("pyttsx3 TTS engine initialized successfully")
            
        except ImportError:
            logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            raise
    
    def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech using pyttsx3.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data as bytes
        """
        if not self.is_initialized:
            self.initialize()
        
        try:
            # Note: pyttsx3 doesn't directly return audio bytes
            # For now, we'll use a workaround by saving to a temporary file
            import tempfile
            import os
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Save speech to temporary file
                self.engine.save_to_file(text, temp_file_path)
                self.engine.runAndWait()
                
                # Read the audio file
                with open(temp_file_path, 'rb') as f:
                    audio_data = f.read()
                
                logger.debug(f"Synthesized {len(text)} characters to {len(audio_data)} bytes")
                return audio_data
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return b""
    
    def get_available_voices(self) -> List[str]:
        """
        Get list of available system voices.
        
        Returns:
            List of available voice names
        """
        try:
            if not self.engine:
                self.initialize()
            
            voices = self.engine.getProperty('voices')
            voice_names = [voice.name for voice in voices]
            
            # Add default option
            if "default" not in voice_names:
                voice_names.insert(0, "default")
            
            return voice_names
            
        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
            return ["default"]
    
    def set_voice(self, voice: str) -> None:
        """
        Set the voice to use for speech synthesis.
        
        Args:
            voice: Voice name to use
        """
        super().set_voice(voice)
        
        if self.engine and self.is_initialized:
            try:
                voices = self.engine.getProperty('voices')
                for v in voices:
                    if voice in v.name.lower():
                        self.engine.setProperty('voice', v.id)
                        logger.info(f"Voice set to: {v.name}")
                        break
            except Exception as e:
                logger.error(f"Failed to set voice: {e}")
    
    def set_speed(self, speed: float) -> None:
        """
        Set the speech rate.
        
        Args:
            speed: Speech rate (0.5 = slow, 1.0 = normal, 2.0 = fast)
        """
        super().set_speed(speed)
        
        if self.engine and self.is_initialized:
            try:
                # Convert speed to words per minute (pyttsx3 uses WPM)
                wpm = int(200 * speed)  # 200 WPM is normal speed
                self.engine.setProperty('rate', wpm)
                logger.info(f"Speed set to: {speed}x ({wpm} WPM)")
            except Exception as e:
                logger.error(f"Failed to set speed: {e}")
    
    def get_engine_info(self) -> dict:
        """
        Get detailed information about the pyttsx3 engine.
        
        Returns:
            Dictionary containing engine information
        """
        info = super().get_engine_info()
        info.update({
            "engine": "pyttsx3",
            "offline": True,
            "system_voices": True
        })
        return info
    
    def cleanup(self) -> None:
        """
        Clean up pyttsx3 resources.
        """
        if self.engine:
            try:
                self.engine.stop()
                del self.engine
                self.engine = None
            except Exception as e:
                logger.error(f"Error cleaning up pyttsx3: {e}")
        
        super().cleanup()
        logger.info("pyttsx3 resources cleaned up")
