"""
Speech Processing Package
========================

This package contains modules for speech-to-text (STT) and text-to-speech (TTS) functionality.

Modules:
- stt_base: Base interface for speech-to-text
- stt_fasterwhisper: Faster-Whisper implementation
- tts_base: Base interface for text-to-speech  
- tts_pyttsx3: pyttsx3 implementation
- tts_elevenlabs: ElevenLabs implementation
- audio_utils: Audio processing utilities
"""

from .stt_base import STTProcessor
from .stt_fasterwhisper import FasterWhisperSTT
from .tts_base import TTSProcessor
from .tts_pyttsx3 import Pyttsx3TTS
from .audio_utils import AudioUtils

__all__ = [
    "STTProcessor",
    "FasterWhisperSTT", 
    "TTSProcessor",
    "Pyttsx3TTS",
    "AudioUtils",
]
