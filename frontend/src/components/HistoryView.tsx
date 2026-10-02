import { TrashIcon } from "./Icons";
import { strings } from "../i18n/strings";
import { deleteSession } from "../api/client";

export function HistoryView({ language, history, onLoadSession, onDelete }: { language: "en"|"ur"|"sd", history: any, onLoadSession: any, onDelete: any }) {
  const t = strings(language);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm(t.confirmDelete)) return;
    try {
      await deleteSession(id);
      onDelete(id);
    } catch {
      alert("Failed to delete session.");
    }
  };

  return (
    <div className="history-view">
      <h2 className="section-title">{t.historyTitle}</h2>
      {history.length === 0 ? (
        <p className="empty-state">{t.emptyHistory}</p>
      ) : (
        <div className="history-grid">
          {history.map((record: any) => (
            <div key={record.id} className="history-card" onClick={() => onLoadSession(record.id)}>
              <div className="history-card__content">
                <h4>{record.preview}</h4>
                <p>{new Date(record.updatedAt).toLocaleDateString(language === "en" ? "en-US" : "ur-PK")}</p>
              </div>
              <button
                type="button"
                className="ghost-button delete-button"
                onClick={(e) => handleDelete(record.id, e)}
                title={t.deleteSession}
              >
                <TrashIcon size={18} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
