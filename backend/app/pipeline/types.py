"""Shared pipeline types. Owners: Person A + B. Contract: MAPENS_CONTEXT.md section 6.4.
Do not change without telling the other person and updating the context file.
"""
from dataclasses import dataclass, field
from typing import Literal, Optional

Label = Literal["noise", "patrol", "accident", "jam", "clear"]
LABELS: list[str] = ["noise", "patrol", "accident", "jam", "clear"]


@dataclass
class Message:
    id: int
    ts: int            # epoch ms
    text: str
    text_norm: str


@dataclass
class Mention:
    text: str
    start: int
    end: int
    source: Literal["ner", "dict", "merged"]


@dataclass
class Candidate:
    gaz_id: str
    name: str
    kind: str
    lat: float
    lon: float
    score: float                     # fused score
    bm25_rank: Optional[int] = None
    dense_rank: Optional[int] = None


@dataclass
class Resolved:
    mentions: list[Mention]
    candidate: Optional[Candidate]   # None -> unresolved
    lat: Optional[float]
    lon: Optional[float]
    confidence: float
    precision: Literal["point", "intersection", "street", "none"]


@dataclass
class Event:
    id: str
    type: Label                      # never "noise"/"clear"
    lat: float
    lon: float
    first_ts: int
    last_ts: int
    report_count: int
    status: Literal["active", "cleared", "expired"]
    ttl_min: int
    message_ids: list[int] = field(default_factory=list)
    location_name: str = ""
