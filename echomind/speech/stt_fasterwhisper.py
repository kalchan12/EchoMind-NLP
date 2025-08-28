"""
Faster-Whisper Speech-to-Text Implementation
===========================================

This module provides speech-to-text functionality using Faster-Whisper,
which is an optimized implementation of OpenAI's Whisper model.
"""

import io
import tempfile
from typing import Optional, Union
import numpy as np
from loguru import logger

from .stt_base import STTProcessor


class FasterWhisperSTT(STTProcessor):
    """
    Faster-Whisper implementation of speech-to-text processing.
    
    This class provides fast and efficient speech recognition using
    the Faster-Whisper library, which is an optimized version of
    OpenAI's Whisper model.
    """
    
    def __init__(self, model_size: str = "small", language: str = "en") -> None:
        """
        Initialize the Faster-Whisper STT processor.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v2)
            language: Language code for speech recognition
        """
        super().__init__(model_size, language)
        self.model = None
        self.transcriber = None
        
    def initialize(self) -> None:
        """
        Initialize the Faster-Whisper model.
        
        Loads the specified model and prepares it for transcription.
        """
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"Loading Faster-Whisper model: {self.model_size}")
            
            # Load the model with CPU inference (can be changed to GPU)
            self.model = WhisperModel(
                self.model_size,
                device="cpu",  # Use "cuda" for GPU
                compute_type="int8"  # Use "float16" for better accuracy
            )
            
            self.is_initialized = True
            logger.info("Faster-Whisper model loaded successfully")
            
        except ImportError:
            logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Faster-Whisper: {e}")
            raise
    
    def transcribe(self, audio_data: Union[bytes, np.ndarray, str]) -> str:
        """
        Transcribe audio data to text using Faster-Whisper.
        
        Args:
            audio_data: Audio data in bytes, numpy array, or file path
            
        Returns:
            Transcribed text
        """
        if not self.is_initialized:
            self.initialize()
        
        try:
            # Handle different input types
            if isinstance(audio_data, str):
                # File path
                segments, _ = self.model.transcribe(
                    audio_data,
                    language=self.language if self.language != "auto" else None,
                    beam_size=5
                )
            elif isinstance(audio_data, bytes):
                # Audio bytes - save to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file.write(audio_data)
                    temp_file_path = temp_file.name
                
                try:
                    segments, _ = self.model.transcribe(
                        temp_file_path,
                        language=self.language if self.language != "auto" else None,
                        beam_size=5
                    )
                finally:
                    # Clean up temporary file
                    import os
                    os.unlink(temp_file_path)
            elif isinstance(audio_data, np.ndarray):
                # Numpy array - save to temporary file
                import soundfile as sf
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    sf.write(temp_file.name, audio_data, 16000)
                    temp_file_path = temp_file.name
                
                try:
                    segments, _ = self.model.transcribe(
                        temp_file_path,
                        language=self.language if self.language != "auto" else None,
                        beam_size=5
                    )
                finally:
                    # Clean up temporary file
                    import os
                    os.unlink(temp_file_path)
            else:
                raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
            
            # Combine all segments into a single text
            transcribed_text = " ".join([segment.text for segment in segments])
            
            logger.debug(f"Transcribed {len(transcribed_text)} characters")
            return transcribed_text.strip()
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
    
    def transcribe_streaming(self, audio_chunk: bytes) -> Optional[str]:
        """
        Transcribe audio chunk for streaming applications.
        
        Note: Faster-Whisper doesn't support true streaming, so this
        is a simplified implementation that processes chunks.
        
        Args:
            audio_chunk: Audio data chunk
            
        Returns:
            Partial transcription or None if not enough data
        """
        # For now, return None as streaming requires more complex implementation
        # This could be enhanced with a buffer-based approach
        return None
    
    def get_model_info(self) -> dict:
        """
        Get detailed information about the Faster-Whisper model.
        
        Returns:
            Dictionary containing model information
        """
        info = super().get_model_info()
        info.update({
            "engine": "faster-whisper",
            "device": "cpu",  # or "cuda" if using GPU
            "compute_type": "int8",
            "supports_streaming": False
        })
        return info
    
    def cleanup(self) -> None:
        """
        Clean up Faster-Whisper resources.
        """
        if self.model:
            del self.model
            self.model = None
        super().cleanup()
        logger.info("Faster-Whisper resources cleaned up")
