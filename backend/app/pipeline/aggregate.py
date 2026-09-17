"""Stage 4 - merge reports into events, handle "clear", TTL. Owner: Person A.
See MAPENS_CONTEXT.md section 7.
"""
from typing import Optional

from app.pipeline.types import Event, Label, Message, Resolved


def aggregate(label: Label, resolved: Resolved, msg: Message, now_ts: int) -> Optional[Event]:
    raise NotImplementedError
