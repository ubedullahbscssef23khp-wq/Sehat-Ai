import { useEffect, useState } from "react";
import { fetchHealth, type HealthStatus } from "./api/health";

type ConnectionState =
  | { kind: "loading" }
  | { kind: "online"; health: HealthStatus }
  | { kind: "offline"; error: string };

export default function App() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    fetchHealth()
      .then((health) => {
        if (!cancelled) setConnection({ kind: "online", health });
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setConnection({
            kind: "offline",
            error: error instanceof Error ? error.message : String(error),
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="shell">
      <h1>Sehat AI</h1>
      <p className="tagline">
        AI-assisted health guidance and symptom triage · English · اردو · سنڌي
      </p>

      <section className="status-card" aria-live="polite">
        {connection.kind === "loading" && <p className="muted">Connecting to backend…</p>}
        {connection.kind === "online" && (
          <>
            <p className="ok">Backend online</p>
            <dl className="kv">
              <dt>Service</dt>
              <dd>{connection.health.service}</dd>
              <dt>Environment</dt>
              <dd>{connection.health.env}</dd>
              <dt>LLM provider</dt>
              <dd>{connection.health.llm_provider}</dd>
            </dl>
          </>
        )}
        {connection.kind === "offline" && (
          <>
            <p className="error">Backend unreachable</p>
            <p className="muted">
              Start the backend (from <code>backend/</code>:{" "}
              <code>python -m uvicorn app.main:create_app --factory</code>) and reload.
            </p>
            <p className="muted small">{connection.error}</p>
          </>
        )}
      </section>

      <footer className="disclaimer">
        Sehat AI provides general guidance only. It does not diagnose conditions and does
        not replace a qualified healthcare professional.
      </footer>
    </main>
  );
}
