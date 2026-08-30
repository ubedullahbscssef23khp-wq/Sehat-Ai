/** Typed backend client. All medical logic stays server-side; the frontend
 * only renders what the API returns (ARCHITECTURE.md §5). */

export interface HealthStatus {
  status: "ok";
  service: string;
  env: string;
  llm_provider: string;
}

export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch("/api/health");
  if (!response.ok) {
    throw new Error(`Health check failed: HTTP ${response.status}`);
  }
  return (await response.json()) as HealthStatus;
}
