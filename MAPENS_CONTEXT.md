# MapeNS - Project Context for AI Coding Assistants

> How to use this file
> Paste this whole file at the start of a conversation with your LLM (or save it as `CLAUDE.md` / `AGENTS.md` / `.cursorrules` in the repo root). Then fill in and send the Session start block from section 12.
>
> Instructions for the assistant reading this: You are helping ONE of two students build this project. The user will tell you whether they are Person A or Person B and what has already been done. Focus on that person's tasks, but know the whole system so your code fits the other person's work. Follow the rules in section 11.

---

## 1. Project in one paragraph

MapeNS shows traffic events in Novi Sad (Serbia) - police patrols, accidents, traffic jams - as pins on a map. The information comes from informal Serbian messages in Viber groups. We do not read Viber live: we have a SQLite database (`viber.db`) of real messages and replay it on a simulated clock so the demo looks live. Each message goes through an NLP + IR pipeline: classify the message -> extract location mentions -> resolve them to coordinates using an OpenStreetMap gazetteer -> merge duplicate reports into events -> store in Lucene -> show on a React + Leaflet map where pins fade as they age.

Two-person university project for a course in Information Retrieval + Natural Language Processing. Timeline: one week. Both students use LLMs to generate most code; they must understand and be able to explain it.

## 2. Course requirements (hard constraints)

- Must be based on Lucene and/or the Hugging Face transformers ecosystem (we use both).
- Main logic packaged as a web service backend -> FastAPI (Python).
- A web UI that exposes the functionality -> React (Vite) + Leaflet. Appearance is secondary.
- Everything runs with Docker Compose so someone else can start it with minimal effort (`docker compose up`).
- Focus of grading is the backend functionality, plus we will report evaluation metrics.

## 3. Language and data realities (why this is hard)

Viber messages are informal Serbian (Latin script mostly), e.g.:

- `patrola kod merkatora na bulevaru`
- `Gužva na mostu, stoji sve do Spensa`
- `cisto na limanu` (= "clear on Liman", no diacritics)
- `udes futoška ugao sa bulevarom, čuvajte se`

Implications:

- Often lowercase and without diacritics (č ć š ž đ -> c c s z dj). NER models rely on capitals; embedding models get worse without diacritics.
- Words are inflected (`Bulevaru`, `Mercatora`, `Limanu`) - they won't exactly match gazetteer names.
- Names are ambiguous: "Bulevar" can be Bulevar oslobođenja, Bulevar Evrope, Bulevar cara Lazara, Bulevar Mihajla Pupina, Bulevar kralja Petra I, Bulevar despota Stefana, Bulevar Jaše Tomića.
- Local nicknames not in OSM: Spens, Štrand, Big, Limanska pijaca, Promenada, Sajam, Železnička...
- Streets are lines, not points; a street name alone is imprecise.

## 4. Architecture

