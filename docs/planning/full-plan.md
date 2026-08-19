# Full plan — Page-to-Markdown Converter

This is the complete design plan preserved from the original planning session.
Nothing here is speculative; every decision below is locked and reflected in
the code, ADRs, and Copilot configuration.

## TL;DR

One FastAPI app serves both the JSON API (`/api/convert` accepts `html` from the
extension OR `url` from Swagger/landing page) and a Jinja2 + Bootstrap 5 marketing
site (home, blog, legal). All Python, one repo, one deploy. Blog and legal are
Markdown files. Extension is TypeScript MV3, distributed as ZIP only for v1 with
per-browser install videos on the home page.

## Stack

- Backend + site: FastAPI, Uvicorn, Jinja2, Bootstrap 5 (local, no CDN)
- Extraction: trafilatura (primary), readability-lxml + markdownify (fallback)
- URL fetch: httpx (plain GET, no browser)
- Queue: Celery + Redis (for `download` and `email` delivery methods)
- Email: SMTP via smtplib
- Content: python-frontmatter + markdown
- Rate limiting: slowapi
- Extension: TypeScript, Manifest V3

## Phase 1 — Dual-input API

### Request contract

`POST /api/convert`

- `html` (string, optional) — raw outerHTML from the extension
- `url` (string, optional) — page URL, server fetches it
- Exactly one of `html` or `url` required (422 `missing_input` otherwise)
- `sourceUrl` (string, optional) — defaults to `url` when only `url` is provided
- `deliveryMethod`: `"inline" | "download" | "email"` (default `"inline"`)
- `email` (string, required only when `deliveryMethod == "email"`)

### Response contract

- `inline` → 200 with `{ sourceUrl, title, markdown, wordCount, extractedAt }`
- `download` / `email` → 202 with `{ jobId }`
- Empty extraction → 422 `no_readable_content`
- Empty extraction from URL fetch → 422 `js_rendered_page_use_extension`
- Missing both `html` and `url` → 422 `missing_input`

### Job endpoints

- `GET /api/jobs/{jobId}` → `{ status, downloadUrl, error }`
- `GET /api/download/{jobId}` → serves `.md` file, 404 after 1h TTL

### Server-side fetcher (URL path only)

- httpx GET, realistic User-Agent, 10s timeout, follow redirects
- Body cap: 5MB for URL fetches, 10MB for HTML uploads
- Strip `<script>` and `<style>` server-side before extraction
- No robots.txt handling in v1 (documented limitation)

### Extraction pipeline

1. `trafilatura.extract(html, output_format="markdown", include_links=True, include_images=True)`
2. If output thin/empty → readability-lxml + markdownify fallback
3. Resolve relative URLs in links and images against `sourceUrl`
4. Still empty → 422 (`js_rendered_page_use_extension` on URL path, else `no_readable_content`)

### Rate limits

- `html` path: unlimited (caller did the work)
- `url` path: 30/min per IP
- `/try` (landing form): 10/min per IP

## Phase 2 — Async delivery (Celery + Redis)

- Inline path stays synchronous, no queue
- `download` and `email` enqueue a task, return `202 { jobId }` immediately
- Worker runs extraction, then:
  - `download`: writes `.md` to `/tmp/jobs/{jobId}.md`, status `ready`, TTL 1h
  - `email`: sends `.md` as attachment via SMTP, status `sent`
- Job state in Redis (hash keyed by jobId), 24h TTL
- One retry on email failure, then `failed` with error message
- Cleanup: Celery beat sweeps expired download files hourly

## Phase 3 — Marketing site (Jinja2 + Bootstrap 5)

### Routes

- `GET /` — home
- `POST /try` — landing "try it" form, calls extraction directly, re-renders home
- `GET /blog` — paginated post list, `?page=N` (10/page)
- `GET /blog/{slug}` — single post
- `GET /legal/privacy`, `/legal/terms`, `/legal/cookies`
- `GET /download/extension.zip` — serves packaged extension

### Home page sections

1. Hero: headline, subheadline, one big "Download extension (.zip)" button
2. Browser picker: Chrome / Edge / Firefox / Brave. Selecting one swaps in that browser's install video + written step-by-step instructions.
3. Try-it box: URL input + Convert button. Submits to `/try`, renders returned markdown in a scrollable `<pre>` with a Copy button. Clear error box on 422.
4. Features: works on SPAs, works logged in, clean extraction, three delivery methods
5. Footer: blog, legal pages, GitHub

### Content

- `app/content/blog/*.md` — frontmatter: title, slug, date, author, excerpt, tags
- `app/content/legal/{privacy,terms,cookies}.md`
- Parsed once at startup, cached in a dict
- Pagination: sort by date desc, slice `[start:start+10]`

### No analytics in v1

