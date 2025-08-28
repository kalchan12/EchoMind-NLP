"""
Conversation Memory Management
=============================

This module provides conversation memory functionality for the EchoMind-NLP assistant.
It maintains a rolling window of conversation turns to provide context for responses.

Features:
- Fixed-size conversation history (FIFO)
- Thread-safe operations
- Easy serialization/deserialization
- Context window management
"""

from collections import deque
from typing import Deque, List, Tuple, Optional, Dict, Any
from datetime import datetime
import json


class ConversationMemory:
    """
    Manages conversation history with a fixed-size rolling window.
    
    This class maintains a deque of conversation turns, automatically
    removing old entries when the maximum size is reached.
    
    Attributes:
        max_turns: Maximum number of conversation turns to remember
        _history: Internal deque storing (user_text, assistant_text) tuples
    """
    
    def __init__(self, max_turns: int = 20) -> None:
        """
        Initialize conversation memory.
        
        Args:
            max_turns: Maximum number of conversation turns to remember.
                      Older turns are automatically removed when exceeded.
        """
        self.max_turns = max_turns
        self._history: Deque[Tuple[str, str]] = deque(maxlen=max_turns)
        self._created_at = datetime.now()
    
    def add_turn(self, user_text: str, assistant_text: str) -> None:
        """
        Add a new conversation turn to memory.
        
        Args:
            user_text: The user's input text
            assistant_text: The assistant's response text
        """
        if not user_text.strip() or not assistant_text.strip():
            return  # Skip empty turns
        
        self._history.append((user_text.strip(), assistant_text.strip()))
    
    def as_list(self) -> List[Tuple[str, str]]:
        """
        Get conversation history as a list.
        
        Returns:
            List of (user_text, assistant_text) tuples
        """
        return list(self._history)
    
    def get_context(self, max_turns: Optional[int] = None) -> str:
        """
        Get conversation context as a formatted string.
        
        Args:
            max_turns: Maximum turns to include in context (defaults to all)
        
        Returns:
            Formatted conversation context string
        """
        if not self._history:
            return ""
        
        turns = self.as_list()
        if max_turns:
            turns = turns[-max_turns:]
        
        context_parts = []
        for i, (user, assistant) in enumerate(turns, 1):
            context_parts.append(f"Turn {i}:")
            context_parts.append(f"User: {user}")
            context_parts.append(f"Assistant: {assistant}")
            context_parts.append("")
        
        return "\n".join(context_parts).strip()
    
    def get_recent_context(self, turns: int = 3) -> str:
        """
        Get recent conversation context for immediate reference.
        
        Args:
            turns: Number of recent turns to include
        
        Returns:
            Recent conversation context
        """
        return self.get_context(max_turns=turns)
    
    def clear(self) -> None:
        """Clear all conversation history."""
        self._history.clear()
    
    def is_empty(self) -> bool:
        """
        Check if conversation memory is empty.
        
        Returns:
            True if no conversation turns are stored
        """
        return len(self._history) == 0
    
    def count(self) -> int:
        """
        Get the number of conversation turns stored.
        
        Returns:
            Number of turns in memory
        """
        return len(self._history)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert conversation memory to dictionary for serialization.
        
        Returns:
            Dictionary representation of the conversation memory
        """
        return {
            "max_turns": self.max_turns,
            "turns": self.as_list(),
            "count": self.count(),
            "created_at": self._created_at.isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load conversation memory from dictionary.
        
        Args:
            data: Dictionary containing conversation memory data
        """
        self.max_turns = data.get("max_turns", 20)
        self._history = deque(data.get("turns", []), maxlen=self.max_turns)
        self._created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save conversation memory to JSON file.
        
        Args:
            filepath: Path to save the conversation memory
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load conversation memory from JSON file.
        
        Args:
            filepath: Path to load the conversation memory from
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.from_dict(data)


