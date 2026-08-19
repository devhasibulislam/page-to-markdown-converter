---
title: "Privacy policy"
updated: 2026-08-19
---

We collect as little as possible. That's the whole policy in one sentence.

## What the extension does

When you click the MarkDrop extension on a page, it reads the fully-rendered
HTML of that page and sends it to our backend for extraction. The HTML is
transmitted over HTTPS, processed, and either returned to you (preview),
saved as a temporary file for download, or attached to an email you asked us
to send.

We do not:

- Read pages you haven't clicked the extension on
- Track which pages you convert
- Store the HTML after extraction is complete
- Set cookies
- Load analytics scripts

## What the backend keeps

- **Inline** requests: nothing is stored. The markdown is returned in the
  response and forgotten.
- **Download** requests: the `.md` file is written to a temporary directory
  and deleted one hour after it becomes ready. Job status lives in Redis for
  24 hours.
- **Email** requests: the `.md` is sent as an attachment through your chosen
  SMTP provider, then deleted. The email address you provide is used for that
  one delivery and not retained.

## Third parties

- SMTP provider (used only when you choose the email delivery method). See
  their privacy policy for how they handle the message in transit.

## Contact

Questions: open an issue on
[GitHub](https://github.com/devhasibulislam/page-to-markdown-converter/issues).
