"""FastAPI entry point. Registers API + site routes and mounts static files."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app import blog
from app.limits import limiter
from app.routes import convert, jobs, pages

_STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):  # type: ignore[no-untyped-def]
    blog.load_all()
    yield


app = FastAPI(
    title="MarkDrop",
    version="0.1.0",
    description="Turn any web page into clean Markdown.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

app.include_router(convert.router)
app.include_router(jobs.router)
app.include_router(pages.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
