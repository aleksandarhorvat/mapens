# MapeNS - traffic events on the map

Reads informal Serbian Viber messages about patrols, accidents and traffic jams in Novi Sad,
classifies them, extracts and geo-resolves locations, and shows them as fading pins on a map.

Stack: transformers (BERTić, Embedić), PyLucene, FastAPI, React + Leaflet, Docker Compose.
Full design, contracts and work split: [MAPENS_CONTEXT.md](MAPENS_CONTEXT.md). Progress: [PROGRESS.md](PROGRESS.md).

## Run

```bash
git clone <repo-url> && cd mapens
cp .env.example .env        # set CLASSIFIER_REPO
docker compose up --build
```

- Map UI: http://localhost:5173
- API docs: http://localhost:8000/docs

First start downloads models (~2-3 GB) and builds indexes; later starts are fast.
Generated files (Lucene indexes, vectors, sqlite, model weights) are never committed -
`scripts/setup.sh` rebuilds them.

## Local development (without Docker)

```bash
# frontend
cd frontend && npm install && npm run dev      # proxies /api -> http://localhost:8000

# backend (PyLucene is easiest inside Docker; run only the backend container)
docker compose up --build backend
```

## Before committing

```bash
python scripts/check_style.py
```

Checks the writing style rules from MAPENS_CONTEXT.md section 14 (no em dashes, emoji or other non-ASCII symbols except Serbian letters).

## Repository layout

```
data/        committed: messages.jsonl, gazetteer.json, aliases.json, labels; raw/ and derived files ignored
models/      fine-tuned classifier (downloaded from Hugging Face, ignored)
scripts/     offline scripts: export, labelling, gazetteer, indexing, eval, setup.sh
backend/     FastAPI app + NLP/IR pipeline
frontend/    React + Leaflet UI
```

## Owners

- Person A - IR / backend / Docker
- Person B - NLP / data / frontend
