"""Site pages: home, try-it form, blog list, single post, legal, extension download."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app import blog
from app.extraction import ExtractionError, extract
from app.fetcher import FetchError, fetch

_BROWSERS = [
    ("chrome", "Chrome", "google-chrome.webp"),
    ("edge", "Edge", "microsoft-edge.webp"),
    ("firefox", "Firefox", "firefox.webp"),
    ("brave", "Brave", "brave.webp"),
    ("opera", "Opera", "opera.webp"),
    ("arc", "Arc", "arc-search.webp"),
    ("vivaldi", "Vivaldi", "vivaldi.webp"),
]
_EXTENSION_ZIP = Path(__file__).resolve().parent.parent.parent / "dist" / "extension.zip"

router = APIRouter(tags=["site"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "home.html", {"browsers": _BROWSERS})


@router.post("/try", response_class=HTMLResponse)
async def try_convert(request: Request, url: str = Form(...)) -> HTMLResponse:
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


@router.get("/blog", response_class=HTMLResponse)
def blog_list(request: Request, page: int = Query(default=1, ge=1)) -> HTMLResponse:
    posts, current, total = blog.paginate(blog.all_posts(), page)
    return templates.TemplateResponse(
        request,
        "blog_list.html",
        {"posts": posts, "page": current, "total_pages": total},
    )


@router.get("/blog/{slug}", response_class=HTMLResponse)
def blog_post(request: Request, slug: str) -> HTMLResponse:
    post = blog.get_post(slug)
    if post is None:
        raise HTTPException(404, "post not found")
    return templates.TemplateResponse(request, "blog_post.html", {"post": post})


@router.get("/legal/{slug}", response_class=HTMLResponse)
def legal_page(request: Request, slug: str) -> HTMLResponse:
    page = blog.get_legal(slug)
    if page is None:
        raise HTTPException(404, "page not found")
    return templates.TemplateResponse(request, "legal.html", {"page": page})


@router.get("/download/extension.zip")
def download_extension() -> FileResponse:
    if not _EXTENSION_ZIP.exists():
        raise HTTPException(404, "extension not built yet — run pnpm build in extension/")
    return FileResponse(
        _EXTENSION_ZIP,
        media_type="application/zip",
        filename="markdrop-extension.zip",
    )
