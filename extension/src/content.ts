// Content script — reads the fully-rendered HTML on request from the popup.
// Strips <script> and <style> to keep the payload small.

function stripHeavyTags(html: string): string {
  return html.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, "");
}

function grabHtml(): { html: string; sourceUrl: string } {
  const html = stripHeavyTags(document.documentElement.outerHTML);
  return { html, sourceUrl: location.href };
}

chrome.runtime.onMessage.addListener((msg: unknown, _sender, sendResponse) => {
  if (typeof msg === "object" && msg !== null && (msg as { type?: string }).type === "grab") {
    sendResponse(grabHtml());
  }
  return true;
});
