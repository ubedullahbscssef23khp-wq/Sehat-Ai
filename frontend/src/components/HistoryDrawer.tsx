import { useCallback, useState } from "react";
import { deleteSession } from "../api/client";
import { strings, directionOf } from "../i18n/strings";
import type { Language } from "../api/types";
import { CloseIcon, MenuIcon, TrashIcon } from "./Icons";
import { useHistory } from "../state/useHistory";

interface Props {
  isSidebarBtn?: boolean;
  isMobileBtn?: boolean;
  language: Language;
  onSelect: (id: string) => void;
  disabled?: boolean;
}

export function HistoryDrawer({ language, onSelect, disabled }: Props) {
  const [open, setOpen] = useState(false);
  const { history, remove } = useHistory();
  const t = strings(language);
  const dir = directionOf(language);

  const handleDelete = useCallback(async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm(t.confirmDelete)) return;
    try {
      await deleteSession(id);
      remove(id);
    } catch {
      alert("Failed to delete session.");
    }
  }, [remove, t.confirmDelete]);

  return (
    <>
      <button
        type="button"
        className="ghost-button"
        onClick={() => setOpen(true)}
        disabled={disabled}
        aria-label={t.historyTitle}
      >
        <MenuIcon size={18} />
      </button>

      {open && (
        <div className="drawer-overlay" onClick={() => setOpen(false)} dir={dir}>
          <div className="drawer" onClick={(e) => e.stopPropagation()}>
            <div className="drawer__header">
              <h2>{t.historyTitle}</h2>
              <button type="button" className="ghost-button" onClick={() => setOpen(false)}>
                <CloseIcon size={18} />
              </button>
            </div>
            <div className="drawer__content">
              {history.length === 0 ? (
                <p className="drawer__empty">{t.emptyHistory}</p>
              ) : (
                <ul className="history-list">
                  {history.map((record) => (
                    <li key={record.id} className="history-item" onClick={() => { onSelect(record.id); setOpen(false); }}>
                      <div className="history-item__text">
                        <span className="history-item__preview">{record.preview}</span>
                        <span className="history-item__date">
                          {new Date(record.updatedAt).toLocaleDateString(language === "en" ? "en-US" : "ur-PK")}
                        </span>
                      </div>
                      <button
                        type="button"
                        className="ghost-button delete-button"
                        onClick={(e) => handleDelete(record.id, e)}
                        title={t.deleteSession}
                      >
                        <TrashIcon size={15} />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
