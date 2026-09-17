"""FastAPI app. Owner: Person A. API contract: MAPENS_CONTEXT.md §6.6.

Endpoints are declared with the agreed shapes; unimplemented ones return 501.
Models and Lucene are loaded once in `lifespan` (single uvicorn worker).
"""
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO(A): lucene.initVM(), open indexes, load models, create replay controller
    yield
    # TODO(A): close index writers


app = FastAPI(title="MapeNS API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def not_implemented():
    raise HTTPException(status_code=501, detail="Not implemented yet")


class ReplayStart(BaseModel):
    speed: float = 60
    start_ts: Optional[int] = None


class IngestBody(BaseModel):
    text: str
    ts: Optional[int] = None


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/events")
def get_events(bbox: Optional[str] = None, since: Optional[int] = None,
               type: Optional[str] = None, status: str = "active"):
    not_implemented()


@app.get("/events/{event_id}/messages")
def get_event_messages(event_id: str):
    not_implemented()


@app.get("/search")
def search(q: str, limit: int = 20):
    not_implemented()


@app.get("/unresolved")
def unresolved(limit: int = 50):
    not_implemented()


@app.post("/replay/start")
def replay_start(body: ReplayStart):
    not_implemented()


@app.post("/replay/pause")
def replay_pause():
    not_implemented()


@app.post("/replay/reset")
def replay_reset():
    not_implemented()


@app.get("/replay/status")
def replay_status():
    not_implemented()


@app.post("/ingest")
def ingest(body: IngestBody):
    not_implemented()
