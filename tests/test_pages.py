from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_home_renders(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"MarkDrop" in response.content
    assert b"Turn any web page into clean Markdown" in response.content
    assert b"Chrome" in response.content
    assert b"Vivaldi" in response.content


def test_home_has_seven_browser_tabs(client: TestClient) -> None:
    response = client.get("/")
    for name in (b"Chrome", b"Edge", b"Firefox", b"Brave", b"Opera", b"Arc", b"Vivaldi"):
        assert name in response.content


def test_blog_list_renders(client: TestClient) -> None:
    response = client.get("/blog")
    assert response.status_code == 200
    assert b"Welcome to MarkDrop" in response.content


def test_blog_post_renders(client: TestClient) -> None:
    response = client.get("/blog/welcome-to-markdrop")
    assert response.status_code == 200
    assert b"Welcome to MarkDrop" in response.content
    assert b"trafilatura" in response.content


def test_blog_post_404(client: TestClient) -> None:
    response = client.get("/blog/nope")
    assert response.status_code == 404


def test_legal_pages_render(client: TestClient) -> None:
    for slug in ("privacy", "terms", "cookies"):
        response = client.get(f"/legal/{slug}")
        assert response.status_code == 200, slug


def test_download_extension_zip_404_when_not_built(client: TestClient) -> None:
    response = client.get("/download/extension.zip")
    assert response.status_code == 404


def test_static_bootstrap_served(client: TestClient) -> None:
    response = client.get("/static/css/bootstrap.min.css")
    assert response.status_code == 200
    assert b".navbar" in response.content
