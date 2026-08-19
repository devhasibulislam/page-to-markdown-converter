# Architecture

## System overview

```
┌─────────────────┐     HTML       ┌──────────────────────────┐
│ Browser         │ ─────────────► │ FastAPI (uvicorn)        │
│ Extension (MV3) │                │  ├─ /api/convert         │
└─────────────────┘                │  ├─ /api/jobs/{id}       │
                                   │  ├─ /api/download/{id}   │
┌─────────────────┐     URL        │  ├─ /  (Jinja2 + BS5)    │
│ Landing "try it"│ ─────────────► │  ├─ /blog, /legal        │
│ or Swagger UI   │                │  └─ /try                 │
└─────────────────┘                └────┬──────────────┬──────┘
                                        │              │
                                        │ enqueue      │ inline
                                        ▼              │ (sync)
                                   ┌────────────┐      │
                                   │ Redis      │◄─────┘
                                   └────┬───────┘
                                        │
                                   ┌────▼───────┐
                                   │ Celery     │ ── SMTP ──► email
                                   │ worker     │ ── file ──► /tmp/jobs/
                                   └────────────┘
```

## Request flows

### Inline (extension preview or landing try-it)

1. Client POSTs `html` or `url` with `deliveryMethod: "inline"`
2. Handler validates input (Pydantic)
3. If `url`: `fetcher.fetch()` → HTML string
4. `extraction.extract(html, source_url)` runs trafilatura → falls back to readability if thin
5. Handler returns `{ title, markdown, wordCount, extractedAt }` inline

### Async (download or email)

1. Client POSTs with `deliveryMethod: "download"` or `"email"`
2. Handler enqueues Celery task, returns `202 { jobId }`
3. Worker runs the same extraction pipeline
4. On `download`: writes `.md` to `/tmp/jobs/{jobId}.md`, sets Redis status `ready`
5. On `email`: sends SMTP with the `.md` attached, sets Redis status `sent`
6. Client polls `GET /api/jobs/{jobId}` until status is terminal

## Why these choices

**FastAPI + Jinja2** — one process serves both API and marketing site. No Node build for the site.

**trafilatura** — best-in-class main-content extraction. This is the one place library quality is language-dependent, so extraction stays in Python.

**httpx (not headless browser)** — the extension already renders the page. Server-side URL fetching is a convenience for testing, not the primary path. Plain GET keeps the server stateless and cheap.

**Bootstrap 5 local** — no CDN dependency, works with strict CSP, no third-party requests.

**Celery + Redis** — extraction is CPU-bound and can take seconds on large pages. Blocking a request thread on it hurts throughput. Redis doubles as job-state store.

**Markdown files for content** — no CMS to run, blog posts live in git with the same review workflow as code.

## What's deliberately not here

- No database. Redis holds transient job state, file content is on disk in Markdown.
- No user accounts. Delivery is the destination, not an identity.
- No headless browser server-side. The extension is the render step.
- No analytics or tracking in v1.
