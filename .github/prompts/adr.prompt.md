---
description: "Scaffold a new Architecture Decision Record with the next sequential number."
---

Create a new ADR in `docs/decisions/` documenting a design decision.

Steps:

1. List existing files in `docs/decisions/` to find the highest number.
2. Compute the next 4-digit number (e.g. `0007`).
3. Ask the user for the decision title if not provided in `${input:title}`.
4. Slugify the title (lowercase, hyphens, ASCII only).
5. Create `docs/decisions/NNNN-<slug>.md` with this structure:

```markdown
# NNNN — <Title>

Date: <YYYY-MM-DD>
Status: Accepted

## Context

<Why is this decision needed? What forces are at play?>

## Decision

<What was chosen. Be specific and unambiguous.>

## Consequences

<What this enables, what it rules out, what trade-offs it accepts.>

## Alternatives considered

<Options rejected and why.>
```

6. Fill in each section based on the current chat context.
7. Add a link to the new ADR in `docs/decisions/README.md` (create if missing).
