"""Site pages: home, try-it form, blog list, single post, legal, extension download."""

from __future__ import annotations

from pathlib import Path as FsPath
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Path, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app import blog
from app.extraction import ExtractionError, extract
from app.fetcher import FetchError, fetch
from app.limits import limiter

_BROWSERS = [
    ("chrome", "Chrome", "google-chrome.webp"),
    ("edge", "Edge", "microsoft-edge.webp"),
    ("firefox", "Firefox", "firefox.webp"),
    ("brave", "Brave", "brave.webp"),
    ("opera", "Opera", "opera.webp"),
    ("arc", "Arc", "arc-search.webp"),
    ("vivaldi", "Vivaldi", "vivaldi.webp"),
]
_EXTENSION_ZIP = FsPath(__file__).resolve().parent.parent.parent / "dist" / "extension.zip"

router = APIRouter(tags=["Site"])
templates = Jinja2Templates(directory=str(FsPath(__file__).resolve().parent.parent / "templates"))


@router.get(
    "/",
    response_class=HTMLResponse,
    summary="Landing page",
    description="Marketing home page with the browser picker, install videos, and the try-it URL box. Renders HTML, not JSON.",
)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "home.html", {"browsers": _BROWSERS})


@router.post(
    "/try",
    response_class=HTMLResponse,
    summary="Try-it form submission (landing page)",
    description=(
        "Handles the URL form on the home page. Fetches the page server-side, "
        "extracts Markdown, and re-renders the home template with the result "
        "inline. Not intended for JSON clients; use `POST /api/convert` for that. "
        "Rate limit: 10 requests per minute per IP."
    ),
)
@limiter.limit("10/minute")
async def try_convert(
    request: Request,
    url: Annotated[
        str,
        Form(
            description="Public URL to convert. Server fetches it with a plain HTTP GET (10s timeout, 5 MB cap).",
            examples=["https://en.wikipedia.org/wiki/Markdown"],
        ),
    ],
) -> HTMLResponse:
    context: dict[str, object] = {"browsers": _BROWSERS, "try_url": url}
    try:
        html = await fetch(url)
        result = extract(html, source_url=url)
        context["try_result"] = result
    except FetchError as exc:
        context["try_error"] = f"Couldn't fetch that URL ({exc})."
    except ExtractionError:
        context["try_error"] = "This page needs a real browser to render. Install the extension and try from the page directly."
    return templates.TemplateResponse(request, "home.html", context)


@router.get(
    "/blog",
    response_class=HTMLResponse,
    summary="Blog index (paginated)",
    description="Lists blog posts, 10 per page. Use `?page=N` to navigate. Sourced from Markdown files under `app/content/blog/`.",
)
def blog_list(
    request: Request,
    page: Annotated[
        int,
        Query(
            ge=1,
            description="1-based page number. 10 posts per page, sorted by date descending.",
            examples=[1, 2, 3],
        ),
    ] = 1,
) -> HTMLResponse:
    posts, current, total = blog.paginate(blog.all_posts(), page)
    return templates.TemplateResponse(
        request,
        "blog_list.html",
        {"posts": posts, "page": current, "total_pages": total},
    )


@router.get(
    "/blog/{slug}",
    response_class=HTMLResponse,
    summary="Single blog post",
    description="Renders one blog post by its `slug` (matches the YAML frontmatter and the filename).",
)
def blog_post(
    request: Request,
    slug: Annotated[
        str,
        Path(
            description="Post slug, matching the `slug` in the YAML frontmatter (typically `kebab-case`).",
            examples=["welcome-to-markdrop"],
        ),
    ],
) -> HTMLResponse:
    post = blog.get_post(slug)
    if post is None:
        raise HTTPException(404, "post not found")
    return templates.TemplateResponse(request, "blog_post.html", {"post": post})


@router.get(
    "/legal/{slug}",
    response_class=HTMLResponse,
    summary="Legal page",
    description="Renders `privacy`, `terms`, or `cookies` from `app/content/legal/{slug}.md`.",
)
def legal_page(
    request: Request,
    slug: Annotated[
        str,
        Path(
            description="Legal page identifier. Must match a Markdown file in `app/content/legal/`.",
            examples=["privacy", "terms", "cookies"],
        ),
    ],
) -> HTMLResponse:
    page = blog.get_legal(slug)
    if page is None:
        raise HTTPException(404, "page not found")
    return templates.TemplateResponse(request, "legal.html", {"page": page})


@router.get(
    "/download/extension.zip",
    summary="Download the browser extension",
    description=(
        "Serves the packaged MarkDrop extension as a ZIP. Users unzip it and load "
        "it as an unpacked extension in Chrome, Edge, Firefox, Brave, Opera, Arc, "
        "or Vivaldi. Returns 404 if the extension has not been built yet "
        "(`cd extension && pnpm build && cd .. && (cd extension/dist && zip -qr "
        "../../dist/extension.zip .)`)."
    ),
    responses={
        200: {"description": "The extension ZIP.", "content": {"application/zip": {}}},
        404: {"description": "The `dist/extension.zip` file is missing."},
    },
)
def download_extension() -> FileResponse:
    if not _EXTENSION_ZIP.exists():
        raise HTTPException(404, "extension not built yet — run pnpm build in extension/")
    return FileResponse(
        _EXTENSION_ZIP,
        media_type="application/zip",
        filename="markdrop-extension.zip",
    )
