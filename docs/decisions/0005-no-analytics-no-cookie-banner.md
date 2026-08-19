# 0005 — No analytics, no cookie banner

Date: 2026-08-19
Status: Accepted

## Context

Adding analytics (GA4, Plausible, Fathom, self-hosted) means either shipping a
cookie banner (GDPR/ePrivacy) or picking a cookieless provider and still
disclosing it in the privacy policy. Both add work and visual noise.

For v1 we care about launching, not traffic breakdown.

## Decision

No analytics scripts. No tracking pixels. No cookies set by the site or the
API in v1. The cookie policy page states plainly that we set no cookies.

## Consequences

**Enables**

- No cookie banner
- Fastest page loads possible
- Simplest privacy policy
- No GDPR consent management

**Rules out**

- Knowing conversion rates without adding it back
- A/B testing on the marketing page

## Alternatives considered

- Plausible (cookieless): still requires disclosure and a small script.
  Revisit when we need traffic data.
- Server-side logs only: doable, but noisy and hard to summarize.
