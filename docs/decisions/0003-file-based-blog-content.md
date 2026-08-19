# 0003 — File-based blog content

Date: 2026-08-19
Status: Accepted

## Context

The marketing site needs a blog and legal pages. Options:

- Headless CMS (Sanity, Contentful): non-devs can edit, extra infra
- Database-backed posts + admin UI: full custom, lots of work
- Markdown files in the repo: `git` is the CMS

Contributors are developers. Post cadence will be low (a few posts a month at
most). Legal pages barely ever change.

## Decision

Blog posts and legal pages live as Markdown files in `app/content/`. Loaded
at startup with `python-frontmatter`, cached in memory, rendered with the
`markdown` package. Pagination is a slice on a sorted list. No CMS, no
database for content.

## Consequences

**Enables**

- PR workflow for content (review, diff, revert)
- Static hosting friendliness
- Zero content infra to run

**Rules out**

- Non-dev content editors
- Draft/scheduled posts (unless we add explicit tooling)
- MDX or custom shortcodes (see [0001](0001-all-python-stack.md))

## Alternatives considered

- Sanity headless CMS: overkill for the post volume.
- Simple SQLite content table: still requires an admin UI.
