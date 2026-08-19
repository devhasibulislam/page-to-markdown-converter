---
description: "Scaffold a new FastAPI route module, its test file, and register it in main.py."
---

Create a new FastAPI route.

Input: `${input:path}` (e.g. `admin/stats`).

Steps:

1. Derive a Python module name from the path (`admin_stats` → `app/routes/admin_stats.py`).
2. Create the route module:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/<path>", tags=["<tag>"])


@router.get("")
async def handler() -> dict[str, str]:
    return {"status": "ok"}
```

3. Register the router in `app/main.py`:

```python
from app.routes import <new_module>
app.include_router(<new_module>.router)
```

4. Create a matching test file at `tests/test_<module>.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_<name>_returns_ok() -> None:
    response = client.get("/api/<path>")
    assert response.status_code == 200
```

5. Do not commit. Ask the user to review.