```
---------- OFFLINE (scripts in /scripts, run once, outputs committed or in /data) ----------
[B] viber.db -> export_messages.py -> data/messages.sqlite
                 (clean, anonymize, dedupe, drop media/links)
[B]   |--> llm_label.py -> data/labels_silver.jsonl   (~2000 msgs: class + location spans)
[B]   |      `--> train_classifier.py (Colab GPU) -> models/classifier/
[A+B] `--> data/gold_test.jsonl  (150 msgs labelled BY HAND, never used for training)

[A] Overpass API -> build_gazetteer.py -> data/gazetteer.json
[A+B]              + data/aliases.json (~80 hand-written nicknames)
[A]                    `--> index_gazetteer.py -> data/lucene/gazetteer/  (BM25)
                                               `--> data/gazetteer_vectors.npy (Embedić)

---------- ONLINE (FastAPI, /backend) ----------
[A] Replay task (simulated clock, speed xN) -> pipeline.process(message)
[B]  0. normalize.py   clean text (for models) + text_norm: lowercase, no diacritics (for matching)
[B]  1. classify.py    fine-tuned BERTić -> noise | patrol | accident | jam | clear
                       noise -> store in messages index, stop
[B]  2. extract.py     classla/bcms-bertic-ner LOC spans + gazetteer/alias dictionary matcher
                       + merge rule "kod X na Y"
[A]  3. georesolve.py  a) Lucene BM25 top-10 + Embedić cosine top-10
                       b) reciprocal rank fusion
                       c) spatial disambiguation (closest pair / street intersection)
                       d) confidence < threshold -> unresolved
[A]  4. aggregate.py   same type + <=300 m + <=20 min -> same event; "clear" closes nearby event;
                       TTL: jam 30, patrol 60, accident 90 min
[A]  lucene_store.py   indexes: events (geo, ts, type, count, status), messages (full text)

[A] API: GET /events, GET /events/{id}/messages, GET /search, GET /unresolved
         POST /replay/start, POST /replay/pause, GET /replay/status, POST /ingest
[B] React + Leaflet: polls /events every 2 s, pins coloured by type, opacity = 1 - age/ttl,
    live feed, search, unresolved panel, replay controls, "test a message" box

---------- EVALUATION (scripts/eval.py on gold_test.jsonl) ----------
[B] classifier macro-F1 (vs keyword rules, vs zero-shot LLM), span F1 (NER vs NER+dict)
   , LLM-vs-human Cohen's kappa
[A] geo accuracy within 250 m + Recall@5: BM25 only, Embedić only, hybrid, hybrid+spatial
```

`[A]` = Person A owns it, `[B]` = Person B owns it.

## 5. Models and libraries

| Purpose | Choice | Notes |
|---|---|---|
| Classifier | `classla/bcms-bertic` + `AutoModelForSequenceClassification`, 5 labels | Fine-tune on Colab (GPU), ~3-5 epochs, save to `models/classifier/`. Inference on CPU. |
| NER | `classla/bcms-bertic-ner` | No training. `pipeline("token-classification", aggregation_strategy="simple")`. Use only LOC (and optionally ORG - shops like "Mercator" may come as ORG). Labels in the model config may be lowercase (e.g. `B-loc`); check `model.config.id2label`. |
| Embeddings | `djovak/embedic-large` via `sentence-transformers` | Fallback `djovak/embedic-base` if too slow on CPU. Normalize vectors, cosine = dot product. |
| Lexical IR | PyLucene (Docker base image `coady/pylucene`) | Check the Lucene version inside the image and use matching API; LLMs often generate outdated PyLucene code. Call `lucene.initVM()` once per process; worker threads need `attachCurrentThread()`. |
| Backend | FastAPI + uvicorn | Single worker (PyLucene JVM + models loaded once). |
| Frontend | React (Vite) + `react-leaflet` | OSM tiles. Fix default Leaflet marker icons under Vite, or use `CircleMarker`. |
| Geo math | `shapely`, `pyproj` or plain haversine | Point-to-line distance for streets, intersections of street lines. |
| Labelling | Any LLM API | Anonymize before sending. |

Torch in Docker: install the CPU wheel (`--index-url https://download.pytorch.org/whl/cpu`) to avoid multi-GB CUDA images.

## 6. Data contracts (DO NOT change without telling the other person)

### 6.1 `data/messages.sqlite` - table `messages`

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | stable id |
| `chat_id` | TEXT | anonymized group id |
| `ts` | INTEGER | Unix epoch milliseconds |
| `text` | TEXT | cleaned, anonymized original |
| `text_norm` | TEXT | lowercase, diacritics removed, whitespace collapsed |

Original Viber desktop DB usually has a `Messages` table (`Body`, `TimeStamp` in ms, `ChatID`, `ContactID`) - inspect the real schema first with `sqlite3 viber.db ".tables"` and `.schema`.

### 6.2 Labels - `labels_silver.jsonl` and `gold_test.jsonl` (one JSON per line)

