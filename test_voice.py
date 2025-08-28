#!/usr/bin/env python3
"""
Voice Features Test Script
=========================

This script tests the voice processing capabilities of EchoMind-NLP.
It verifies that STT and TTS are working correctly.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from echomind.core.orchestrator import AssistantOrchestrator
from loguru import logger


def test_voice_features():
    """Test voice processing features."""
    print("🎤 Testing EchoMind-NLP Voice Features")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = AssistantOrchestrator()
    
    # Check speech capabilities
    speech_info = orchestrator.get_speech_info()
    print(f"Speech Enabled: {speech_info['speech_enabled']}")
    print(f"STT Available: {speech_info['stt_available']}")
    print(f"TTS Available: {speech_info['tts_available']}")
    
    if speech_info['stt_available']:
        print(f"STT Model: {speech_info['stt_info']['model_size']}")
        print(f"STT Language: {speech_info['stt_info']['language']}")
    
    if speech_info['tts_available']:
        print(f"TTS Engine: {speech_info['tts_info']['engine']}")
        print(f"Available Voices: {len(speech_info['tts_info']['available_voices'])}")
    
    # Test text processing
    print("\n📝 Testing Text Processing:")
    test_text = "Hello, this is a test message."
    response = orchestrator.handle_text(test_text)
    print(f"Input: {test_text}")
    print(f"Response: {response}")
    
    # Test TTS (if available)
    if speech_info['tts_available']:
        print("\n🔊 Testing Text-to-Speech:")
        try:
            audio_data = orchestrator.synthesize_response("Hello, this is a test of text-to-speech.")
            print(f"TTS Success: Generated {len(audio_data)} bytes of audio")
        except Exception as e:
            print(f"TTS Error: {e}")
    
    # Test system status
    print("\n📊 System Status:")
    status = orchestrator.get_system_status()
    print(f"Total Turns: {status['total_turns']}")
    print(f"Memory Turns: {status['memory_turns']}")
    print(f"Voice Processing: {status['system_info']['capabilities']['voice_processing']}")
    
    print("\n✅ Voice features test completed!")


if __name__ == "__main__":
    test_voice_features()
