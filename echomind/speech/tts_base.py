"""
Text-to-Speech Base Interface
============================

This module defines the base interface for text-to-speech processing.
All TTS implementations should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
import io


class TTSProcessor(ABC):
    """
    Base class for text-to-speech processors.
    
    This abstract class defines the interface that all TTS implementations
    must follow. It provides a consistent API for different TTS engines.
    """
    
    def __init__(self, voice: str = "default", speed: float = 1.0) -> None:
        """
        Initialize the TTS processor.
        
        Args:
            voice: Voice to use for speech synthesis
            speed: Speech rate (1.0 = normal speed)
        """
        self.voice = voice
        self.speed = speed
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the TTS engine and resources.
        
        This method should load the voice and prepare it for synthesis.
        """
        pass
    
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio data as bytes
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> list[str]:
        """
        Get list of available voices.
        
        Returns:
            List of available voice names
        """
        pass
    
    def set_voice(self, voice: str) -> None:
        """
        Set the voice to use for speech synthesis.
        
        Args:
            voice: Voice name to use
        """
        if voice in self.get_available_voices():
            self.voice = voice
        else:
            raise ValueError(f"Voice '{voice}' not available. Available voices: {self.get_available_voices()}")
    
    def set_speed(self, speed: float) -> None:
        """
        Set the speech rate.
        
        Args:
            speed: Speech rate (0.5 = slow, 1.0 = normal, 2.0 = fast)
        """
        if 0.1 <= speed <= 3.0:
            self.speed = speed
        else:
            raise ValueError("Speed must be between 0.1 and 3.0")
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the TTS engine.
        
        Returns:
            Dictionary containing engine information
        """
        return {
            "voice": self.voice,
            "speed": self.speed,
            "is_initialized": self.is_initialized,
            "available_voices": self.get_available_voices()
        }
    
    def cleanup(self) -> None:
        """
        Clean up resources and free memory.
        
        This method should be called when the processor is no longer needed.
        """
        self.is_initialized = False
