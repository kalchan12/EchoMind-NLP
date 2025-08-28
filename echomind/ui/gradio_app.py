"""
Gradio User Interface for EchoMind-NLP
=====================================

This module provides the web-based user interface for the EchoMind-NLP assistant
using Gradio. It includes a modern chat interface with various controls and features.

Features:
- Clean, modern chat interface
- Conversation history management
- System status and statistics
- Settings panel
- Export/import functionality
- Responsive design
"""

import gradio as gr
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path

from echomind.core.orchestrator import AssistantOrchestrator
from echomind.config import settings, get_config_summary
from loguru import logger


def create_interface() -> gr.Blocks:
    """
    Create the main Gradio interface for EchoMind-NLP.
    
    Returns:
        gr.Blocks: Configured Gradio interface
    """
    # Initialize the assistant orchestrator
    orchestrator = AssistantOrchestrator()
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    .chat-container {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        background: #fafafa;
    }
    .status-panel {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .settings-panel {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
    }
    """
    
    with gr.Blocks(
        title="EchoMind-NLP Assistant",
        theme=gr.themes.Soft(),
        css=custom_css
    ) as demo:
        
        # Header with title and description
        with gr.Row():
            gr.Markdown("""
            # 🤖 EchoMind-NLP Assistant
            
            **Your intelligent voice and text assistant with conversation memory**
            
            ---
            """)
        
        # Main content area
        with gr.Row():
            # Left column: Chat interface
            with gr.Column(scale=3):
                # Status panel
                with gr.Group(elem_classes=["status-panel"]):
                    status_text = gr.Markdown("**Status:** Ready to chat")
                    stats_text = gr.Markdown("**Stats:** 0 turns, 0 in memory")
                
                # Chat interface
                with gr.Group(elem_classes=["chat-container"]):
                    chat = gr.Chatbot(
                        type="messages",
                        height=500,
                        show_label=False,
                        container=True,
                        bubble_full_width=False
                    )
                    
                    # Input area
                    with gr.Row():
                        textbox = gr.Textbox(
                            placeholder="Type your message here and press Enter...",
                            lines=2,
                            max_lines=4,
                            show_label=False,
                            container=False
                        )
                    
                    # Voice input area
                    with gr.Row():
                        audio_input = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            label="Voice Input",
                            show_label=False
                        )
                        voice_status = gr.Markdown("*Click microphone to record*")
                    
                    # Action buttons
                    with gr.Row():
                        send_btn = gr.Button("Send", variant="primary", size="sm")
                        clear_btn = gr.Button("Clear Chat", variant="secondary", size="sm")
                        export_btn = gr.Button("Export", variant="secondary", size="sm")
                        tts_btn = gr.Button("🔊 Speak Response", variant="secondary", size="sm")
            
            # Right column: Settings and info
            with gr.Column(scale=1):
                # Settings panel
                with gr.Group(elem_classes=["settings-panel"]):
                    gr.Markdown("### ⚙️ Settings")
                    
                    # Model settings
                    model_size = gr.Dropdown(
                        choices=["tiny", "base", "small", "medium", "large-v2"],
                        value=settings.whisper_model_size,
                        label="Whisper Model Size",
                        info="Larger models = better accuracy, slower speed"
                    )
                    
                    language = gr.Dropdown(
                        choices=["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                        value=settings.stt_language,
                        label="Language",
                        info="Preferred language for speech recognition"
                    )
                    
                    theme_selector = gr.Dropdown(
                        choices=["light", "dark", "auto"],
                        value=settings.theme,
                        label="Theme",
                        info="Interface theme preference"
                    )
                    
                    # Apply settings button
                    apply_settings_btn = gr.Button("Apply Settings", variant="primary", size="sm")
                
                # Quick actions panel
                with gr.Group(elem_classes=["settings-panel"]):
                    gr.Markdown("### 🚀 Quick Actions")
                    
                    help_btn = gr.Button("Help", variant="secondary", size="sm")
                    status_btn = gr.Button("System Status", variant="secondary", size="sm")
                    time_btn = gr.Button("Current Time", variant="secondary", size="sm")
                
                # Information panel
                with gr.Group(elem_classes=["settings-panel"]):
                    gr.Markdown("### ℹ️ Information")
                    
                    info_text = gr.Markdown(f"""
                    **Version:** 0.1.0
                    **Model:** {settings.whisper_model_size}
                    **Language:** {settings.stt_language}
                    **Memory:** {settings.max_conversation_turns} turns
                    
                    **Features:**
                    ✅ Text chat
                    ✅ Conversation memory
                    ✅ Command system
                    ✅ Voice input (STT)
                    ✅ Voice output (TTS)
                    """)
        
        # Event handlers
        def respond(message: str, history: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], str]:
            """
            Process user message and generate response.
            
            Args:
                message: User's input message
                history: Current chat history
            
            Returns:
                Tuple of (updated_history, empty_string)
            """
            if not message.strip():
                return history, ""
            
            try:
                # Generate response
                reply = orchestrator.handle_text(message)
                
                # Update history
                updated_history = history + [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": reply}
                ]
                
                # Update status
                stats = orchestrator.get_conversation_stats()
                stats_text.value = f"**Stats:** {stats['total_turns']} turns, {stats['memory_turns']} in memory"
                
                return updated_history, ""
                
            except Exception as e:
                logger.error(f"Error in respond function: {e}")
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                updated_history = history + [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": error_msg}
                ]
                return updated_history, ""
        
        def clear_chat() -> Tuple[List[Dict[str, str]], str]:
            """Clear the chat history."""
            result = orchestrator.clear_conversation()
            return [], result
        
        def export_conversation() -> str:
            """Export conversation to JSON file."""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            filepath = Path("exports") / filename
            
            # Create exports directory if it doesn't exist
            filepath.parent.mkdir(exist_ok=True)
            
            return orchestrator.export_conversation(str(filepath))
        
        def show_help() -> str:
            """Show help information."""
            return orchestrator.nlp.commands["help"]()
        
        def show_status() -> str:
            """Show system status."""
            return orchestrator.nlp.commands["status"]()
        
        def show_time() -> str:
            """Show current time."""
            return orchestrator.nlp.commands["time"]()
        
        def update_status() -> str:
            """Update status display."""
            stats = orchestrator.get_conversation_stats()
            speech_info = orchestrator.get_speech_info()
            speech_status = "✅" if speech_info["speech_enabled"] else "❌"
            return f"**Status:** Active | **Stats:** {stats['total_turns']} turns, {stats['memory_turns']} in memory | **Speech:** {speech_status}"
        
        def process_voice_input(audio_data) -> Tuple[List[Dict[str, str]], str, str]:
            """
            Process voice input and generate response.
            
            Args:
                audio_data: Audio data from microphone (filepath)
                
            Returns:
                Tuple of (updated_history, empty_string, status_message)
            """
            if audio_data is None:
                return [], "", "*No audio detected*"
            
            try:
                # Read audio file
                with open(audio_data, 'rb') as f:
                    audio_bytes = f.read()
                
                # Process voice input
                response = orchestrator.handle_voice_input(audio_bytes)
                
                # Update history
                updated_history = [
                    {"role": "user", "content": "[Voice Input]"},
                    {"role": "assistant", "content": response}
                ]
                
                return updated_history, "", f"*Processed voice input: {len(response)} chars*"
                
            except Exception as e:
                logger.error(f"Voice processing error: {e}")
                return [], "", f"*Voice processing error: {str(e)}*"
        
        def speak_response(text: str) -> str:
            """
            Convert text response to speech.
            
            Args:
                text: Text to speak
                
            Returns:
                Status message
            """
            if not text.strip():
                return "*No text to speak*"
            
            try:
                audio_data = orchestrator.synthesize_response(text)
                if audio_data:
                    return f"*Synthesized {len(text)} characters to speech*"
                else:
                    return "*Speech synthesis failed*"
                    
            except Exception as e:
                logger.error(f"Speech synthesis error: {e}")
                return f"*Speech synthesis error: {str(e)}*"
        
        # Bind event handlers
        textbox.submit(
            respond,
            inputs=[textbox, chat],
            outputs=[chat, textbox]
        )
        
        send_btn.click(
            respond,
            inputs=[textbox, chat],
            outputs=[chat, textbox]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chat]
        )
        
        export_btn.click(
            export_conversation,
            outputs=[status_text]
        )
        
        help_btn.click(
            show_help,
            outputs=[status_text]
        )
        
        status_btn.click(
            show_status,
            outputs=[status_text]
        )
        
        time_btn.click(
            show_time,
            outputs=[status_text]
        )
        
        # Voice input handler
        audio_input.change(
            process_voice_input,
            inputs=[audio_input],
            outputs=[chat, textbox, voice_status]
        )
        
        # TTS handler
        tts_btn.click(
            speak_response,
            inputs=[chat],  # Get the last response from chat
            outputs=[voice_status]
        )
        
        # Auto-refresh status every 30 seconds
        demo.load(update_status, outputs=[status_text])
    
    return demo


