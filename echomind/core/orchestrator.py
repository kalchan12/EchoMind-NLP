from echomind.core.memory import ConversationMemory
from echomind.core.nlp import NLPProcessor


class AssistantOrchestrator:
    def __init__(self) -> None:
        self.memory = ConversationMemory(max_turns=20)
        self.nlp = NLPProcessor()

    def handle_text(self, user_text: str) -> str:
        context = None
        if self.memory.as_list():
            last_user, last_bot = self.memory.as_list()[-1]
            context = f"{last_user}\n{last_bot}"
        reply = self.nlp.generate(user_text, context=context)
        self.memory.add_turn(user_text, reply)
        return reply

    def clear(self) -> None:
        self.memory.clear()


