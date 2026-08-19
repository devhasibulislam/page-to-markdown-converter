---
description: "Add a URL to the extraction test fixtures: snapshot HTML + expected markdown."
---

Add a new extraction fixture.

Input: `${input:url}`.

Steps:

1. Slugify the URL host + path → `<slug>` (e.g. `en-wikipedia-org-wiki-markdown`).
2. Fetch the URL with `httpx.get(url, follow_redirects=True, timeout=10)`.
3. Save the raw HTML to `tests/fixtures/extraction/<slug>.html`.
4. Run `app.extraction.extract(html, source_url=url)` and save the resulting
   markdown to `tests/fixtures/extraction/<slug>.expected.md`.
5. Add a parametrized test case to `tests/test_extraction.py`:

```python
@pytest.mark.parametrize("slug", [..., "<slug>"])
def test_extraction_fixture(slug: str) -> None:
    html = (FIXTURES / f"{slug}.html").read_text()
    expected = (FIXTURES / f"{slug}.expected.md").read_text()
    assert extract(html, source_url="...").markdown.strip() == expected.strip()
```

6. Verify the fixture manually (does the markdown look clean?) before
   committing. Only commit when the extraction quality passes the checklist
   in [`skills/extraction-quality/SKILL.md`](../../skills/extraction-quality/SKILL.md).
