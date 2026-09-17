"""Labelling with Claude in the chat app (no API).

split: data/messages.jsonl -> data/label_batches/batch_NNN.jsonl (~150 messages each, gold test ids excluded)
merge: data/label_batches/batch_NNN.labels.jsonl -> validate -> data/labels_silver.jsonl (section 6.2)

Owner: Person B. See MAPENS_CONTEXT.md.
Run: python scripts/label_batches.py split | merge
"""


def split() -> None:
    raise NotImplementedError


def merge() -> None:
    """Check every id exists, label is one of LABELS, and text[start:end] == location text."""
    raise NotImplementedError


if __name__ == "__main__":
    import sys

    {"split": split, "merge": merge}[sys.argv[1]]()
