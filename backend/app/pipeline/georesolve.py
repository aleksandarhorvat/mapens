"""Stage 3 - hybrid retrieval (Lucene BM25 + Embedić), RRF, spatial disambiguation.
Owner: Person A. See MAPENS_CONTEXT.md section 7.
"""
from app.pipeline.types import Candidate, Mention, Resolved


def retrieve(mention: Mention, k: int = 10) -> list[Candidate]:
    raise NotImplementedError


def georesolve(mentions: list[Mention]) -> Resolved | None:
    raise NotImplementedError


if __name__ == "__main__":
    m = Mention(text="merkatora na bulevaru", start=0, end=21, source="merged")
    print(retrieve(m))
