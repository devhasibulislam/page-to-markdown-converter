# Deployment

## Docker compose (recommended)

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      REDIS_URL: redis://redis:6379/0
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      SMTP_FROM: ${SMTP_FROM}
    depends_on: [redis]

  worker:
    build: .
    command: celery -A app.tasks worker --loglevel=info
    environment:
      REDIS_URL: redis://redis:6379/0
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      SMTP_FROM: ${SMTP_FROM}
    depends_on: [redis]
    volumes:
      - jobs:/tmp/jobs

  redis:
    image: redis:7-alpine
    volumes: [redis:/data]

volumes:
  jobs:
  redis:
```

`docker compose up -d --build` and put nginx or Caddy in front for TLS.

## Env vars

| Var               | Purpose                                          |
| ----------------- | ------------------------------------------------ |
| `REDIS_URL`       | Redis connection string                          |
| `SMTP_HOST`       | SMTP server host                                 |
| `SMTP_PORT`       | SMTP port (usually 587)                          |
| `SMTP_USER`       | SMTP username                                    |
| `SMTP_PASSWORD`   | SMTP password (SES, SendGrid, etc.)              |
| `SMTP_FROM`       | From address on outgoing mail                    |
| `PUBLIC_BASE_URL` | e.g. `https://example.com` — used in email links |

## Nginx snippet

```nginx
server {
  listen 443 ssl http2;
  server_name page-to-markdown.example.com;

  ssl_certificate     /etc/ssl/example/fullchain.pem;
  ssl_certificate_key /etc/ssl/example/privkey.pem;

  client_max_body_size 10M;

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

## Manual (no Docker)

```bash
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
uv run celery -A app.tasks worker --loglevel=info
```

Redis must be running separately.
