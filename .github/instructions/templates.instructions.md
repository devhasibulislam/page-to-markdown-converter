---
applyTo: "app/templates/**/*.html"
---

# Template conventions

- **Bootstrap 5 classes only** for styling. No inline `style="..."` attributes.
- **Local Bootstrap**: use `{{ url_for('static', path='css/bootstrap.min.css') }}`, never a CDN.
- **Escape user content**: Jinja auto-escapes by default. Never mark user input `| safe`.
- **Semantic HTML**: `<main>`, `<article>`, `<nav>`, `<footer>`. Not everything is a `<div>`.
- **Accessibility**: `alt` on every `<img>`, labels on every form field, focus states visible.
- **No JavaScript except Bootstrap's bundle** in v1. If a page needs JS, write it in `app/static/js/site.js` and load it explicitly.
- **Template inheritance**: extend `base.html`. Blocks: `title`, `head_extra`, `content`, `scripts`.
