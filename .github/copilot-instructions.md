# Copilot instructions — page-to-markdown-converter

Auto-loaded on every chat in this repo. Keep this file the single source of truth
for how any agent should work here.

## What this is

A browser extension captures rendered HTML from any page and sends it to a
Python backend. The backend extracts the main content, converts to Markdown, and
delivers it inline, as a downloadable `.md` file, or as an email attachment.

## Stack

- **Backend + site**: FastAPI, Uvicorn, Jinja2, Bootstrap 5 (local, no CDN)
- **Extraction**: trafilatura (primary), readability-lxml + markdownify (fallback)
- **URL fetch**: httpx (plain GET, no headless browser)
- **Queue**: Celery + Redis (for `download` and `email` delivery)
- **Email**: SMTP via smtplib
- **Content**: python-frontmatter + `markdown` package for blog and legal pages
- **Rate limiting**: slowapi
- **Extension**: TypeScript, Manifest V3

## Golden rules

1. **The extension path never triggers a server-side fetch.** If `html` is present
   in a request, use it. Only fetch when `url` is the only input.
2. **No headless browser server-side, ever.** URL fetches are plain `httpx.get`.
   If a page needs JavaScript to render, return `422 js_rendered_page_use_extension`.
3. **Extraction pipeline is fixed**: trafilatura first, readability-lxml +
   markdownify fallback only if the first pass is thin.
4. **Blog and legal are Markdown files in `app/content/`.** No CMS, no database
   for content.
5. **No analytics, no cookies, no tracking scripts** in v1.
6. **No new dependencies without an ADR** in `docs/decisions/`.
7. **Comments only when the code can't show it**, one line where possible.

## Commands

```bash
uv sync                                        # install
uvicorn app.main:app --reload                  # run backend + site
celery -A app.tasks worker --loglevel=info     # run job worker
docker compose up redis                        # run redis

pytest                                         # all tests
pytest tests/test_extraction.py::test_name     # one test
ruff check --fix . && ruff format .            # lint + format
mypy app/                                      # type check

cd extension && pnpm install && pnpm build     # build extension
zip -r dist/extension.zip extension/dist/*     # package for release
```

## Repo map

```
app/
├── main.py               FastAPI app entry, mounts static, registers routes
├── schemas.py            Pydantic request/response models
├── fetcher.py            httpx URL fetcher, size + timeout guards
├── extraction.py         trafilatura + readability fallback
├── blog.py               Loads Markdown posts, pagination
├── tasks.py              Celery tasks (download, email)
├── routes/
│   ├── convert.py        POST /api/convert
│   ├── jobs.py           GET /api/jobs/{id}, /api/download/{id}
│   └── pages.py          Home, blog, legal, try-it
├── templates/            Jinja2 templates (Bootstrap 5)
├── static/               Local Bootstrap, site CSS, videos, favicon
└── content/
    ├── blog/*.md         Blog posts with YAML frontmatter
    └── legal/*.md        Privacy, terms, cookies

extension/                TypeScript MV3 source
dist/extension.zip        Built extension for /download/extension.zip
docs/                     Architecture, API, ADRs, planning
tests/                    Pytest + extraction fixtures
hooks/                    Pre-commit + pre-push scripts
```

## Do not touch

- `app/static/css/bootstrap.min.css` and `app/static/js/bootstrap.bundle.min.js` — vendored
- `dist/` — build output
- `extension/dist/` — build output
- `app/content/` content files unless the task is explicitly to add or edit a post

## Conventions (summary — details in scoped instructions)

- Python: PEP 8 via ruff, type hints on all public functions, Pydantic v2 models
  in `schemas.py`, route handlers thin (delegate to service functions), no bare
  `except`, log with `logging`, never `print`. See
  [`instructions/python.instructions.md`](instructions/python.instructions.md).
- TypeScript: strict mode, no `any`, `chrome.*` APIs (not `browser.*`), gzip
  payload before POST. See
  [`instructions/typescript.instructions.md`](instructions/typescript.instructions.md).
- Templates: Bootstrap 5 classes only, no inline styles, escape user content,
  no CDN. See [`instructions/templates.instructions.md`](instructions/templates.instructions.md).
- Content: YAML frontmatter shape fixed. See
  [`instructions/content.instructions.md`](instructions/content.instructions.md).

## Slash commands (in `.github/prompts/`)

- `/adr <title>` — new decision record with next sequential number
- `/blog <title>` — new blog post scaffold with correct frontmatter
- `/route <path>` — new FastAPI route + test file + registration
- `/extract-test <url>` — new extraction fixture (HTML snapshot + golden markdown)

## Chat modes (in `.github/chatmodes/`)

- **Plan** — research anywhere (web, terminal, SSH, curl), never edits files
- **Review** — read-only code review: over-engineering, reusability, industry
  practices. Loads the ponytail-review skill.

## MCP servers (in `.vscode/mcp.json`)

- **GitHub** — issues, PRs, releases
- **Playwright** — extension E2E, recording install videos

## Hooks (in `hooks/`)

- **pre-commit**: `ruff check --fix`, `ruff format`, `mypy app/`, `pytest -x --ff`
- **pre-push**: full `pytest` + `pnpm --dir extension test`

## Installed skills (in `.agents/skills/`)

Managed by `npx skills`. Copilot-scoped, project-local.

- `tdd`, `improve-codebase-architecture` — mattpocock
- `code-review-excellence`, `python-testing-patterns`, `python-type-safety`, `async-python-patterns` — wshobson
- `fastapi` — official FastAPI skill
- `multi-stage-dockerfile` — github/awesome-copilot
- `extraction-quality` — local, project-specific

Update with `npx skills update`. Add more with `npx skills add <pkg> -a github-copilot -y`.

## Autonomous / auto-approve

`.vscode/settings.json` keeps `run_in_terminal` off the auto-approve list. Every
shell command needs an explicit confirm dialog. Do not add write-capable tools to
the auto-approve list without a discussion.

## Full plan and decisions

- Full plan: [`docs/planning/full-plan.md`](../docs/planning/full-plan.md)
- Decisions (ADRs): [`docs/decisions/`](../docs/decisions/)
- Copilot setup rationale: [`docs/copilot-setup.md`](../docs/copilot-setup.md)

## When adding a new convention

Add a pointer line to this file. If it isn't referenced here, agents will not
discover it.
