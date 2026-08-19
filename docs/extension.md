# Extension

Manifest V3, TypeScript, Chrome / Edge / Firefox / Brave compatible. Distributed
as a ZIP for v1 (no store submissions yet).

## Install (end user)

1. Download `extension.zip` from the home page.
2. Unzip.
3. Open your browser's extensions page:
   - Chrome / Brave: `chrome://extensions`
   - Edge: `edge://extensions`
   - Firefox: `about:debugging#/runtime/this-firefox`
4. Enable **Developer mode** (top-right toggle in Chromium browsers).
5. Click **Load unpacked** and pick the unzipped folder.

The home page has a browser picker with a video tutorial per browser.

## Dev build

```bash
cd extension
pnpm install
pnpm dev            # watch mode, rebuilds on save
pnpm build          # production bundle
```

Load `extension/dist/` as an unpacked extension while developing.

## Structure

```
extension/
├── manifest.json           MV3 manifest
├── src/
│   ├── content.ts          Grabs outerHTML, strips scripts/styles, gzips
│   ├── background.ts       Service worker: fetch to backend, poll jobs
│   └── popup.tsx           UI: Preview / Download / Email
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Permissions (manifest)

- `activeTab` — read current tab content on user click
- `scripting` — inject content script
- `storage` — remember backend URL, last email
- `downloads` — save `.md` files locally
- Host permission: the backend URL (configurable)

## Flows

### Preview

1. User picks "Preview," clicks Convert.
2. Content script runs on the active tab, returns HTML string.
3. Background worker POSTs `{ html, sourceUrl, deliveryMethod: "inline" }`.
4. Response markdown shows in the popup with a Copy button.

### Download

1. Same start.
2. Background worker POSTs `{ ..., deliveryMethod: "download" }`, gets `jobId`.
3. Polls `/api/jobs/{jobId}` every 2s.
4. On `ready`: `chrome.downloads.download({ url: downloadUrl })`.

### Email

1. Popup shows an email input.
2. Background worker POSTs `{ ..., deliveryMethod: "email", email }`, gets `jobId`.
3. Polls until `sent` or `failed`.
4. Shows confirmation.

## Payload shape (extension → backend)

```json
{
  "html": "<full outerHTML with scripts/styles stripped>",
  "sourceUrl": "https://example.com/article",
  "deliveryMethod": "inline",
  "email": null
}
```

Content-Encoding: gzip.
