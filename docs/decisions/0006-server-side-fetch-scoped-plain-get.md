# 0006 — Server-side fetch scoped to plain GET

Date: 2026-08-19
Status: Accepted

## Context

[0002](0002-dual-input-html-or-url.md) reintroduces server-side URL fetching
for the URL-input path. Left unbounded, that becomes:

- A DDoS amplification vector
- A way to hit internal networks (SSRF) if not restricted
- A performance headache if pages are huge or hostile
- An attractive nuisance if we start adding "render this with a browser" logic

## Decision

Server-side fetching is limited to plain `httpx.get`:

- 10-second timeout
- 5MB body cap on the fetched HTML
- Follow redirects
- Realistic User-Agent
- No headless browser, ever
- Rate limit: 30/min per IP on the URL path (unlimited on the HTML path)
- Strip `<script>` and `<style>` before extraction

If a fetched page returns thin content, we return `422
js_rendered_page_use_extension` — we don't try harder.

## Consequences

**Enables**

- Predictable server load per request
- Simple, testable fetcher
- Clear "use the extension" signal for JS-heavy pages

**Rules out**

- Rendering SPAs server-side (that's the extension's job by design)
- Following long redirect chains that exceed timeout
- Handling paywalled content via the URL path

**Trade-offs**

- Some pages that could technically render with a headless browser return an error
- No robots.txt handling in v1 (documented limitation, revisit if abused)

## Alternatives considered

- Playwright fallback when trafilatura returns thin: doubles infra cost,
  makes extraction latency unpredictable. Rejected for v1.
- No caps: unsafe.
