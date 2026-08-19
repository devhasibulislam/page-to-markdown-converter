from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


HTML_SAMPLE = """
<html><head><title>Sample</title></head><body>
<article><h1>Sample</h1>
<p>This is a sample article body with more than thirty words of content so that
the extractor considers it real content and returns markdown instead of raising
no_readable_content on us during tests, which would be a shame.</p>
</article></body></html>
"""


def test_convert_inline_html_returns_markdown() -> None:
    response = client.post(
        "/api/convert",
        json={
            "html": HTML_SAMPLE,
            "sourceUrl": "https://example.com/x",
            "deliveryMethod": "inline",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sourceUrl"] == "https://example.com/x"
    assert "sample article body" in body["markdown"].lower()
    assert body["wordCount"] > 0


def test_convert_missing_input_returns_422() -> None:
    response = client.post("/api/convert", json={"deliveryMethod": "inline"})
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == "missing_input"


def test_convert_both_inputs_returns_422() -> None:
    response = client.post(
        "/api/convert",
        json={"html": HTML_SAMPLE, "url": "https://example.com", "deliveryMethod": "inline"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == "missing_input"


def test_convert_email_without_address_returns_422() -> None:
    response = client.post(
        "/api/convert",
        json={"html": HTML_SAMPLE, "deliveryMethod": "email"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == "email_required"


def test_convert_no_readable_content_returns_422() -> None:
    response = client.post(
        "/api/convert",
        json={"html": "<html><body></body></html>", "sourceUrl": "https://x.com", "deliveryMethod": "inline"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["error"] == "no_readable_content"


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
