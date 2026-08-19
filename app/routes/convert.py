"""POST /api/convert — dual-input (html | url), three delivery methods."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.extraction import ExtractionError, extract
from app.fetcher import FetchError, fetch
from app.jobs import set_job
from app.schemas import ApiError, ConvertRequest, InlineResponse, JobResponse
from app.tasks import process_conversion

router = APIRouter(prefix="/api", tags=["convert"])


@router.post(
    "/convert",
    response_model=None,
    responses={
        200: {"model": InlineResponse},
        202: {"model": JobResponse},
        422: {"model": ApiError},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "url_inline": {
                            "summary": "URL, inline preview",
                            "value": {
                                "url": "https://en.wikipedia.org/wiki/Markdown",
                                "deliveryMethod": "inline",
                            },
                        },
                        "html_inline": {
                            "summary": "HTML from extension, inline preview",
                            "value": {
                                "html": "<html><body><article><h1>Hi</h1><p>Body text here.</p></article></body></html>",
                                "sourceUrl": "https://example.com/post",
                                "deliveryMethod": "inline",
                            },
                        },
                        "url_email": {
                            "summary": "URL, delivered by email",
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
async def convert(payload: dict) -> InlineResponse | JobResponse:
    try:
        request = ConvertRequest.model_validate(payload)
    except ValidationError as exc:
        raise _map_validation_error(exc) from exc

    html = request.html
    fetched_from_url = html is None
    if fetched_from_url:
        assert request.url is not None
        try:
            html = await fetch(request.url)
        except FetchError as exc:
            raise HTTPException(422, ApiError(error=str(exc), message="Failed to fetch URL.").model_dump()) from exc

    try:
        result = extract(html, source_url=request.source_url)
    except ExtractionError:
        code = "js_rendered_page_use_extension" if fetched_from_url else "no_readable_content"
        message = (
            "This page needs a real browser to render. Install the extension and try from the page directly."
            if fetched_from_url
            else "No extractable article content found on this page."
        )
        raise HTTPException(422, ApiError(error=code, message=message).model_dump()) from None

    if request.delivery_method == "inline":
        return InlineResponse(
            source_url=request.source_url or "",
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
        source_url=request.source_url,
        delivery=request.delivery_method,
        email=request.email,
    )
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
