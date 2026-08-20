"""POST /api/convert — dual-input (html | url), three delivery methods."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import ValidationError

from app.extraction import ExtractionError, extract
from app.fetcher import FetchError, fetch
from app.jobs import set_job
from app.limits import limiter
from app.schemas import ApiError, ConvertRequest, InlineResponse, JobResponse
from app.tasks import process_conversion

router = APIRouter(prefix="/api", tags=["Convert"])


@router.post(
    "/convert",
    response_model=None,
    summary="Convert a page to Markdown",
    description=(
        "Extracts the main content of a web page and returns it as Markdown.\n\n"
        "**Provide exactly one of:**\n"
        "- `html`: the raw outerHTML of a page (used by the browser extension after "
        "the page has fully rendered).\n"
        "- `url`: a public URL that the server fetches with a plain HTTP GET.\n\n"
        "**Delivery methods (`deliveryMethod`):**\n"
        "- `inline` (default): the response body contains the Markdown.\n"
        "- `download`: returns 202 with a `jobId`. Poll `/api/jobs/{jobId}` until "
        "`status=ready`, then GET `/api/download/{jobId}`.\n"
        "- `email`: returns 202 with a `jobId`. A worker sends the .md file to the "
        "`email` address. Poll `/api/jobs/{jobId}` until `status=sent` or `failed`.\n\n"
        "Rate limit: 60 requests per minute per IP."
    ),
    responses={
        200: {
            "model": InlineResponse,
            "description": "Inline conversion complete. The Markdown is in the response body.",
        },
        202: {
            "model": JobResponse,
            "description": "Async delivery queued. Poll `/api/jobs/{jobId}` for status.",
        },
        422: {
            "model": ApiError,
            "description": (
                "Validation or extraction failure. Possible `error` values: "
                "`missing_input`, `email_required`, `no_readable_content`, "
                "`js_rendered_page_use_extension`, `fetch_failed`."
            ),
        },
        429: {
            "model": ApiError,
            "description": "Rate limit exceeded (over 60/minute for this IP).",
        },
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "url_inline": {
                            "summary": "URL, inline preview",
                            "description": "Simplest call. Server fetches the URL and returns Markdown in the response.",
                            "value": {
                                "url": "https://en.wikipedia.org/wiki/Markdown",
                                "deliveryMethod": "inline",
                            },
                        },
                        "html_inline": {
                            "summary": "HTML from extension, inline preview",
                            "description": (
                                "How the browser extension calls the endpoint. The extension "
                                "sends the already-rendered outerHTML so the server does not "
                                "have to fetch the page itself."
                            ),
                            "value": {
                                "html": "<html><body><article><h1>Hi</h1><p>Body text here with enough words to pass the minimum content threshold used by the extractor before it falls back to readability.</p></article></body></html>",
                                "sourceUrl": "https://example.com/post",
                                "deliveryMethod": "inline",
                            },
                        },
                        "url_download": {
                            "summary": "URL, async .md download",
                            "description": (
                                "Returns 202 with a jobId. Poll /api/jobs/{jobId} until "
                                "status=ready, then GET /api/download/{jobId} for the file."
                            ),
                            "value": {
                                "url": "https://en.wikipedia.org/wiki/Markdown",
                                "deliveryMethod": "download",
                            },
                        },
                        "url_email": {
                            "summary": "URL, delivered by email",
                            "description": (
                                "Returns 202 with a jobId. A Celery worker converts the page "
                                "and emails the .md file as an attachment."
                            ),
                            "value": {
                                "url": "https://en.wikipedia.org/wiki/Markdown",
                                "deliveryMethod": "email",
                                "email": "reader@example.com",
                            },
                        },
                    }
                }
            }
        }
    },
)
@limiter.limit("60/minute")
async def convert(
    request: Request,
    payload: dict,
    response: Response,
) -> InlineResponse | JobResponse:
    """Convert a web page to Markdown.

    See the endpoint summary for the full contract. The handler performs
    extraction synchronously so the client learns about unreadable content
    immediately; async delivery (download or email) only defers the *delivery*
    step, not the extraction.
    """
    try:
        parsed = ConvertRequest.model_validate(payload)
    except ValidationError as exc:
        raise _map_validation_error(exc) from exc

    html = parsed.html
    fetched_from_url = html is None
    if fetched_from_url:
        assert parsed.url is not None
        try:
            html = await fetch(parsed.url)
        except FetchError as exc:
            raise HTTPException(422, ApiError(error=str(exc), message="Failed to fetch URL.").model_dump()) from exc

    try:
        result = extract(html, source_url=parsed.source_url)
    except ExtractionError:
        code = "js_rendered_page_use_extension" if fetched_from_url else "no_readable_content"
        message = (
            "This page needs a real browser to render. Install the extension and try from the page directly."
            if fetched_from_url
            else "No extractable article content found on this page."
        )
        raise HTTPException(422, ApiError(error=code, message=message).model_dump()) from None

    if parsed.delivery_method == "inline":
        return InlineResponse(
            source_url=parsed.source_url or "",
            title=result.title,
            markdown=result.markdown,
            word_count=result.word_count,
            extracted_at=datetime.now(UTC),
        )

    # Extraction is already done; the worker only handles delivery.
    job_id = uuid.uuid4().hex
    set_job(job_id, {"status": "queued", "title": result.title})
    process_conversion.delay(
        job_id=job_id,
        title=result.title,
        markdown=result.markdown,
        source_url=parsed.source_url,
        delivery=parsed.delivery_method,
        email=parsed.email,
    )
    response.status_code = status.HTTP_202_ACCEPTED
    return JobResponse(job_id=job_id)


def _map_validation_error(exc: ValidationError) -> HTTPException:
    for err in exc.errors():
        raw = err.get("ctx", {}).get("error") or err.get("msg", "")
        text = str(raw)
        if "missing_input" in text:
            return HTTPException(
                422,
                ApiError(error="missing_input", message="Provide either 'html' or 'url'.").model_dump(),
            )
        if "email_required" in text:
            return HTTPException(
                422,
                ApiError(error="email_required", message="Email delivery requires an 'email' field.").model_dump(),
            )
    return HTTPException(422, ApiError(error="invalid_request", message=exc.errors()[0]["msg"]).model_dump())