```json
{"id": 123, "text": "patrola kod merkatora na bulevaru",
 "label": "patrol",
 "locations": [{"text": "merkatora na bulevaru", "start": 11, "end": 32}],
 "gold_lat": 45.2461, "gold_lon": 19.8412}
```

`gold_lat/gold_lon` only in the gold set (null if location unclear). Character offsets are into `text`.

Label guidelines

- `patrol` - police, radar, traffic control, "murija", "pandure", "saobraćajci", "radar".
- `accident` - crash, "udes", "sudar", "nesreća", ambulance at a crash.
- `jam` - "gužva", "zastoj", "kolona", "stoji sve", roadworks causing delays.
- `clear` - a previous event is gone: "čisto", "otišli", "pomerili se", "nema ih više", "prošlo".
- `noise` - everything else: greetings, jokes, questions without info ("ima li nešto na mostu?"), thanks, off-topic.
- If one message has two events, label the main one.

### 6.3 `data/gazetteer.json`

```json
[{"gaz_id": "way/123456", "name": "Bulevar oslobođenja", "name_norm": "bulevar oslobodjenja",
  "kind": "street",              // "street" | "poi" | "area"
  "category": "primary",         // OSM highway type or amenity/shop type
  "lat": 45.2539, "lon": 19.8373,  // centroid / representative point
  "geometry": [[45.24, 19.83], [45.25, 19.84]],  // lat,lon list for streets; null for poi
  "aliases": ["bulevar", "bul. oslobodjenja"]}]
```

Bounding box of Novi Sad (incl. Petrovaradin, Sremska Kamenica): roughly south 45.20, west 19.72, north 45.32, east 19.95. Include named `highway=*` ways (merge segments with same name), `shop=supermarket|mall`, `amenity=fuel|school|hospital|marketplace`, `junction=roundabout`, `bridge=yes` with names, `place=suburb|neighbourhood|quarter`.

`data/aliases.json`: `{"spens": "way/...", "štrand": "node/...", "big": "...", ...}` mapping nickname -> `gaz_id`.

### 6.4 Python pipeline types (`backend/app/pipeline/types.py`)

```python
from dataclasses import dataclass, field
from typing import Literal, Optional

Label = Literal["noise", "patrol", "accident", "jam", "clear"]

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
```

### 6.5 Function signatures

```python
# [B] backend/app/pipeline/normalize.py
def clean(text: str) -> str
def normalize(text: str) -> str            # lowercase, strip diacritics (đ->dj), collapse spaces

# [B] backend/app/pipeline/classify.py
def classify(text: str) -> tuple[Label, float]           # label, probability

# [B] backend/app/pipeline/extract.py
def extract(text: str, text_norm: str) -> list[Mention]

# [A] backend/app/pipeline/georesolve.py
def retrieve(mention: Mention, k: int = 10) -> list[Candidate]   # hybrid BM25 + dense, fused
def georesolve(mentions: list[Mention]) -> Resolved

# [A] backend/app/pipeline/aggregate.py
def aggregate(label: Label, resolved: Resolved, msg: Message, now_ts: int) -> Optional[Event]

# [A] backend/app/pipeline/__init__.py
def process(msg: Message, now_ts: int) -> dict   # runs 0->4, stores results, returns debug trace
```

`process()` returns a trace dict (label, prob, mentions, candidates, resolved, event_id) - used by `/ingest` and for debugging.

### 6.6 REST API (`backend/app/main.py`) - the frontend depends on this

All timestamps are epoch ms. `now` = simulated replay clock.

