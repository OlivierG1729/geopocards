
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Flashcard:
    id: str
    question: str
    answer: str
    created_at: Optional[datetime] = None


@dataclass
class FlashcardStats:
    flashcard_id: str
    times_seen: int
    times_correct: int
    last_seen: Optional[datetime] = None
