"""Server-side URL fetching for the /api/convert url path. Plain GET only."""

from __future__ import annotations

import logging

import httpx

log = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36 page-to-markdown-converter/0.1"
)
_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
_MAX_BYTES = 5 * 1024 * 1024


class FetchError(Exception):
    """Raised when the URL fetch fails or returns something we can't use."""


async def fetch(url: str) -> str:
    """Fetch a URL as HTML. Enforces timeout and 5MB body cap."""
    headers = {"User-Agent": _USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
    try:
        async with httpx.AsyncClient(
            timeout=_TIMEOUT, follow_redirects=True, headers=headers
        ) as client:
            response = await client.get(url)
    except httpx.HTTPError as exc:
        log.info("fetch failed for %s: %s", url, exc)
        raise FetchError("fetch_failed") from exc

    if response.status_code >= 400:
        raise FetchError(f"fetch_status_{response.status_code}")

    content = response.content[:_MAX_BYTES]
    if len(response.content) > _MAX_BYTES:
        log.info("truncated %s from %d to %d bytes", url, len(response.content), _MAX_BYTES)
    return content.decode(response.encoding or "utf-8", errors="replace")
