---
applyTo: "app/**/*.py"
---

# Python conventions

- **Type hints** on every public function and every Pydantic field.
- **Pydantic v2** models live in `app/schemas.py`. Use `model_config = ConfigDict(...)` when needed, never the v1 `class Config`.
- **Route handlers stay thin**: parse input, call a service function, shape the response. Business logic goes in dedicated modules (`extraction.py`, `fetcher.py`, `blog.py`, `tasks.py`).
- **HTTP client**: `httpx.AsyncClient` in async paths, `httpx.Client` only in Celery tasks. Never `requests`.
- **Logging**: use `logging.getLogger(__name__)`. Never `print`.
- **Errors**: raise specific `HTTPException` from routes. Never bare `except:`. Only catch what you can handle.
- **Async correctness**: never block the event loop with sync I/O in a route handler. If it's CPU-bound (extraction), it goes through Celery.
- **Validation at boundaries only**: Pydantic validates at the API boundary. Internal functions trust their arguments (they have type hints).
- **Imports**: sorted by ruff (`I` rule). No wildcard imports.
- **Naming**: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE` for constants. No abbreviations except widely-known ones (`html`, `url`).
- **Docstrings** on public API functions and non-obvious modules. One line where possible. Skip on trivial internal helpers.
- **Comments** only when the code can't show it. Never restate what the next line does.
- **Testing**: one behavior per test. Use `pytest.mark.parametrize` for multi-case. Fixtures in `conftest.py`.
