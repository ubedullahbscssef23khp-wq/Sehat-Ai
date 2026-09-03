import type { Language, LocalizedText } from "../api/types";
import { localized } from "../api/types";
import { strings } from "../i18n/strings";
import { QuestionIcon } from "./Icons";

interface FollowUpListProps {
  questions: LocalizedText[];
  language: Language;
}

/** Renders exactly the follow-up questions the backend provides — never more,
 * never fewer, and never generated on the client. */
export function FollowUpList({ questions, language }: FollowUpListProps) {
  if (questions.length === 0) {
    return null;
  }
  const t = strings(language);
  return (
    <section className="followup" aria-label={t.followUpHeading}>
      <p className="followup__intro">
        <QuestionIcon size={16} />
        <span>{t.followUpHeading}</span>
      </p>
      {questions.length === 1 ? (
        <p className="followup__single">{localized(questions[0], language)}</p>
      ) : (
        <ol className="followup__list">
          {questions.map((question, index) => (
            <li key={index}>{localized(question, language)}</li>
          ))}
        </ol>
      )}
    </section>
  );
}
