"""Paths and tunable parameters. Owner: Person A (both may add values)."""
import os
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
MODELS_DIR = Path(os.getenv("MODELS_DIR", "models"))

MESSAGES_JSONL = DATA_DIR / "messages.jsonl"
MESSAGES_SQLITE = DATA_DIR / "messages.sqlite"
GAZETTEER_JSON = DATA_DIR / "gazetteer.json"
ALIASES_JSON = DATA_DIR / "aliases.json"
GAZETTEER_VECTORS = DATA_DIR / "gazetteer_vectors.npy"
LUCENE_DIR = DATA_DIR / "lucene"

# Models
CLASSIFIER_DIR = MODELS_DIR / "classifier"
CLASSIFIER_REPO = os.getenv("CLASSIFIER_REPO", "")
NER_MODEL = "classla/bcms-bertic-ner"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "djovak/embedic-large")

# Novi Sad bounding box (south, west, north, east)
NOVI_SAD_BBOX = (45.20, 19.72, 45.32, 19.95)

# Stage 3 — geo-resolution
RETRIEVAL_K = 10
RRF_K = 60
GEO_CONFIDENCE_THRESHOLD = 0.35   # tune on gold_test.jsonl
PAIR_MAX_DISTANCE_M = 800

# Stage 4 — aggregation
MERGE_DISTANCE_M = 300
MERGE_WINDOW_MIN = 20
CLEAR_DISTANCE_M = 500
CLEAR_WINDOW_MIN = 90
TTL_MIN = {"jam": 30, "patrol": 60, "accident": 90}

# Replay
DEFAULT_REPLAY_SPEED = 60
