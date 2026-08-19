"""GET /api/jobs/{id} and GET /api/download/{id}."""

from __future__ import annotations

from pathlib import Path as FsPath
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse

from app.config import get_settings
from app.jobs import get_job
from app.schemas import ApiError, JobStatusResponse

router = APIRouter(prefix="/api", tags=["Jobs"])
_settings = get_settings()


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Poll job status",
    description=(
        "Returns the current state of an async job created by `POST /api/convert` "
        "with `deliveryMethod=download` or `deliveryMethod=email`. Poll every few "
        "seconds until `status` is one of the terminal values: `ready`, `sent`, or "
        "`failed`.\n\n"
        "**Statuses:**\n"
        "- `queued`: waiting for a worker.\n"
        "- `processing`: worker is delivering the file or sending the email.\n"
        "- `ready`: download file written. Fetch it at `/api/download/{jobId}`. Kept 1 hour.\n"
        "- `sent`: email delivered successfully.\n"
        "- `failed`: something went wrong. `error` contains a short reason (for example `smtp_failed`)."
    ),
    responses={
        200: {"description": "Job state returned."},
        404: {"model": ApiError, "description": "Unknown or expired `jobId`."},
    },
)
def get_job_status(
    job_id: Annotated[
        str,
        Path(
            description="Opaque job identifier returned by `POST /api/convert` when `deliveryMethod` is `download` or `email`.",
            examples=["8f3c9a2e4d1b4f7a9c2e1a8b5d6c7e0f"],
        ),
    ],
) -> JobStatusResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(404, ApiError(error="job_not_found", message="No such job.").model_dump())
    return JobStatusResponse(
        status=job.get("status", "queued"),
        download_url=job.get("downloadUrl"),
        error=job.get("error"),
    )


@router.get(
    "/download/{job_id}",
    summary="Download a converted .md file",
    description=(
        "Serves the Markdown file produced by a `deliveryMethod=download` job. "
        "The response is `Content-Disposition: attachment`, so browsers save it "
        "instead of rendering. The file is available for 1 hour after the job "
        "reaches `ready`, then deleted."
    ),
    responses={
        200: {"description": "The `.md` file is served as an attachment.", "content": {"text/markdown": {}}},
        404: {"model": ApiError, "description": "Job not found, not ready yet, or the file has expired."},
    },
)
def download(
    job_id: Annotated[
        str,
        Path(
            description="Job identifier from a `download` delivery. The job status must be `ready` for the file to be served.",
            examples=["8f3c9a2e4d1b4f7a9c2e1a8b5d6c7e0f"],
        ),
    ],
) -> FileResponse:
    job = get_job(job_id)
    if job is None or job.get("status") != "ready":
        raise HTTPException(404, ApiError(error="not_ready", message="File not ready or expired.").model_dump())

    path: FsPath = _settings.job_dir / f"{job_id}.md"
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
