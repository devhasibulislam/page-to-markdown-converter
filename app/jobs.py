"""Job state stored in Redis. Keys namespaced by REDIS_KEY_PREFIX."""

from __future__ import annotations

import json
from typing import Any

import redis

from app.config import get_settings

_settings = get_settings()
_client: redis.Redis | None = None


def client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis.from_url(_settings.redis_url, decode_responses=True)
    return _client


def _key(job_id: str) -> str:
    return f"{_settings.redis_key_prefix}:job:{job_id}"


def set_job(job_id: str, data: dict[str, Any]) -> None:
    client().set(_key(job_id), json.dumps(data), ex=86400)


def get_job(job_id: str) -> dict[str, Any] | None:
    raw = client().get(_key(job_id))
    return json.loads(raw) if raw else None


def update_job(job_id: str, **fields: Any) -> None:
    existing = get_job(job_id) or {}
    existing.update(fields)
    set_job(job_id, existing)
