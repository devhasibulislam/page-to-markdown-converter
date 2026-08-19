# API contract

Base URL: `/api`.

## `POST /api/convert`

### Request

```json
{
  "html": "<optional string>",
  "url": "<optional string>",
  "sourceUrl": "<optional string, defaults to url>",
  "deliveryMethod": "inline | download | email",
  "email": "<required only when deliveryMethod == email>"
}
```

Rules:

- Exactly one of `html` or `url` is required.
- `deliveryMethod` defaults to `"inline"`.
- Body caps: `html` up to 10MB, URL-fetched HTML up to 5MB.

### Response — inline (200)

```json
{
  "sourceUrl": "https://en.wikipedia.org/wiki/Markdown",
  "title": "Markdown - Wikipedia",
  "markdown": "# Markdown\n\n...",
  "wordCount": 3421,
  "extractedAt": "2026-08-19T14:47:02Z"
}
```

### Response — download / email (202)

```json
{ "jobId": "8f3c9a2e-4d1b-4f7a-9c2e-1a8b5d6c7e0f" }
```

### Errors (422)

```json
{ "error": "missing_input", "message": "Provide either 'html' or 'url'." }
{ "error": "no_readable_content", "message": "No extractable article content found." }
{ "error": "js_rendered_page_use_extension", "message": "This page needs a real browser to render. Install the extension and try from the page directly." }
```

### Rate limits

- `url`-based requests: 30/min per IP → 429 on exceed
- `html`-based requests: unlimited

## `GET /api/jobs/{jobId}`

```json
{
  "status": "queued | processing | ready | sent | failed",
  "downloadUrl": "/api/download/{jobId} | null",
  "error": "string | null"
}
```

## `GET /api/download/{jobId}`

Serves the `.md` file with `Content-Disposition: attachment`.

- 404 if the job doesn't exist, isn't `ready`, or has expired (1h TTL from `ready`).

## Swagger examples

`/docs` includes two example payloads on `/api/convert`:

- One with `html` (extension pattern)
- One with `url` (Swagger / landing pattern)

## curl examples

Inline via URL:

```bash
curl -X POST http://localhost:8000/api/convert \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://en.wikipedia.org/wiki/Markdown","deliveryMethod":"inline"}'
```

Inline via HTML:

```bash
curl -X POST http://localhost:8000/api/convert \
  -H 'Content-Type: application/json' \
  -d '{"html":"<html>...</html>","sourceUrl":"https://example.com","deliveryMethod":"inline"}'
```

Download:

```bash
curl -X POST http://localhost:8000/api/convert \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://en.wikipedia.org/wiki/Markdown","deliveryMethod":"download"}'
# → { "jobId": "..." }
curl http://localhost:8000/api/jobs/<jobId>
# → { "status": "ready", "downloadUrl": "/api/download/<jobId>" }
curl -O http://localhost:8000/api/download/<jobId>
```
