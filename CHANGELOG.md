# Changelog

All notable changes documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Phase 5: Docker Compose (api + worker + redis), multi-stage Dockerfile, rate limits via slowapi (60/min on /api/convert, 10/min on /try)
- Phase 4: TypeScript MV3 browser extension (Preview / Download / Email), Vite build, packaged extension.zip
- Phase 3: Jinja2 + Bootstrap 5 site (home, 7-browser picker, try-it, paginated blog, legal pages)
- Phase 2: Celery + Redis async jobs, SMTP email delivery
- Phase 1: FastAPI `/api/convert` with dual input (html OR url), trafilatura + readability fallback
- Phase 0: repo scaffolding, docs, ADRs, Copilot customization surface
