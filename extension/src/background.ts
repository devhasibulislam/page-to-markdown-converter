// Background service worker — forwards convert requests from the popup to the
// backend and polls job status for async deliveries.

import {
  type ApiError,
  type InlineResponse,
  type JobResponse,
  type JobStatus,
  type MessageFromBackground,
  type MessageToBackground,
  getBackendUrl,
} from "./shared";

async function grabActiveTabHtml(): Promise<{
  html: string;
  sourceUrl: string;
}> {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) throw new Error("no_active_tab");

  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ["content.js"],
  });

  return new Promise((resolve, reject) => {
    chrome.tabs.sendMessage(
      tab.id!,
      { type: "grab" },
      (response: { html?: string; sourceUrl?: string } | undefined) => {
        if (
          chrome.runtime.lastError ||
          !response?.html ||
          !response.sourceUrl
        ) {
          reject(new Error(chrome.runtime.lastError?.message ?? "grab_failed"));
          return;
        }
        resolve({ html: response.html, sourceUrl: response.sourceUrl });
      },
    );
  });
}

async function postConvert(
  backend: string,
  html: string,
  sourceUrl: string,
  delivery: "inline" | "download" | "email",
  email?: string,
): Promise<Response> {
  return fetch(`${backend}/api/convert`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ html, sourceUrl, deliveryMethod: delivery, email }),
  });
}

async function handleConvert(
  delivery: "inline" | "download" | "email",
  email: string | undefined,
): Promise<MessageFromBackground> {
  const backend = await getBackendUrl();
  const { html, sourceUrl } = await grabActiveTabHtml();
  const response = await postConvert(backend, html, sourceUrl, delivery, email);

  if (response.status === 200) {
    const data = (await response.json()) as InlineResponse;
    return { ok: true, kind: "inline", data };
  }
  if (response.status === 202) {
    const data = (await response.json()) as JobResponse;
    return { ok: true, kind: "job", data };
  }
  const err = (await response.json().catch(() => null)) as {
    detail?: ApiError;
  } | null;
  const detail = err?.detail;
  return {
    ok: false,
    error: detail?.error ?? "unknown_error",
    message: detail?.message ?? `HTTP ${response.status}`,
  };
}

async function handlePoll(jobId: string): Promise<MessageFromBackground> {
  const backend = await getBackendUrl();
  const response = await fetch(`${backend}/api/jobs/${jobId}`);
  if (!response.ok) {
    return {
      ok: false,
      error: "job_not_found",
      message: `HTTP ${response.status}`,
    };
  }
  const data = (await response.json()) as JobStatus;
  return { ok: true, kind: "status", data };
}

chrome.runtime.onMessage.addListener(
  (
    msg: MessageToBackground,
    _sender,
    sendResponse: (m: MessageFromBackground) => void,
  ) => {
    (async () => {
      try {
        if (msg.type === "convert") {
          sendResponse(await handleConvert(msg.delivery, msg.email));
        } else if (msg.type === "poll") {
          sendResponse(await handlePoll(msg.jobId));
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        sendResponse({ ok: false, error: "extension_error", message });
      }
    })();
    return true;
  },
);
