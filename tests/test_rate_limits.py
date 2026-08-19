"""Rate-limit smoke test: 11th /try POST within a minute should get 429."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def fresh_client() -> TestClient:
    # Reset the in-memory limiter state so this test doesn't interact with others.
    app.state.limiter.reset()
    with TestClient(app) as c:
        yield c
    app.state.limiter.reset()


def test_try_form_rate_limited_at_ten_per_minute(fresh_client: TestClient) -> None:
    # slowapi's default in-memory storage keys by IP, and TestClient uses testclient as the host.
    for i in range(10):
        response = fresh_client.post("/try", data={"url": "https://en.wikipedia.org/wiki/Markdown"})
        assert response.status_code in (200, 422), f"request {i} unexpectedly failed"

    response = fresh_client.post("/try", data={"url": "https://en.wikipedia.org/wiki/Markdown"})
    assert response.status_code == 429
