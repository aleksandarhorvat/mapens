"""Stage 0 - normalization. Owner: Person B. See MAPENS_CONTEXT.md section 7."""


def clean(text: str) -> str:
    """Remove emoji/URLs, collapse whitespace. Keeps case and diacritics (for models)."""
    raise NotImplementedError


def normalize(text: str) -> str:
    """Lowercase, strip diacritics (č->c ć->c š->s ž->z đ->dj), collapse spaces (for matching)."""
    raise NotImplementedError


if __name__ == "__main__":
    for t in ["Gužva na mostu, stoji sve do Spensa !!", "PATROLA kod Merkatora https://x.y"]:
        print(clean(t), "|", normalize(t))
