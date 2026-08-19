from __future__ import annotations

import pytest

from app.extraction import ExtractionError, extract, strip_scripts_and_styles

SAMPLE_ARTICLE = """
<!DOCTYPE html>
<html>
  <head>
    <title>Test article</title>
    <script>console.log("nope")</script>
    <style>.x{color:red}</style>
  </head>
  <body>
    <nav>Home | About</nav>
    <article>
      <h1>The joy of Markdown</h1>
      <p>Markdown is a lightweight markup language that people use to write
      formatted text using a plain-text editor. It has become the default
      format for README files, forum posts, and static site generators.</p>
      <p>The syntax was created by John Gruber in 2004 with the goal of being
      readable as-is, without the visual clutter of HTML tags. Anyone can pick
      it up in an afternoon.</p>
      <p>Today many flavors exist including CommonMark and GitHub Flavored
      Markdown, each adding useful extensions to the original spec.</p>
      <a href="/wiki/CommonMark">CommonMark</a>
    </article>
    <footer>Copyright</footer>
  </body>
</html>
"""


def test_strip_scripts_and_styles_removes_both() -> None:
    stripped = strip_scripts_and_styles(SAMPLE_ARTICLE)
    assert "console.log" not in stripped
    assert "color:red" not in stripped


def test_extract_returns_title_and_body() -> None:
    result = extract(SAMPLE_ARTICLE, source_url="https://example.com/wiki/Markdown")
    assert result.title == "Test article"
    assert "lightweight markup language" in result.markdown
    assert result.word_count > 30


def test_extract_resolves_relative_links() -> None:
    result = extract(SAMPLE_ARTICLE, source_url="https://example.com/wiki/Markdown")
    assert "https://example.com/wiki/CommonMark" in result.markdown


def test_extract_raises_on_empty_content() -> None:
    with pytest.raises(ExtractionError):
        extract("<html><body></body></html>")
