"""Pydantic v2 request/response models for the API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

DeliveryMethod = Literal["inline", "download", "email"]
JobStatus = Literal["queued", "processing", "ready", "sent", "failed"]


class ConvertRequest(BaseModel):
    """Body for POST /api/convert. Exactly one of html/url is required."""

    model_config = ConfigDict(extra="forbid")

    html: str | None = Field(
        default=None,
        description="Raw outerHTML captured by the browser extension. Use this OR `url`, not both. Max 10 MB.",
    )
    url: str | None = Field(
        default=None,
        description="Public URL to fetch and convert. Use this OR `html`, not both. Server truncates fetched HTML at 5 MB.",
    )
    source_url: str | None = Field(
        default=None,
        alias="sourceUrl",
        description="Origin URL. Used to resolve relative links and images in the output. Defaults to `url` when the URL path is used.",
    )
    delivery_method: DeliveryMethod = Field(
        default="inline",
        alias="deliveryMethod",
        description="How to deliver the result: `inline` returns Markdown in the response, `download` writes a .md file (fetched via /api/download/{jobId}), `email` sends it as an attachment.",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Recipient address. Required when `deliveryMethod` is `email`; ignored otherwise.",
    )

    @model_validator(mode="after")
    def _validate_inputs(self) -> ConvertRequest:
        if bool(self.html) == bool(self.url):
            raise ValueError("missing_input")
        if self.delivery_method == "email" and not self.email:
            raise ValueError("email_required")
        if self.url and not self.source_url:
            self.source_url = self.url
        return self


class InlineResponse(BaseModel):
    """Successful inline conversion (HTTP 200)."""

    model_config = ConfigDict(populate_by_name=True)

    source_url: str = Field(alias="sourceUrl", description="Origin URL that was converted.")
    title: str = Field(description="Page title extracted from the HTML.")
    markdown: str = Field(description="Extracted main content as Markdown.")
    word_count: int = Field(alias="wordCount", description="Number of words in the extracted Markdown.")
    extracted_at: datetime = Field(alias="extractedAt", description="Server timestamp when extraction completed (UTC).")


class JobResponse(BaseModel):
    """Async delivery queued (HTTP 202). Poll /api/jobs/{jobId} for status."""

    job_id: str = Field(alias="jobId", description="Opaque job identifier. Use it with /api/jobs/{jobId} and /api/download/{jobId}.")

    model_config = ConfigDict(populate_by_name=True)


class JobStatusResponse(BaseModel):
    """Current state of an async job."""

    model_config = ConfigDict(populate_by_name=True)

    status: JobStatus = Field(
        description="One of: `queued`, `processing`, `ready` (download path), `sent` (email path), `failed`."
    )
    download_url: str | None = Field(
        default=None,
        alias="downloadUrl",
        description="Populated only when `status=ready`. Relative path to fetch the .md file.",
    )
    error: str | None = Field(default=None, description="Short reason string when `status=failed`.")


class ApiError(BaseModel):
    """Standard error shape for 4xx responses."""

    error: str = Field(description="Machine-readable error code (e.g. `missing_input`).")
    message: str = Field(description="Human-readable explanation for the error.")