| Method & path | Query / body | Response |
|---|---|---|
| `GET /events` | `bbox=south,west,north,east` (opt), `since` (opt, default now-90min), `type` (opt, comma list), `status=active` (default) | `{"now": ts, "events": [Event...]}` + each event has `"age_min"` |
| `GET /events/{id}/messages` | - | `{"messages": [{"id","ts","text","label","prob"}]}` |
| `GET /search` | `q`, `limit=20` | `{"results": [{"id","ts","text","label","score"}]}` |
| `GET /unresolved` | `limit=50` | `{"messages": [{"id","ts","text","label","mentions":[...]}]}` |
| `POST /replay/start` | `{"speed": 60, "start_ts": null}` | `{"status": "running", "now": ts}` |
| `POST /replay/pause` | - | `{"status": "paused", "now": ts}` |
| `POST /replay/reset` | - | clears indexes, resets clock |
| `GET /replay/status` | - | `{"status", "now", "speed", "processed", "total"}` |
| `POST /ingest` | `{"text": "...", "ts": null}` | trace dict from `process()` |
| `GET /health` | - | `{"ok": true}` |

Enable CORS for `http://localhost:5173` and the nginx frontend origin.

Frontend colours: patrol `#1f5fa8` (blue), accident `#c0392b` (red), jam `#e67e22` (orange). Opacity = `max(0.15, 1 - age_min / ttl_min)`.

## 7. Algorithm details (so both sides agree)

Stage 0 - normalize: remove emoji/URLs, collapse whitespace; `text_norm` = lowercase + map `č->c ć->c š->s ž->z đ->dj`. Models get `text`; lexical matching uses `text_norm`.

Stage 2 - extract:
1. Run NER on `text`; keep LOC (and ORG if it matches the gazetteer).
2. Dictionary matcher: slide n-grams (1-4 tokens) over `text_norm`, match against gazetteer `name_norm` + aliases using prefix match on each token (handles endings: `bulevaru` starts with `bulevar`, `merkatora`~`mercator` - treat `k/c` as equal in norm or use fuzzy ratio >= 85).
3. Union NER + dict spans, drop overlaps (keep longer).
4. Merge: two spans separated by <=3 tokens that are only prepositions/conjunctions (`kod, na, u, iza, ispred, blizu, pored, kraj, prema, ka, sa, i, ugao, uglu, raskrsnica`) -> one `Mention(source="merged")`, but keep the parts too (Stage 3 needs them for spatial checks).

Stage 3 - georesolve:
1. For each atomic mention: BM25 top-10 from Lucene (fields `name_norm`, `aliases`; fuzzy `~1` on tokens >=5 chars) and dense top-10 (embed mention text with Embedić, cosine vs `gazetteer_vectors.npy`).
2. Reciprocal rank fusion: `score = sum 1/(60 + rank)`.
3. One mention -> best candidate; `precision="street"` if kind street else `"point"`.
4. Two+ mentions -> for all pairs of top-5 candidates compute distance (point-point, point-line, or line-line intersection). Choose the pair minimizing distance with a penalty for low fused score. If a street crosses a street -> `precision="intersection"`, coordinates = intersection point. If POI + street -> POI coordinates.
5. `confidence` = fused score normalized to 0-1 (x 0.5 if pair distance > 800 m). If `confidence < THRESHOLD` (start 0.35, tune on gold set) -> unresolved.
6. Only Novi Sad bbox results allowed.

Stage 4 - aggregate:
- `patrol/accident/jam`: find active event with same type, distance <= 300 m, `now - last_ts` <= 20 min -> update (`report_count += 1`, `last_ts`, append message id, keep location of highest confidence). Else create new.
- `clear`: find nearest active event (any type) within 500 m, last 90 min -> `status="cleared"`. No location -> ignore.
- Expiry at query time: `now - last_ts > ttl_min` -> `expired` (not returned by default).
- TTL: jam 30, patrol 60, accident 90 minutes.

Lucene indexes (Person A):
- `gazetteer`: `gaz_id` (StringField stored), `name` (stored), `name_norm` + `aliases` (TextField, analyzer: StandardTokenizer + LowerCase + ASCIIFolding), `kind`, `lat`, `lon` (stored).
- `events`: `id`, `type` (StringField), `status`, `location` (`LatLonPoint` for bbox queries + stored lat/lon), `first_ts`/`last_ts` (`LongPoint` + stored), `report_count`, `message_ids` (stored JSON). Updates via `updateDocument(Term("id", ...))`.
- `messages`: `id`, `ts` (LongPoint + stored), `text` (TextField, Serbian-friendly analyzer: lowercase + ASCIIFolding / `SerbianNormalizationFilter`), `label`, `resolved` (bool as string), `event_id`.
- Use `SearcherManager` or reopen `DirectoryReader` after commits.

