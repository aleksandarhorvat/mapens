"""Stage 1 — message classifier (fine-tuned classla/bcms-bertic). Owner: Person B.

Temporary mock for Person A: keyword rules until models/classifier exists.
"""
from app.pipeline.types import Label


def classify(text: str) -> tuple[Label, float]:
    """Return (label, probability)."""
    raise NotImplementedError


if __name__ == "__main__":
    for t in ["patrola kod merkatora na bulevaru", "cisto na limanu", "dobro jutro svima"]:
        print(t, "→", classify(t))
