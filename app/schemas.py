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

    html: str | None = None
    url: str | None = None
    source_url: str | None = Field(default=None, alias="sourceUrl")
    delivery_method: DeliveryMethod = Field(default="inline", alias="deliveryMethod")
    email: EmailStr | None = None

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
    model_config = ConfigDict(populate_by_name=True)

    source_url: str = Field(alias="sourceUrl")
    title: str
    markdown: str
    word_count: int = Field(alias="wordCount")
    extracted_at: datetime = Field(alias="extractedAt")


class JobResponse(BaseModel):
    job_id: str = Field(alias="jobId")

    model_config = ConfigDict(populate_by_name=True)


class JobStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: JobStatus
    download_url: str | None = Field(default=None, alias="downloadUrl")
    error: str | None = None


class ApiError(BaseModel):
    error: str
    message: str