## 8. Repository layout

```
mapens/
|- MAPENS_CONTEXT.md          <- this file
|- PROGRESS.md                <- each person appends what they finished (see section 12)
|- docker-compose.yml          [A]
|- data/
|  |- raw/viber.db             (NEVER committed - shared privately; contains all chats, contacts, phone numbers)
|  |- messages.jsonl           (committed: anonymized, traffic groups only - output of export_messages.py)
|  |- messages.sqlite          (gitignored: rebuilt from messages.jsonl on startup/first run)
|  |- lucene/                  (gitignored: rebuilt by scripts)
|  `- gazetteer.json, aliases.json, labels_silver.jsonl, gold_test.jsonl  (committed)
|- models/                     (gitignored; classifier weights)
|- scripts/
|  |- export_messages.py       [B]
|  |- llm_label.py             [B]
|  |- train_classifier.ipynb   [B]  (Colab)
|  |- build_gazetteer.py       [A]
|  |- index_gazetteer.py       [A]
|  `- eval.py                  [A: geo part, B: NLP part]
|- backend/
|  |- Dockerfile               [A]  FROM coady/pylucene
|  |- requirements.txt
|  `- app/
|     |- main.py               [A]  FastAPI app, endpoints, startup loading
|     |- config.py             [A]  paths, thresholds, TTLs
|     |- replay.py             [A]
|     |- index/lucene_store.py [A]
|     `- pipeline/
|        |- types.py           [A+B]
|        |- normalize.py       [B]
|        |- classify.py        [B]
|        |- extract.py         [B]
|        |- georesolve.py      [A]
|        |- aggregate.py       [A]
|        `- __init__.py        [A]  process()
`- frontend/                   [B]
   |- Dockerfile               (Vite build -> nginx)
   `- src/ (App.jsx, MapView.jsx, EventFeed.jsx, SearchBox.jsx, UnresolvedPanel.jsx, ReplayControls.jsx, api.js)
