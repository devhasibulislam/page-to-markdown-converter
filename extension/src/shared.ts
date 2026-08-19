export type DeliveryMethod = "inline" | "download" | "email";

export interface ConvertRequest {
  html: string;
  sourceUrl: string;
  deliveryMethod: DeliveryMethod;
  email?: string;
}

export interface InlineResponse {
  sourceUrl: string;
  title: string;
  markdown: string;
  wordCount: number;
  extractedAt: string;
}

export interface JobResponse {
  jobId: string;
}

export interface JobStatus {
  status: "queued" | "processing" | "ready" | "sent" | "failed";
  downloadUrl: string | null;
  error: string | null;
}

export interface ApiError {
  error: string;
  message: string;
}

export type MessageToBackground =
  | { type: "convert"; delivery: DeliveryMethod; email?: string }
  | { type: "poll"; jobId: string };

export type MessageFromBackground =
  | { ok: true; kind: "inline"; data: InlineResponse }
  | { ok: true; kind: "job"; data: JobResponse }
  | { ok: true; kind: "status"; data: JobStatus }
  | { ok: false; error: string; message: string };

export const DEFAULT_BACKEND = "http://localhost:8000";

export async function getBackendUrl(): Promise<string> {
  const { backendUrl } = await chrome.storage.local.get("backendUrl");
  return typeof backendUrl === "string" && backendUrl.length > 0 ? backendUrl : DEFAULT_BACKEND;
}
