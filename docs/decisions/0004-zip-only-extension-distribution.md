# 0004 — ZIP-only extension distribution

Date: 2026-08-19
Status: Accepted

## Context

Distribution options for the browser extension:

- Chrome Web Store: $5 one-time fee, review takes days to weeks first time
- Edge Add-ons: free, 1-7 day review
- Firefox AMO: free, usually under a day
- Direct ZIP download from our site: no approval, users load unpacked

Users have to enable Developer Mode to install unpacked extensions on Chromium
browsers. That's a real UX cost.

## Decision

Ship a direct ZIP download from `/download/extension.zip` for v1. No store
submissions. Home page includes a browser picker with an install-tutorial video
per browser (Chrome, Edge, Firefox, Brave) plus written steps.

## Consequences

**Enables**

- Ship immediately, no review queue
- Update at any cadence without going through store review
- Full control of the download experience

**Rules out** (until v2)

- Chrome Web Store visibility and one-click install
- Automatic updates through the browser
- Store trust badges

**Trade-offs**

- Users must enable Developer Mode
- Manual updates on new releases

## Alternatives considered

- Store-only: ships slower, blocks launch.
- Both stores + ZIP: worth doing later when the product is validated.
