#!/usr/bin/env python3
"""
EchoMind-NLP: Voice and Text Assistant
=====================================

Main entry point for the EchoMind-NLP application.
This module initializes the environment and launches the Gradio interface.

Features:
- Text-based chat interface
- Voice input/output (when dependencies are available)
- Conversation memory
- Configurable settings via environment variables

Usage:
    python app.py

Environment Variables:
    OPENAI_API_KEY: Optional OpenAI API key for enhanced responses
    ELEVENLABS_API_KEY: Optional ElevenLabs API key for high-quality TTS
    WHISPER_MODEL_SIZE: Whisper model size (tiny/base/small/medium/large-v2)
    STT_LANGUAGE: Preferred language for speech recognition
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from echomind.ui.gradio_app import create_interface
from echomind.config import settings
from loguru import logger


def setup_logging() -> None:
    """Configure logging for the application."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/echomind.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )


def main() -> None:
    """
    Main application entry point.
    
    Initializes the environment, sets up logging, and launches the Gradio interface.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    logger.info("Starting EchoMind-NLP application")
    logger.info(f"Configuration: Whisper={settings.whisper_model_size}, Language={settings.stt_language}")
    
    try:
        # Create and launch the Gradio interface
        iface = create_interface()
        
        # Launch with clean configuration
        iface.launch(
            server_name="127.0.0.1",
            server_port=7862,  # Changed port to avoid conflicts
            share=False,  # Set to True for public sharing
            debug=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


