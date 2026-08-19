"""GET /api/jobs/{id} and GET /api/download/{id}."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import get_settings
from app.jobs import get_job
from app.schemas import ApiError, JobStatusResponse

router = APIRouter(prefix="/api", tags=["jobs"])
_settings = get_settings()


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    responses={404: {"model": ApiError}},
)
def get_job_status(job_id: str) -> JobStatusResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(404, ApiError(error="job_not_found", message="No such job.").model_dump())
    return JobStatusResponse(
        status=job.get("status", "queued"),
        download_url=job.get("downloadUrl"),
        error=job.get("error"),
    )


@router.get("/download/{job_id}", responses={404: {"model": ApiError}})
def download(job_id: str) -> FileResponse:
    job = get_job(job_id)
    if job is None or job.get("status") != "ready":
        raise HTTPException(404, ApiError(error="not_ready", message="File not ready or expired.").model_dump())

    path: Path = _settings.job_dir / f"{job_id}.md"
    if not path.exists():
        raise HTTPException(404, ApiError(error="not_ready", message="File missing or expired.").model_dump())

    filename = _settings.job_dir / f"{job_id}.md"
    display = (job.get("title") or "page").strip() or "page"
    display = "".join(c if c.isalnum() or c in "-_." else "-" for c in display).strip("-") or "page"
    return FileResponse(
        path=filename,
        media_type="text/markdown",
        filename=f"{display}.md",
    )
