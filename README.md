# page-to-markdown-converter

Turn any web page into clean Markdown. A browser extension captures the rendered
HTML, a Python backend extracts the main content, and you get the result three
ways: preview, download, or email.

Works on JavaScript-heavy SPAs, logged-in pages, and paywalled content — because
the extension uses your real browser session.

## Features

- Browser extension (Chrome / Edge / Firefox / Brave) captures rendered HTML
- Public API accepts either raw HTML (from the extension) or a URL (for testing)
- Three delivery methods: `inline` (preview), `download` (.md file), `email`
- Landing page has a try-it box that converts a URL right in the browser
- No headless browser on the server — the extension does the rendering work
- Blog and legal pages served from Markdown files in the repo

## Quick start

```bash
# Backend
uv sync
uvicorn app.main:app --reload

# Extension
cd extension && pnpm install && pnpm build
```

Open http://localhost:8000 for the site, http://localhost:8000/docs for Swagger.

## Docs

- [Architecture](docs/architecture.md)
- [API contract](docs/api.md)
- [Extension](docs/extension.md)
- [Deployment](docs/deployment.md)
- [Copilot setup](docs/copilot-setup.md)
- [Decisions (ADRs)](docs/decisions/)
- [Full plan](docs/planning/full-plan.md)

## License

MIT. See [LICENSE](LICENSE).
