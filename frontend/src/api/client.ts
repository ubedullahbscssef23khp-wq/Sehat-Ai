/** Typed conversation API client over the existing Vite `/api` proxy.
 *
 * The client only transports and classifies responses; all medical logic
 * stays server-side (ARCHITECTURE.md §5). No health text is ever logged.
 */

import type { ErrorEnvelope, GuidanceResponse, Language, Session } from "./types";

const BASE = "/api";

/** A structured failure returned by the backend error envelope. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

/** The backend could not be reached at all (network failure). */
export class NetworkError extends Error {
  constructor() {
    super("The Sehat AI service could not be reached.");
    this.name = "NetworkError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new NetworkError();
  }

  if (!response.ok) {
    let code = "unexpected_error";
    let message = "";
    try {
      const body = (await response.json()) as ErrorEnvelope;
      code = body.error?.code ?? code;
      message = body.error?.message ?? "";
    } catch {
      // Non-JSON failure body: keep the generic classification.
    }
    throw new ApiError(response.status, code, message);
  }

  return (await response.json()) as T;
}

export function createSession(preferred_language: Language): Promise<Session> {
  return request<Session>("/sessions", {
    method: "POST",
    body: JSON.stringify({ preferred_language }),
  });
}

export function getSession(session_id: string): Promise<Session> {
  return request<Session>(`/sessions/${encodeURIComponent(session_id)}`);
}

export function sendMessage(session_id: string, text: string): Promise<GuidanceResponse> {
  return request<GuidanceResponse>(`/sessions/${encodeURIComponent(session_id)}/messages`, {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}