```

## 9. Work split

### Person A - IR / backend / Docker

1. Repo skeleton, `docker-compose.yml`, backend Dockerfile on `coady/pylucene` with a working `GET /health`.
2. `build_gazetteer.py` (Overpass -> `gazetteer.json`, merge street segments by name).
3. `index_gazetteer.py` (Lucene BM25 index + Embedić vectors).
4. `georesolve.py` (hybrid retrieval, RRF, spatial disambiguation, threshold).
5. `lucene_store.py` (events + messages indexes), `aggregate.py`, `replay.py`, `pipeline.process()`.
6. All API endpoints in section 6.6.
7. Geo evaluation (BM25 / dense / hybrid / hybrid+spatial; accuracy@250 m, Recall@5). Tune threshold.
8. README: setup + architecture.

Temporary mocks A may use: `classify()` = keyword rules; `extract()` = dictionary matcher only.

### Person B - NLP / data / frontend

1. `export_messages.py` (inspect `viber.db`, clean, anonymize, dedupe -> `messages.sqlite`).
2. `llm_label.py` (batch labelling to `labels_silver.jsonl`; spot-check 50).
3. `train_classifier.ipynb` on Colab -> `models/classifier/`; report metrics.
4. `normalize.py`, `classify.py`, `extract.py` (NER + dictionary matcher + merge rule).
5. React + Leaflet frontend (first against mock JSON matching section 6.6, then real API).
6. NLP evaluation (classifier vs keyword rules vs zero-shot LLM, span F1, kappa).
7. Report: results tables, error examples.

Temporary mocks B may use: static `mock_events.json` in the shape of `GET /events`.

### Shared

- Day 1: agree on section 6 contracts and label guidelines, write `aliases.json`.
- Day 5: gold test set - each labels 100 messages, 50 overlap (inter-annotator agreement), include `gold_lat/gold_lon` (look up on openstreetmap.org).
- Day 6: `docker compose up` on a fresh clone; walk each other through the code.

### Day plan

| Day | Person A | Person B |
|---|---|---|
| 1 | Skeleton, Docker + PyLucene health check, gazetteer builder | DB export + anonymize, start LLM labelling |
| 2 | Gazetteer Lucene index + embeddings, manual retrieval tests | Check labels, train classifier, map skeleton on mocks |
| 3 | `georesolve.py` | `normalize.py`, `classify.py`, `extract.py` |
| 4 | Stores, aggregate, replay, API -> integration evening | Frontend on real API |
| 5 | Tune parameters from replay errors | Search, unresolved panel, event detail; gold set (both) |
| 6 | Geo eval; Docker fresh-clone test | NLP eval |
| 7 | README, bug fixes, demo rehearsal | Report, demo rehearsal |

## 10. Known pitfalls

- PyLucene API differs between Lucene versions; check `lucene.VERSION` in the container before writing code.
- PyLucene + FastAPI threads: call `lucene.getVMEnv().attachCurrentThread()` in any thread touching Lucene (including the replay background task).
- Loading models at import time in multiple uvicorn workers -> OOM. Use one worker; load in the startup/lifespan handler.
- Hugging Face downloads at container start are slow: mount a volume for `HF_HOME`.
- Overpass: be polite, run once, save to JSON. Do not call Nominatim/Overpass at runtime.
- Viber timestamps are ms; Python `datetime.fromtimestamp` expects seconds.
- Replay must drive a simulated `now`; all "last 60 minutes" logic uses simulated time, not wall clock.
- Leaflet in Vite: import `leaflet/dist/leaflet.css`; default marker icons break - use `CircleMarker`.
- Don't send non-anonymized messages to external LLM APIs; don't commit `viber.db`.
- Evaluate only on `gold_test.jsonl`; exclude those ids from training.

## 11. Rules for the AI assistant

1. Respect the contracts in section 6. If a change is needed, say so explicitly and tell the user to inform the other person and update this file.
2. One module at a time. Produce complete, runnable files (not fragments) with a `if __name__ == "__main__":` block that runs on a few hard-coded Serbian examples.
3. Explain briefly what the code does and why, in plain language - the student must defend it at the exam.
4. Stay within the owner's files unless asked; if the other person's module is missing, use the mocks from section 9.
5. Prefer simple, readable code over clever abstractions. Pin library versions in `requirements.txt`.
6. When unsure about a library API (especially PyLucene), say so and give a quick check command.
7. After finishing a task, output a short PROGRESS.md entry (format in section 12) the user can paste.
8. Follow the writing style rules in section 14 for everything you write: code, comments, docstrings, markdown, UI text, log messages and commit messages.

## 12. Session start and progress log

### Session start (user fills in and sends after this file)

```
I am Person [A / B].
Today is day [1-7].
My task now: [e.g. "implement georesolve.py"]

What I have already done:
- ...

What the other person has done (from PROGRESS.md):
- ...

