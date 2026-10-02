import re

with open("frontend/src/components/AssistantMessage.tsx", "r") as f:
    content = f.read()

# I want to replace the whole <article> block
replacement = """        <article className="card assistant-card">
          <TriageCard decision={response.triage} language={language} />
          <p className="assistant-card__text">{localized(response.user_message, language)}</p>
          <FollowUpList questions={response.follow_up_questions} language={language} />
          <DisclaimerBlock disclaimers={response.disclaimers} language={language} />
          <EvidenceList
            evidence={response.evidence}
            evidenceNote={response.evidence_note}
            language={language}
          />
          {response.clinician_summary && (
            <ClinicianSummaryView summary={response.clinician_summary} language={language} />
          )}
        </article>"""

content = re.sub(r'        <article className="card assistant-card">.*?</article>', replacement, content, flags=re.DOTALL)

with open("frontend/src/components/AssistantMessage.tsx", "w") as f:
    f.write(content)
