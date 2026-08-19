"""Load blog posts and legal pages from Markdown files at startup."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import frontmatter
import markdown as md

_BLOG_DIR = Path(__file__).parent / "content" / "blog"
_LEGAL_DIR = Path(__file__).parent / "content" / "legal"
_MD = md.Markdown(extensions=["fenced_code", "tables", "toc"])


@dataclass(frozen=True)
class Post:
    slug: str
    title: str
    date: date
    author: str
    excerpt: str
    tags: list[str]
    html: str


@dataclass(frozen=True)
class LegalPage:
    slug: str
    title: str
    updated: date
    html: str


_posts: dict[str, Post] = {}
_legal: dict[str, LegalPage] = {}


def load_all() -> None:
    _posts.clear()
    _legal.clear()

    if _BLOG_DIR.exists():
        for path in _BLOG_DIR.glob("*.md"):
            fm = frontmatter.load(path)
            slug = str(fm.get("slug") or path.stem)
            _posts[slug] = Post(
                slug=slug,
                title=str(fm["title"]),
                date=_as_date(fm["date"]),
                author=str(fm.get("author", "")),
                excerpt=str(fm.get("excerpt", "")),
                tags=list(fm.get("tags", []) or []),
                html=_render(fm.content),
            )

    if _LEGAL_DIR.exists():
        for path in _LEGAL_DIR.glob("*.md"):
            fm = frontmatter.load(path)
            slug = path.stem
            _legal[slug] = LegalPage(
                slug=slug,
                title=str(fm["title"]),
                updated=_as_date(fm["updated"]),
                html=_render(fm.content),
            )


def all_posts() -> list[Post]:
    return sorted(_posts.values(), key=lambda p: p.date, reverse=True)


def get_post(slug: str) -> Post | None:
    return _posts.get(slug)


def get_legal(slug: str) -> LegalPage | None:
    return _legal.get(slug)


def paginate(posts: list[Post], page: int, per_page: int = 10) -> tuple[list[Post], int, int]:
    total_pages = max(1, (len(posts) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    return posts[start : start + per_page], page, total_pages


def _render(body: str) -> str:
    _MD.reset()
    return _MD.convert(body)


def _as_date(value: object) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
