---
applyTo: "app/content/**/*.md"
---

# Content conventions (blog + legal)

## Blog frontmatter (required)

```yaml
---
title: "Post title in sentence case"
slug: "url-safe-slug"
date: 2026-08-19
author: "Name"
excerpt: "One-sentence summary shown on the list page."
tags: [tag-one, tag-two]
---
```

- **Filename**: `YYYY-MM-DD-<slug>.md`
- **Slug** matches the filename slug and the URL path (`/blog/<slug>`).
- **Date** is ISO (YYYY-MM-DD), no time.
- **Excerpt** under 160 chars.

## Legal frontmatter

```yaml
---
title: "Privacy policy"
updated: 2026-08-19
---
```

## Body rules

- Standard Markdown only. No custom shortcodes, no MDX.
- Images live in `app/static/img/blog/<slug>/`. Reference with absolute paths (`/static/img/blog/...`).
- External links open in new tab: `[text](https://... "title"){:target="_blank"}` — handled by post-processor, don't add manually.
- Code blocks use fenced syntax with language: ` ```python `.
- No inline HTML except when Markdown can't express it.