No tracking scripts, no cookie banner needed. Cookie policy page says "we set no cookies."

## Phase 4 — Extension (TypeScript MV3)

### Structure

- `extension/src/content.ts` — grabs `outerHTML` after MutationObserver settles, strips scripts/styles, gzips
- `extension/src/background.ts` — service worker, fetch to backend, job polling, notifications
- `extension/src/popup.tsx` — radio buttons, email field, Convert button, status states
- `extension/manifest.json` — MV3, permissions: `activeTab`, `scripting`, `storage`, `downloads`

### Popup flows

- Preview: POST inline, show markdown in scrollable pane, Copy button
- Download: POST download, poll job, `chrome.downloads.download()` when ready
- Email: POST email, poll job, show "sent" confirmation

## Phase 5 — Packaging & deploy

- Build extension with Vite, `zip -r dist/extension.zip extension/dist/*`
- Serve via `/download/extension.zip`
- Record 4 short install videos, store in `app/static/videos/`
- Docker compose: fastapi (uvicorn), celery worker, redis
- Nginx or Caddy in front for TLS

## Mock request/response

### URL-based inline (landing page try-it)

```
POST /api/convert
{ "url": "https://en.wikipedia.org/wiki/Markdown", "deliveryMethod": "inline" }
```

```
200
{
  "sourceUrl": "https://en.wikipedia.org/wiki/Markdown",
  "title": "Markdown - Wikipedia",
  "markdown": "# Markdown\n\nMarkdown is a lightweight markup language...",
  "wordCount": 3421,
  "extractedAt": "2026-08-19T14:47:02Z"
}
```

### HTML-based inline (extension preview)

```
POST /api/convert
{ "html": "<html>...</html>", "sourceUrl": "https://example.com/x", "deliveryMethod": "inline" }
```

Response shape identical.

### Download (async)

`deliveryMethod: "download"` → `202 { "jobId": "..." }`
Poll `/api/jobs/{jobId}` → `{ "status": "ready", "downloadUrl": "/api/download/..." }`

### Email (async)

`deliveryMethod: "email"`, `email: "..."` → `202 { "jobId": "..." }`
Poll `/api/jobs/{jobId}` → `{ "status": "sent" }`

### Failures

- `422 { "error": "missing_input" }`
- `422 { "error": "js_rendered_page_use_extension" }`
- `422 { "error": "no_readable_content" }`
- Job `failed` with `error: "smtp_timeout"` after one retry

## Verification checklist

**API**

1. `curl` with only `url` → inline markdown
2. `curl` with only `html` → inline markdown
3. `curl` with neither → 422 `missing_input`
4. `curl` a JS-heavy URL → 422 `js_rendered_page_use_extension`
5. `deliveryMethod: download` → 202 → poll ready → GET file works
6. `deliveryMethod: email` → 202 → poll sent → email arrives
7. Oversized payload rejected with clear error
8. 31st URL-path request in a minute → 429

**Site** 9. `GET /` renders hero + browser picker + try-it form 10. Browser picker swaps videos when clicked 11. Try-it form with a Wikipedia URL renders markdown + Copy works 12. `GET /blog` shows first 10, `?page=2` shows next 10 13. `GET /blog/{slug}` renders a real post 14. `GET /legal/{privacy,terms,cookies}` all render 15. `GET /download/extension.zip` downloads the built zip

**Extension** 16. Install unpacked, click on a real article → Preview shows markdown 17. Download flow saves a `.md` file 18. Email flow sends an email 19. SPA page still extracts correctly

## Locked decisions

- All-Python: FastAPI + Jinja2 + Bootstrap 5. No Node front-end.
- Same endpoint accepts `html` or `url`; server-side fetch is plain GET.
- Blog + legal as Markdown files in repo. No CMS, no DB for content.
- Extension distributed as ZIP only in v1. No store submissions.
- Home page has a browser picker with per-browser install videos.
- No analytics, no cookies, no banner in v1.
- Rate limits: 30/min on URL path, 10/min on `/try`, unlimited on `html` path.
- Body caps: 5MB URL fetch, 10MB HTML upload.
- Copilot-only agent setup: `.github/copilot-instructions.md` is the single
  source of truth. No `AGENTS.md`, no `.claude/CLAUDE.md`.

## Out of scope for v1

- User accounts / auth
- MCP for the product itself
- Headless browser fallback for URL path
- Multi-language extraction tuning
- Store submissions (Chrome / Edge / Firefox)
- Analytics + cookie banner

## Related docs

- [Architecture](../architecture.md)
- [API contract](../api.md)
- [Extension](../extension.md)
- [Deployment](../deployment.md)
- [Copilot setup](../copilot-setup.md)
- [Decisions (ADRs)](../decisions/)
- [Original context](original-context.md)
