"""Stage 2 — location extraction: bcms-bertic-ner ∪ gazetteer/alias matcher + merge rule.
Owner: Person B. See MAPENS_CONTEXT.md §7.
"""
from app.pipeline.types import Mention


def extract(text: str, text_norm: str) -> list[Mention]:
    raise NotImplementedError


if __name__ == "__main__":
    t = "Patrola kod Merkatora na Bulevaru"
    print(extract(t, t.lower()))
