"""HTML → Markdown extraction: trafilatura primary, readability fallback."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from urllib.parse import urljoin

import trafilatura
from markdownify import markdownify
from readability import Document

log = logging.getLogger(__name__)

_MIN_WORDS = 30
_LINK_RE = re.compile(r"\[([^\]]+)\]\((?!https?://|mailto:|#)([^)]+)\)")
_IMG_RE = re.compile(r"!\[([^\]]*)\]\((?!https?://)([^)]+)\)")
_SCRIPT_STYLE_RE = re.compile(
    r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL
)


@dataclass(frozen=True)
class Extracted:
    title: str
    markdown: str
    word_count: int


class ExtractionError(Exception):
    """Raised when no readable content can be extracted."""


def strip_scripts_and_styles(html: str) -> str:
    return _SCRIPT_STYLE_RE.sub("", html)


def extract(html: str, source_url: str | None = None) -> Extracted:
    """Extract main content as Markdown. Raises ExtractionError if none found."""
    cleaned_html = strip_scripts_and_styles(html)

    markdown = _try_trafilatura(cleaned_html)
    title = _extract_title(cleaned_html) or ""

    if not markdown or _word_count(markdown) < _MIN_WORDS:
        log.info("trafilatura output thin, falling back to readability")
        markdown, fallback_title = _try_readability(cleaned_html)
        title = title or fallback_title

    if not markdown or _word_count(markdown) < _MIN_WORDS:
        raise ExtractionError("no_readable_content")

    if source_url:
        markdown = _resolve_relative_urls(markdown, source_url)

    return Extracted(title=title.strip(), markdown=markdown.strip(), word_count=_word_count(markdown))


def _try_trafilatura(html: str) -> str:
    result = trafilatura.extract(
        html,
        output_format="markdown",
        include_links=True,
        include_images=True,
        include_tables=True,
        with_metadata=False,
    )
    return result or ""


def _try_readability(html: str) -> tuple[str, str]:
    try:
        doc = Document(html)
        summary_html = doc.summary(html_partial=True)
        title = doc.short_title() or ""
        markdown = markdownify(summary_html, heading_style="ATX", strip=["script", "style"])
        return markdown, title
    except Exception as exc:  # readability raises broad errors on odd HTML
        log.warning("readability fallback failed: %s", exc)
        return "", ""


def _extract_title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def _word_count(text: str) -> int:
    return len(text.split())


def _resolve_relative_urls(markdown: str, base_url: str) -> str:
    markdown = _LINK_RE.sub(lambda m: f"[{m.group(1)}]({urljoin(base_url, m.group(2))})", markdown)
    markdown = _IMG_RE.sub(lambda m: f"![{m.group(1)}]({urljoin(base_url, m.group(2))})", markdown)
    return markdown
