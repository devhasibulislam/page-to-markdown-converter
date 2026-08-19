"""Celery tasks: delivery only. Extraction runs in the request handler so
the client gets immediate feedback on unreadable pages."""

from __future__ import annotations

import logging

from celery import Celery

from app.config import get_settings
from app.email_sender import send_markdown
from app.jobs import update_job

log = logging.getLogger(__name__)
_settings = get_settings()

celery_app = Celery("page_to_md", broker=_settings.redis_url, backend=_settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_time_limit=60,
    task_soft_time_limit=45,
)


@celery_app.task(bind=True, max_retries=1, default_retry_delay=10)
def process_conversion(  # type: ignore[no-untyped-def]
    self,
    *,
    job_id: str,
    title: str,
    markdown: str,
    source_url: str | None,
    delivery: str,
    email: str | None,
) -> None:
    update_job(job_id, status="processing")

    if delivery == "download":
        _settings.job_dir.mkdir(parents=True, exist_ok=True)
        (_settings.job_dir / f"{job_id}.md").write_text(markdown, encoding="utf-8")
        update_job(job_id, status="ready", downloadUrl=f"/api/download/{job_id}", title=title)
        return

    if delivery == "email":
        assert email is not None
        filename = _safe_filename(title or "page") + ".md"
        body = f"Attached is the Markdown for: {source_url or ''}\n\n— Page to Markdown"
        try:
            send_markdown(
                to=email,
                subject=title or "Your converted page",
                body=body,
                attachment=markdown,
                filename=filename,
            )
        except Exception as exc:
            log.exception("email send failed")
            try:
                raise self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                update_job(job_id, status="failed", error=f"smtp_failed: {exc}")
                return
        update_job(job_id, status="sent")


def _safe_filename(name: str) -> str:
    cleaned = "".join(c if c.isalnum() or c in "-_." else "-" for c in name).strip("-")
    return (cleaned or "page")[:80]
