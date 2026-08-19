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


API_DESCRIPTION = """
MarkDrop turns any web page into clean Markdown.

## How it works

Send a page to `POST /api/convert`. The request accepts one of two inputs:

- `html`: raw outerHTML captured by the browser extension after the page has
  finished rendering. Use this for JavaScript-heavy pages, logged-in sessions,
  or paywalled content that a server-side fetch would fail on.
- `url`: a public URL. The server fetches the page with a plain HTTP GET
  (no headless browser) and extracts from that. Use this for Swagger, curl,
  or the landing page try-it box.

Exactly one of the two is required. If `url` is used and the page needs a real
browser to render, the response is `422 js_rendered_page_use_extension`.

## Delivery methods

`deliveryMethod` on the same request picks how you receive the Markdown:

- `inline` (default): the response body contains the Markdown itself. Fastest,
  no follow-up calls needed.
- `download`: returns `202` with a `jobId`. Poll `GET /api/jobs/{jobId}` until
  status is `ready`, then fetch `GET /api/download/{jobId}` for the .md file.
  File is deleted 1 hour after it becomes ready.
- `email`: returns `202` with a `jobId`. A Celery worker sends the .md as an
  attachment to the address in the `email` field. Poll `GET /api/jobs/{jobId}`
  until status is `sent` or `failed`.

## Rate limits

- `POST /api/convert`: 60 requests per minute per IP.
- `POST /try` (landing page form): 10 requests per minute per IP.
- `429 Too Many Requests` is returned when the limit is exceeded.

## Payload caps

- `html` uploads: up to 10 MB.
- `url` fetches: server truncates the fetched HTML at 5 MB.

## Error codes

All 4xx errors return `{ "error": "<code>", "message": "<human text>" }`.

| Code | Meaning |
|---|---|
| `missing_input` | Neither `html` nor `url` provided (or both). |
| `email_required` | `deliveryMethod` is `email` but no `email` field. |
| `no_readable_content` | Extraction returned nothing usable (thin page). |
| `js_rendered_page_use_extension` | URL-fetched page needs a real browser. |
| `fetch_failed` | Server could not fetch the URL (timeout, DNS, etc.). |
| `job_not_found` | The `jobId` does not exist or expired. |
| `not_ready` | Download requested before job finished. |

## Source

Open source at
[github.com/devhasibulislam/page-to-markdown-converter](https://github.com/devhasibulislam/page-to-markdown-converter).
"""


TAGS_METADATA = [
    {
        "name": "Convert",
        "description": (
            "The single conversion endpoint. Accepts raw HTML (sent by the browser "
            "extension) or a URL (fetched server-side) and returns Markdown either "
            "inline in the response or via an async job."
        ),
    },
    {
        "name": "Jobs",
        "description": (
            "Poll the status of async conversions and fetch the resulting `.md` "
            "file. Only used when `deliveryMethod` is `download` or `email` on the "
            "convert endpoint. Inline conversions do not create jobs."
        ),
    },
    {
        "name": "Site",
        "description": (
            "HTML pages served by the same app: landing page, blog, legal, and the "
            "browser-extension ZIP download. Not JSON endpoints, listed here so the "
            "OpenAPI spec covers every route."
        ),
    },
    {
        "name": "Meta",
        "description": "Operational endpoints used by Docker healthchecks and uptime monitors.",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):  # type: ignore[no-untyped-def]
    blog.load_all()
    yield


app = FastAPI(
    title="MarkDrop",
    version="0.1.0",
    summary="Turn any web page into clean Markdown.",
    description=API_DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    contact={
        "name": "GitHub",
        "url": "https://github.com/devhasibulislam/page-to-markdown-converter",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

app.include_router(convert.router)
app.include_router(jobs.router)
app.include_router(pages.router)


@app.get(
    "/health",
    tags=["Meta"],
    summary="Health check",
    description="Returns `{\"status\": \"ok\"}` when the API process is running. Used by Docker healthchecks and uptime monitors.",
)
def health() -> dict[str, str]:
    return {"status": "ok"}
