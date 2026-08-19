// Popup UI: three delivery methods, calls background worker, polls jobs.

import {
  type DeliveryMethod,
  type MessageFromBackground,
  type MessageToBackground,
  getBackendUrl,
} from "./shared";

const $ = <T extends HTMLElement>(id: string): T => {
  const el = document.getElementById(id);
  if (!el) throw new Error(`missing #${id}`);
  return el as T;
};

const convertBtn = $<HTMLButtonElement>("convert");
const emailRow = $<HTMLDivElement>("email-row");
const emailInput = $<HTMLInputElement>("email");
const statusBox = $<HTMLDivElement>("status");
const previewBox = $<HTMLDivElement>("preview");
const previewTitle = $<HTMLElement>("preview-title");
const markdownBox = $<HTMLPreElement>("markdown");
const copyBtn = $<HTMLButtonElement>("copy");

function selectedDelivery(): DeliveryMethod {
  const el = document.querySelector<HTMLInputElement>(
    'input[name="delivery"]:checked',
  );
  return (el?.value as DeliveryMethod) ?? "inline";
}

function setStatus(text: string, tone: "ok" | "err" | "info"): void {
  statusBox.textContent = text;
  statusBox.className = `status ${tone}`;
  statusBox.hidden = false;
}

function clearStatus(): void {
  statusBox.hidden = true;
  statusBox.textContent = "";
}

function toggleEmail(): void {
  emailRow.hidden = selectedDelivery() !== "email";
}

document
  .querySelectorAll<HTMLInputElement>('input[name="delivery"]')
  .forEach((r) => r.addEventListener("change", toggleEmail));
toggleEmail();

function send(msg: MessageToBackground): Promise<MessageFromBackground> {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(msg, (response: MessageFromBackground) =>
      resolve(response),
    );
  });
}

async function pollUntilTerminal(
  jobId: string,
): Promise<MessageFromBackground> {
  for (let i = 0; i < 60; i++) {
    await new Promise((r) => setTimeout(r, 2000));
    const response = await send({ type: "poll", jobId });
    if (!response.ok) return response;
    if (response.kind !== "status") return response;
    const s = response.data.status;
    if (s === "ready" || s === "sent" || s === "failed") return response;
  }
  return {
    ok: false,
    error: "timeout",
    message: "Job did not finish in time.",
  };
}

convertBtn.addEventListener("click", async () => {
  clearStatus();
  previewBox.hidden = true;
  convertBtn.disabled = true;
  convertBtn.textContent = "Converting…";
  const delivery = selectedDelivery();
  const email = delivery === "email" ? emailInput.value.trim() : undefined;

  if (delivery === "email" && !email) {
    setStatus("Enter an email address.", "err");
    resetButton();
    return;
  }

  try {
    const response = await send({ type: "convert", delivery, email });
    if (!response.ok) {
      setStatus(`${response.error}: ${response.message}`, "err");
      return;
    }

    if (response.kind === "inline") {
      previewTitle.textContent = response.data.title || "Untitled";
      markdownBox.textContent = response.data.markdown;
      previewBox.hidden = false;
      setStatus(`Extracted ${response.data.wordCount} words.`, "ok");
      return;
    }

    if (response.kind === "job") {
      setStatus(
        delivery === "email" ? "Queued email…" : "Preparing download…",
        "info",
      );
      const final = await pollUntilTerminal(response.data.jobId);
      if (!final.ok) {
        setStatus(final.message, "err");
        return;
      }
      if (final.kind !== "status") return;

      if (final.data.status === "ready" && final.data.downloadUrl) {
        const backend = await getBackendUrl();
        chrome.downloads.download({
          url: `${backend}${final.data.downloadUrl}`,
        });
        setStatus("Download started.", "ok");
      } else if (final.data.status === "sent") {
        setStatus("Email sent.", "ok");
      } else {
        setStatus(`Failed: ${final.data.error ?? "unknown"}`, "err");
      }
    }
  } finally {
    resetButton();
  }
});

copyBtn.addEventListener("click", async () => {
  await navigator.clipboard.writeText(markdownBox.textContent ?? "");
  const original = copyBtn.textContent;
  copyBtn.textContent = "Copied!";
  setTimeout(() => {
    copyBtn.textContent = original;
  }, 1200);
});

function resetButton(): void {
  convertBtn.disabled = false;
  convertBtn.textContent = "Convert this page";
}
