# 0001 — All-Python stack

Date: 2026-08-19
Status: Accepted

## Context

We need a backend, a public website, and a browser extension. Options were:

- Python backend + Node/React front-end (two toolchains)
- Node full-stack (Next.js) with Python extraction service
- All-Python (FastAPI + Jinja2 + Bootstrap) with a small TypeScript extension

The main constraint: keep the stack narrow. The extraction quality gap between
Python (`trafilatura`) and JS equivalents is meaningful, so Python for the
backend is fixed. The question was what the marketing site runs on.

## Decision

One FastAPI app serves both the JSON API and the marketing site. Jinja2
templates styled with local Bootstrap 5 (no CDN). The only non-Python code is
the browser extension itself (TypeScript, MV3), which can't be avoided.

## Consequences

**Enables**

- One process, one deploy target, one build toolchain for the core product
- Simpler contributor onboarding (Python only for backend + site)
- No Node runtime on the server

**Rules out**

- React/Vue/Svelte on the marketing site
- MDX (custom components in Markdown) for blog posts
- Client-side interactivity beyond what Bootstrap's bundle provides

## Alternatives considered

- Next.js everywhere: heavier, better SEO tools, splits the team's mental model.
  Rejected because the site is mostly static.
- Django: batteries included, but overkill for a 6-route site with no DB.
