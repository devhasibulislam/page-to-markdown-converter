---
applyTo: "extension/**/*.{ts,tsx}"
---

# TypeScript / Extension conventions

- **Strict mode** on. `noImplicitAny`, `strictNullChecks`, `exactOptionalPropertyTypes`.
- **No `any`**. Use `unknown` and narrow. If a third-party lib forces it, isolate in one adapter file.
- **Named exports only** (no default exports). Makes refactors safer.
- **Chrome APIs**: use `chrome.*`. Do not use `browser.*` (Firefox has a chrome shim in MV3).
- **Manifest V3 patterns**: background is a service worker, not a persistent page. Assume it can be killed anytime — persist state in `chrome.storage`.
- **Payload**: gzip HTML before POST. Strip `<script>` and `<style>` client-side first.
- **Readiness**: wait for MutationObserver to settle before grabbing `outerHTML`. Do not fire on `DOMContentLoaded` alone.
- **Errors**: typed. Never `throw "string"`. Prefer discriminated unions in message passing.
- **Formatting**: Prettier defaults, 100-char lines.
- **Testing**: Vitest for unit, Playwright for E2E against real sites.
