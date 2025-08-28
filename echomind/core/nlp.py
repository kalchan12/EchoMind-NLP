from typing import Dict


class NLPProcessor:
    """Minimal text processor with simple echo/command handling.

    Replace this with spaCy/Transformers or API-backed models later.
    """

    def generate(self, prompt: str, context: str | None = None) -> str:
        cleaned = prompt.strip()
        if not cleaned:
            return "Say something to begin."
        # Simple command: /help
        if cleaned.lower() in {"/help", "help"}:
            return "I'm EchoMind. Ask me anything or click the mic to speak."
        # Echo with a tiny bit of formatting
        reply = f"You said: {cleaned}"
        if context:
            reply += "\n(Recent context available)"
        return reply

    def analyze(self, text: str) -> Dict[str, str]:
        return {"length": str(len(text.strip())), "lower": text.lower()}


