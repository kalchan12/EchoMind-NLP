"""
Speech-to-Text Base Interface
============================

This module defines the base interface for speech-to-text processing.
All STT implementations should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
import numpy as np


class STTProcessor(ABC):
    """
    Base class for speech-to-text processors.
    
    This abstract class defines the interface that all STT implementations
    must follow. It provides a consistent API for different STT engines.
    """
    
    def __init__(self, model_size: str = "small", language: str = "en") -> None:
        """
        Initialize the STT processor.
        
        Args:
            model_size: Size of the model to use (tiny, base, small, medium, large-v2)
            language: Language code for speech recognition
        """
        self.model_size = model_size
        self.language = language
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the STT model and resources.
        
        This method should load the model and prepare it for inference.
        """
        pass
    
    @abstractmethod
    def transcribe(self, audio_data: Union[bytes, np.ndarray, str]) -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Audio data in bytes, numpy array, or file path
            
        Returns:
            Transcribed text
        """
        pass
    
    @abstractmethod
    def transcribe_streaming(self, audio_chunk: bytes) -> Optional[str]:
        """
        Transcribe audio chunk for streaming applications.
        
        Args:
            audio_chunk: Audio data chunk
            
        Returns:
            Partial transcription or None if not enough data
        """
        pass
    
    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported language codes.
        
        Returns:
            List of supported language codes
        """
        return ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model_size": self.model_size,
            "language": self.language,
            "is_initialized": self.is_initialized,
            "supported_languages": self.get_supported_languages()
        }
    
    def cleanup(self) -> None:
        """
        Clean up resources and free memory.
        
        This method should be called when the processor is no longer needed.
        """
        self.is_initialized = False
