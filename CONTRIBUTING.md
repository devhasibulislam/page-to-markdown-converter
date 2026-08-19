# Contributing

Thanks for helping. Quick rules:

## Dev setup

```bash
uv sync                                # Python deps
pre-commit install                     # ruff + mypy + pytest on commit
cd extension && pnpm install && cd ..  # Extension deps
```

## Run

```bash
docker compose up redis                # Redis for async jobs
uvicorn app.main:app --reload          # Backend + site
celery -A app.tasks worker --loglevel=info   # Job worker
```

## Test

```bash
pytest                                 # All
pytest tests/test_extraction.py::test_x  # One
cd extension && pnpm test              # Extension tests
```

## Conventions

- Read [`.github/copilot-instructions.md`](.github/copilot-instructions.md) first.
- Language-specific rules: [`.github/instructions/`](.github/instructions/).
- Comments: only when the code can't show it, one line where possible.
- No new dependencies without an ADR in [`docs/decisions/`](docs/decisions/).
- Every architectural change gets an ADR.

## PR checklist

- [ ] `ruff check .` clean
- [ ] `mypy app/` clean
- [ ] `pytest` passes
- [ ] Docs updated if behavior changed
- [ ] ADR added if a design decision was made

## Slash commands (Copilot)

- `/adr <title>` — new decision record
- `/blog <title>` — new blog post scaffold
- `/route <path>` — new FastAPI route + test
- `/extract-test <url>` — new extraction fixture
