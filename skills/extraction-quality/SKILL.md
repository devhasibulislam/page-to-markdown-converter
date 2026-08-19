---
name: extraction-quality
description: Checklist for adding a new URL to the extraction test fixtures. Use when adding a fixture, when a user reports poor extraction, or when reviewing extraction changes.
---

# extraction-quality skill

## When to use

Whenever you add a new URL to the extraction test fixtures, or when a real
user reports that a page extracts poorly. Follow this checklist before
committing the fixture.

## Coverage

The fixture suite should cover at least these page types:

1. **News article** (e.g. BBC, NYT, Guardian)
2. **Long-form blog post** (e.g. Substack, Medium)
3. **Technical documentation** (e.g. MDN, Python docs, framework guide)
4. **SPA-heavy site** (e.g. React app, dashboard)
5. **Wikipedia article** (the boring baseline)
6. **Paywalled article** (extension-only, but keep an HTML snapshot)

When adding a new fixture, check which category is under-represented.

## Quality check

For each fixture, open the resulting `.expected.md` and verify:

- [ ] Title captured, matches the visible page title
- [ ] Body text present, in reading order
- [ ] No navigation, sidebar, or footer content leaked in
- [ ] No cookie banner text, no "subscribe" prompts, no comments section
- [ ] Links preserved with absolute URLs (relative → resolved against source URL)
- [ ] Images preserved with absolute URLs and `alt` text where the page had it
- [ ] Code blocks (if any) preserved with correct fencing
- [ ] Headings preserved with correct level (`#`, `##`, `###`)
- [ ] Lists preserved (both ordered and unordered)
- [ ] No trailing whitespace, no double blank lines, no HTML entities in text

## Reject the fixture if

- The main content is missing or truncated
- More than a paragraph of non-content leaked in (nav, ads, related posts)
- The fallback (readability-lxml) was needed and its output is worse than trafilatura's would have been on a fixed version

## Signal-to-noise threshold

Word count of extracted markdown / word count of visible article should be
between 0.8 and 1.15. Below 0.8: content missing. Above 1.15: noise leaked in.