Current problems / errors:
- ...
```

### PROGRESS.md entry format

```
## [Day N] Person [A/B] - <module/task>
- Status: done | partial | blocked
- Files: backend/app/pipeline/georesolve.py, ...
- How to run/test: `python -m app.pipeline.georesolve`
- Contract changes: none | <describe>
- Notes for the other person: ...
```

---

## 13. Repo setup (already done - Day 0)

The skeleton exists; every module in section 8 is a stub with the agreed signature that raises `NotImplementedError`. Fill in only your own files.

- Run everything: `cp .env.example .env` then `docker compose up --build`. API on http://localhost:8000 (`/health` works, other endpoints return 501 until implemented), UI on http://localhost:5173.
- Frontend dev: `cd frontend && npm install && npm run dev`. The frontend calls the backend through the `/api` prefix (Vite proxy in dev, nginx in Docker) - never hard-code `localhost:8000`. `src/api.js` has `USE_MOCK = true` and serves `src/mock/events.json` until the real API exists.
- Backend code is mounted into the container (`./backend/app`, `./scripts`); restart the backend container to pick up changes.
- Not in git, rebuilt automatically by `scripts/setup.sh` (run on backend start): `models/classifier` (downloaded from Hugging Face repo in `CLASSIFIER_REPO`), `data/messages.sqlite` (from `messages.jsonl` via `scripts/load_messages.py`), `data/lucene/` + `data/gazetteer_vectors.npy` (via `scripts/index_gazetteer.py`). Pretrained NER/embedding models download on first use into the `hf-cache` volume. A step that fails only prints a warning, so the API still starts while modules are stubs.
- Classifier sharing: after training, Person B runs `hf auth login` and `hf upload <hf-username>/mapens-classifier models/classifier .`, then sets `CLASSIFIER_REPO` in `.env.example`.
- Raw data: `viber.db` goes in `data/raw/` (gitignored, shared privately). Only the anonymized `data/messages.jsonl` is committed.
- Tunable parameters (thresholds, distances, TTLs, bbox) live in `backend/app/config.py`.
- Line endings: `.gitattributes` forces LF for `.sh`, `.py`, Dockerfiles - required because the repo is edited on Windows but runs in Linux containers.

## 14. Writing style rules (code, comments, docs, UI, commits)

The repo must not read like default LLM output. Apply these rules to every file and every commit message. Run `python scripts/check_style.py` before committing.

Characters

- Use plain ASCII punctuation only. Hyphen `-`, never the em dash or en dash. Write `->` and `<-` instead of arrow symbols, `...` instead of the ellipsis character, `x` instead of the multiplication sign, `<=` and `>=` instead of the math symbols.
- Straight quotes `"` and `'` only, no curly quotes.
- No emoji anywhere: not in code, comments, logs, UI, docs or commit messages. No check marks, rockets, sparkles or warning signs.
- No box-drawing or decorative characters. Directory trees use `|-` and `` `- ``.
- Serbian letters (č ć š ž đ) are allowed and required in data, examples, gazetteer names and UI text in Serbian. They are the only allowed non-ASCII characters.

Wording

- Plain, short, specific sentences. Say what the thing does.
- Do not use filler or buzzwords: delve, leverage, seamless, robust, comprehensive, crucial, powerful, elevate, streamline, cutting-edge, "it's worth noting", "in summary", "let's dive in", "under the hood", "game changer". <!-- check_style: ignore -->
- No hype or friendliness in text: no "Happy coding", no "Great question", no exclamation marks in UI text or logs.
- Do not over-format markdown: no bold for emphasis in every sentence, no heading for every paragraph, no emoji headings. Short lists and tables are fine where they help.

Code and comments

- Comments explain why, not what. Do not narrate obvious code (`# increment counter`, `# Step 1: import libraries`).
- No decorative banner comments (`# ==========`, `# ----- SECTION -----`).
- Docstrings only where they add information: one or two lines, no "This function..." boilerplate, no Args/Returns blocks for trivial functions.
- No leftover generic TODOs like "add error handling here". A TODO names the owner and the concrete task: `# TODO(A): reopen reader after commit`.
- Log and print messages are short and plain: `loaded 1523 gazetteer entries`, not `Successfully loaded all entries!`.
- Names are descriptive and consistent with the contracts in section 6; no `data2`, `temp_final`, `new_helper`.

Commits

- Short imperative subject in lowercase or sentence case, max about 60 characters: `add gazetteer builder`, `fix bbox filter in /events`.
- No emoji, no "Generated by", no long bullet lists for small changes.

