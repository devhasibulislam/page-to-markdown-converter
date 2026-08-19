# 0002 — Dual-input API (`html` or `url`)

Date: 2026-08-19
Status: Accepted

## Context

Two callers hit the same conversion endpoint:

- The browser extension already has the rendered HTML in hand. Asking it to
  submit a URL would force the server to re-fetch what the extension already
  has.
- Swagger UI, curl users, and the landing page "try it" form only have a URL.
  Asking them to paste raw HTML is unusable.

Original design (`PROJECT_CONTEXT.md`) forbade server-side fetching entirely.
That made Swagger and the landing page useless for the URL case.

## Decision

`POST /api/convert` accepts either `html` or `url` (exactly one). When `url`
is provided, the server fetches it with `httpx` (plain GET, no headless
browser — see [0006](0006-server-side-fetch-scoped-plain-get.md)). When
extraction from a URL fetch returns thin content, return `422
js_rendered_page_use_extension` so URL callers get a clear "install the
extension" hint.

One endpoint, one contract, two entry paths.

## Consequences

**Enables**

- Swagger and curl work with a URL argument
- Landing page "try it" box works without shipping an extension
- Extension keeps its zero-server-fetch guarantee (see rule in copilot-instructions)

**Rules out**

- Two separate endpoints (would fragment the contract for no benefit)
- Requiring HTML from all callers

**Trade-offs**

- Server-side fetching is now part of the surface (with strict caps and rate limits)

## Alternatives considered

- Two endpoints (`/api/convert-html`, `/api/convert-url`): rejected, adds contract surface for no gain.
- Extension-only: rejected, kills Swagger utility and the landing page pitch.
