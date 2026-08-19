# Project: Page-to-Markdown Converter (Browser Extension + Python Backend)

## What this does
A browser extension captures the fully-rendered HTML of the page the user is
currently viewing, sends it to a Python backend, which extracts the main
content, converts it to clean markdown, and emails the resulting `.md` file
to an address the user provides. No URL fetching/re-rendering server-side —
the extension already has the rendered DOM, so we skip headless browser
infra entirely.

## Why this architecture (context, don't re-litigate)
- Extension captures already-rendered DOM: works on JS-heavy SPAs,
  logged-in/paywalled pages, and sites with bot detection — because the
  user's real browser session already rendered it.
- No Playwright/Puppeteer needed server-side. Backend never fetches URLs.
- Extraction happens server-side in Python because `trafilatura` gives the
  cleanest main-content extraction (strips nav/ads/sidebars) compared to JS
  equivalents — this is the one part of the pipeline where library quality
  differs meaningfully by language.
- Async job queue because extraction + email shouldn't block the extension's
  HTTP request/response cycle.

## Stack

### Extension (Manifest V3 — Chrome/Edge, Firefox-compatible where noted)
- Language: TypeScript
- Content script: grabs `document.documentElement.outerHTML` from the
  active tab after page load (respect SPA hydration — see Edge Cases below)
- Popup UI: delivery method choice (Preview / Download / Email), email
  input field shown only when Email is selected, "Convert this page"
  button, status states (idle / sending / queued / ready / error)
  - Preview: shows markdown in a scrollable pane inside the popup, with a
    "Copy to clipboard" button
  - Download: triggers `chrome.downloads.download()` once job status is
    `ready`
  - Email: same flow as download but no local file, just confirmation once
    status is `sent`
- Background/service worker: handles the fetch() to backend API, manages
  extension state, polls job status for download/email paths, shows badge/
  notification on success or failure
- Sends: `{ html: string, sourceUrl: string, deliveryMethod: string, email?: string }`
  as gzip'd POST body to backend API
- No auth/login system needed for v1 — email is just a destination, not an
  account

### Backend (Python)
- Framework: **FastAPI** — async, fast to build, good for a small API
  surface (1-2 endpoints)
- Extraction: **trafilatura** — `trafilatura.extract(html, output_format="markdown", include_links=True, include_images=True)`
  - Fallback if trafilatura returns thin/empty content: try
    `readability-lxml` + `markdownify` as a secondary pass
- Queue: **Celery** with **Redis** as broker (RQ is the simpler
  alternative if you don't need Celery's retry/chaining features — pick one,
  don't run both)
- Job flow:
  1. API endpoint receives payload, validates `deliveryMethod` and HTML size
  2. If `inline`: run trafilatura synchronously in the handler, return
     markdown directly, no queue involved, no job created
  3. If `download` or `email`: validate email if applicable, enqueue job,
     return `202 Accepted` with a job ID immediately
  4. Celery worker picks up queued jobs: runs trafilatura, then either
     writes `.md` file to temp storage (download) or sends via email
     (email), updates job status accordingly
  5. Store job status in Redis (or DB if you want history) so extension/
     Swagger can poll job ID for status
- Email: SMTP via `smtplib`, or a transactional provider (SendGrid /
  Postmark / AWS SES) — pick provider based on what you already have
  configured. If none yet, SES is a reasonable default given your AWS stack.
- DB: not required for MVP (stateless job processing). If you want job
  history/status tracking, use PostgreSQL with a `jobs` table
  (id, source_url, email, status, created_at, completed_at, error).

## API contract (v1)

Three delivery methods, one endpoint, branch on `deliveryMethod`:

- **`inline`** — synchronous, no queue. Runs extraction in the request
  handler and returns the markdown directly in the JSON response. Use this
  for Swagger UI testing and for the extension's "preview" case.
- **`download`** — async via Celery queue. Extraction happens in a worker,
  result is written to a temp file, client polls job status and gets a
  `downloadUrl` once ready. File expires/deletes after a TTL (~1 hour).
- **`email`** — async via Celery queue. Same as download but the worker
  emails the `.md` file instead of exposing a download link.

```
POST /api/convert
Body: {
  "html": "<string, required, raw outerHTML>",
  "sourceUrl": "<string, required>",
  "deliveryMethod": "inline" | "download" | "email",  // default: "inline"
  "email": "<string, required only if deliveryMethod is 'email'>"
}
```

**If `deliveryMethod` is `inline`** — synchronous response, no job created:
```
Response: 200 {
  "sourceUrl": "<string>",
  "title": "<string, extracted page title>",
  "markdown": "<string, full converted markdown>",
  "wordCount": <int>,
  "extractedAt": "<ISO 8601 timestamp>"
}
```
If extraction fails or returns near-empty content:
```
Response: 422 {
  "error": "no_readable_content",
  "message": "No extractable article content found on this page."
}
```

**If `deliveryMethod` is `download` or `email`** — async, returns a job ID:
```
Response: 202 { "jobId": "<uuid>" }
```

```
GET /api/jobs/{jobId}
Response: 200 {
  "status": "queued" | "processing" | "ready" | "sent" | "failed",
  "downloadUrl": "<string | null>",  // populated when status is "ready" (download path only)
  "error": "<string | null>"
}
```

```
GET /api/download/{jobId}
Serves the .md file with Content-Disposition: attachment.
Returns 404 if expired or not yet ready.
```

## Edge cases to handle

**Extension side:**
- SPA content not yet rendered when content script fires — add a short
  delay or MutationObserver-based readiness check before grabbing HTML,
  don't just grab on `DOMContentLoaded`
- Very large pages (some news sites embed huge inline JSON/script blobs) —
  strip `<script>` and `<style>` tags client-side before sending, this
  shrinks payload significantly and trafilatura doesn't need them
- User on a page with no extractable article content (e.g. a dashboard,
  search results page) — trafilatura will return empty/near-empty output,
  surface this back to the user as "no readable content found" rather than
  emailing an empty file

**Backend side:**
- Payload size limits — set a reasonable max (e.g. 10MB) on the FastAPI
  endpoint, reject oversized requests with a clear error
- trafilatura returning None or very short output — trigger the
  readability-lxml fallback before giving up
- Email delivery failure — mark job as failed with the specific error, do
  not silently drop it. Consider one retry via Celery's retry mechanism.
- Malformed/relative URLs inside extracted markdown (links, images) —
  trafilatura's `include_links`/`include_images` can leave relative paths;
  resolve them against `sourceUrl` before writing final markdown

## Explicitly out of scope for v1
- User accounts / auth
- MCP integration (not needed for this use case)
- Headless browser / server-side URL fetching (extension replaces this)
- Multi-language content extraction tuning (trafilatura handles this
  reasonably out of the box, don't over-engineer)

## Suggested build order
1. FastAPI skeleton with `/api/convert` returning a stubbed job ID
   (no queue yet) — validate request/response contract works
2. Wire in trafilatura extraction synchronously first (no Celery), confirm
   output quality on 5-10 real test URLs across different site types
   (news article, blog, docs page, SPA-heavy site)
3. Add Celery + Redis, move extraction into a task, confirm async flow
   works end-to-end
4. Add email sending
5. Build extension: content script → popup → background worker → API call
6. Add job status polling in extension popup (optional but good UX)
7. Add relative URL resolution + fallback extraction path
