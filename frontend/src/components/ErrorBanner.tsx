import type { Language } from "../api/types";
import { strings } from "../i18n/strings";
import type { UiError, UiErrorKind } from "../state/useChat";
import { AlertIcon, PlusIcon, RefreshIcon } from "./Icons";

const MESSAGE_KEY: Record<UiErrorKind, keyof ReturnType<typeof strings>> = {
  offline: "errorOffline",
  server: "errorServer",
  validation: "errorValidation",
  tooLong: "errorTooLong",
  closed: "errorClosed",
  notFound: "errorNotFound",
  unavailable: "errorUnavailable",
  generic: "errorGeneric",
};

const RETRYABLE: ReadonlySet<UiErrorKind> = new Set(["offline", "server", "unavailable", "generic"]);
const RESTART: ReadonlySet<UiErrorKind> = new Set(["closed", "notFound"]);

interface ErrorBannerProps {
  error: UiError;
  language: Language;
  onRetry: () => void;
  onNewConversation: () => void;
}

export function ErrorBanner({ error, language, onRetry, onNewConversation }: ErrorBannerProps) {
  const t = strings(language);
  const message = t[MESSAGE_KEY[error.kind]] as string;
  return (
    <div className="error-banner" role="alert">
      <p className="error-banner__text">
        <AlertIcon size={17} />
        <span>{message}</span>
      </p>
      {RETRYABLE.has(error.kind) && (
        <button type="button" className="error-banner__action" onClick={onRetry}>
          <RefreshIcon size={15} />
          <span>{t.retry}</span>
        </button>
      )}
      {RESTART.has(error.kind) && (
        <button type="button" className="error-banner__action" onClick={onNewConversation}>
          <PlusIcon size={15} />
          <span>{t.newConversation}</span>
        </button>
      )}
    </div>
  );
}
