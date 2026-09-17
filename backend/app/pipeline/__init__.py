"""Pipeline entry point. Owner: Person A.

process() runs stages 0->4, stores results in Lucene and returns a debug trace:
{"label", "prob", "mentions", "candidates", "resolved", "event_id"}
"""
from app.pipeline.types import Message


def process(msg: Message, now_ts: int) -> dict:
    raise NotImplementedError
