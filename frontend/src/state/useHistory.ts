import { useCallback, useEffect, useState } from "react";
import { v1GetHistorySessions } from "../api/client";

export interface HistoryRecord {
  id: string;
  preview: string;
  createdAt: number;
  updatedAt: number;
}

export function useHistory() {
  const [history, setHistory] = useState<HistoryRecord[]>([]);

  const fetchHistory = useCallback(async () => {
    try {
      const sessions = await v1GetHistorySessions();
      setHistory(sessions.map(s => ({
        id: s.id,
        preview: s.preview,
        createdAt: new Date(s.created_at).getTime(),
        updatedAt: new Date(s.updated_at).getTime(),
      })));
    } catch (err) {
      console.error("Failed to load history", err);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const addOrUpdate = useCallback((id: string, preview?: string) => {
    // Optionally refresh from backend, or optimistically update
    setHistory((prev) => {
      const existing = prev.find((r) => r.id === id);
      const now = Date.now();
      const updated = existing
        ? prev.map((r) => (r.id === id ? { ...r, updatedAt: now, preview: preview || r.preview } : r))
        : [{ id, preview: preview || "New Session", createdAt: now, updatedAt: now }, ...prev];
      return updated.sort((a, b) => b.updatedAt - a.updatedAt);
    });
  }, []);

  const remove = useCallback((id: string) => {
    setHistory((prev) => prev.filter((r) => r.id !== id));
  }, []);

  return { history, addOrUpdate, remove };
}
