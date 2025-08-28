import gradio as gr

from echomind.core.orchestrator import AssistantOrchestrator


def create_interface() -> gr.Blocks:
    orchestrator = AssistantOrchestrator()

    with gr.Blocks(title="EchoMind-NLP") as demo:
        gr.Markdown("## EchoMind-NLP — simple text + voice assistant (text-only starter)")

        chat = gr.Chatbot(type="messages", height=450)
        textbox = gr.Textbox(placeholder="Type a message and press Enter", lines=2)
        clear_btn = gr.Button("Clear")

        def respond(message: str, history: list[dict]) -> tuple[list[dict], str]:
            reply = orchestrator.handle_text(message)
            updated = history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": reply},
            ]
            return updated, ""

        textbox.submit(respond, [textbox, chat], [chat, textbox])
        clear_btn.click(lambda: ([], orchestrator.clear()), outputs=[chat])

    return demo


