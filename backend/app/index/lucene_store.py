"""Lucene indexes for events and messages. Owner: Person A.

Field design: MAPENS_CONTEXT.md §7 ("Lucene indexes").
Check `lucene.VERSION` inside the container before writing API calls.
"""
from typing import Optional

from app.pipeline.types import Event, Message


class LuceneStore:
    def __init__(self, index_dir: str):
        raise NotImplementedError

    # events
    def upsert_event(self, event: Event) -> None:
        raise NotImplementedError

    def get_event(self, event_id: str) -> Optional[Event]:
        raise NotImplementedError

    def query_events(self, bbox=None, since: Optional[int] = None,
                     types: Optional[list[str]] = None, status: str = "active") -> list[Event]:
        raise NotImplementedError

    # messages
    def add_message(self, msg: Message, label: str, prob: float,
                    resolved: bool, event_id: Optional[str]) -> None:
        raise NotImplementedError

    def search_messages(self, q: str, limit: int = 20) -> list[dict]:
        raise NotImplementedError

    def unresolved_messages(self, limit: int = 50) -> list[dict]:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError
