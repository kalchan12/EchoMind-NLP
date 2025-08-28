"""
Audio Utilities
==============

This module provides utility functions for audio processing,
format conversion, and audio data manipulation.
"""

import io
import tempfile
import wave
from typing import Union, Tuple, Optional
import numpy as np
from loguru import logger

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    logger.warning("soundfile not available. Install with: pip install soundfile")

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub not available. Install with: pip install pydub")


class AudioUtils:
    """
    Utility class for audio processing operations.
    
    This class provides methods for audio format conversion,
    resampling, and audio data manipulation.
    """
    
    @staticmethod
    def bytes_to_numpy(audio_bytes: bytes, sample_rate: int = 16000) -> np.ndarray:
        """
        Convert audio bytes to numpy array.
        
        Args:
            audio_bytes: Audio data as bytes
            sample_rate: Expected sample rate
            
        Returns:
            Audio data as numpy array
        """
        try:
            if SOUNDFILE_AVAILABLE:
                # Use soundfile for better format support
                with io.BytesIO(audio_bytes) as audio_io:
                    data, sr = sf.read(audio_io)
                    if sr != sample_rate:
                        data = AudioUtils.resample_audio(data, sr, sample_rate)
                    return data
            else:
                # Fallback to wave module for WAV files
                with io.BytesIO(audio_bytes) as audio_io:
                    with wave.open(audio_io, 'rb') as wav_file:
                        frames = wav_file.readframes(wav_file.getnframes())
                        data = np.frombuffer(frames, dtype=np.int16)
                        data = data.astype(np.float32) / 32768.0
                        return data
                        
        except Exception as e:
            logger.error(f"Failed to convert audio bytes to numpy: {e}")
            return np.array([])
    
    @staticmethod
    def numpy_to_bytes(audio_array: np.ndarray, sample_rate: int = 16000) -> bytes:
        """
        Convert numpy array to audio bytes.
        
        Args:
            audio_array: Audio data as numpy array
            sample_rate: Sample rate of the audio
            
        Returns:
            Audio data as bytes
        """
        try:
            if SOUNDFILE_AVAILABLE:
                # Use soundfile for better format support
                with io.BytesIO() as audio_io:
                    sf.write(audio_io, audio_array, sample_rate, format='WAV')
                    return audio_io.getvalue()
            else:
                # Fallback to wave module
                with io.BytesIO() as audio_io:
                    with wave.open(audio_io, 'wb') as wav_file:
                        wav_file.setnchannels(1)  # Mono
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(sample_rate)
                        
                        # Convert to int16
                        audio_int16 = (audio_array * 32767).astype(np.int16)
                        wav_file.writeframes(audio_int16.tobytes())
                    
                    return audio_io.getvalue()
                    
        except Exception as e:
            logger.error(f"Failed to convert numpy to audio bytes: {e}")
            return b""
    
    @staticmethod
    def resample_audio(audio_data: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
        """
        Resample audio to a different sample rate.
        
        Args:
            audio_data: Audio data as numpy array
            original_rate: Original sample rate
            target_rate: Target sample rate
            
        Returns:
            Resampled audio data
        """
        if original_rate == target_rate:
            return audio_data
        
        try:
            if PYDUB_AVAILABLE:
                # Use pydub for resampling
                # Convert numpy to audio segment
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    sf.write(temp_file.name, audio_data, original_rate)
                    temp_file_path = temp_file.name
                
                try:
                    # Load with pydub and resample
                    audio_segment = AudioSegment.from_wav(temp_file_path)
                    resampled = audio_segment.set_frame_rate(target_rate)
                    
                    # Convert back to numpy
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file2:
                        resampled.export(temp_file2.name, format="wav")
                        temp_file2_path = temp_file2.name
                    
                    try:
                        data, _ = sf.read(temp_file2_path)
                        return data
                    finally:
                        import os
                        os.unlink(temp_file2_path)
                        
                finally:
                    import os
                    os.unlink(temp_file_path)
            else:
                # Simple resampling (not as accurate)
                ratio = target_rate / original_rate
                new_length = int(len(audio_data) * ratio)
                indices = np.linspace(0, len(audio_data) - 1, new_length)
                return np.interp(indices, np.arange(len(audio_data)), audio_data)
                
        except Exception as e:
            logger.error(f"Failed to resample audio: {e}")
            return audio_data
    
    @staticmethod
    def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio to prevent clipping.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Normalized audio data
        """
        if len(audio_data) == 0:
            return audio_data
        
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val * 0.95  # Leave some headroom
        return audio_data
    
    @staticmethod
    def trim_silence(audio_data: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """
        Remove silence from the beginning and end of audio.
        
        Args:
            audio_data: Audio data as numpy array
            threshold: Silence threshold
            
        Returns:
            Audio data with silence trimmed
        """
        if len(audio_data) == 0:
            return audio_data
        
        # Find non-silent regions
        energy = np.abs(audio_data)
        silent = energy < threshold
        
        # Find start and end
        start = 0
        end = len(audio_data)
        
        for i in range(len(silent)):
            if not silent[i]:
                start = i
                break
        
        for i in range(len(silent) - 1, -1, -1):
            if not silent[i]:
                end = i + 1
                break
        
        return audio_data[start:end]
    
    @staticmethod
    def get_audio_info(audio_data: Union[bytes, np.ndarray]) -> dict:
        """
        Get information about audio data.
        
        Args:
            audio_data: Audio data as bytes or numpy array
            
        Returns:
            Dictionary containing audio information
        """
        info = {
            "type": type(audio_data).__name__,
            "length_bytes": 0,
            "length_samples": 0,
            "duration_seconds": 0,
            "sample_rate": 16000,
            "channels": 1,
            "format": "unknown"
        }
        
        try:
            if isinstance(audio_data, bytes):
                info["length_bytes"] = len(audio_data)
                
                # Try to get info from WAV header
                if len(audio_data) >= 44:  # Minimum WAV header size
                    with io.BytesIO(audio_data) as audio_io:
                        try:
                            with wave.open(audio_io, 'rb') as wav_file:
                                info["sample_rate"] = wav_file.getframerate()
                                info["channels"] = wav_file.getnchannels()
                                info["length_samples"] = wav_file.getnframes()
                                info["duration_seconds"] = wav_file.getnframes() / wav_file.getframerate()
                                info["format"] = "WAV"
                        except:
                            pass
                            
            elif isinstance(audio_data, np.ndarray):
                info["length_samples"] = len(audio_data)
                info["duration_seconds"] = len(audio_data) / info["sample_rate"]
                info["format"] = "numpy"
                
        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
        
        return info
    
    @staticmethod
    def validate_audio_format(audio_data: bytes) -> bool:
        """
        Validate if audio data is in a supported format.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            True if format is supported, False otherwise
        """
        if len(audio_data) < 12:
            return False
        
        # Check for WAV format
        if audio_data[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
            return True
        
        # Check for other formats (can be extended)
        # MP3, OGG, etc.
        
        return False
