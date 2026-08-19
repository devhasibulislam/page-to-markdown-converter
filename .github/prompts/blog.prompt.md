---
description: "Scaffold a new blog post in app/content/blog/ with correct frontmatter."
---

Create a new blog post at `app/content/blog/YYYY-MM-DD-<slug>.md`.

Steps:

1. Take title from `${input:title}` or ask the user.
2. Use today's date (YYYY-MM-DD).
3. Slugify the title.
4. Create the file with this frontmatter (see [`.github/instructions/content.instructions.md`](../instructions/content.instructions.md)):

```markdown
---
title: "<Title in sentence case>"
slug: "<slug>"
date: <YYYY-MM-DD>
author: "<Author name, ask if unknown>"
excerpt: "<One-sentence summary, ask user>"
tags: []
---

<Body starts here. Standard Markdown only.>
```

5. Leave a `<!-- TODO: write body -->` marker in the body.
6. Do not commit; the user reviews first.
