from collections import deque
from typing import Deque, List, Tuple


class ConversationMemory:
    def __init__(self, max_turns: int = 20) -> None:
        self._history: Deque[Tuple[str, str]] = deque(maxlen=max_turns)

    def add_turn(self, user_text: str, assistant_text: str) -> None:
        self._history.append((user_text, assistant_text))

    def as_list(self) -> List[Tuple[str, str]]:
        return list(self._history)

    def clear(self) -> None:
        self._history.clear()


