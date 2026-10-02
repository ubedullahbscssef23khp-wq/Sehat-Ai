import re

with open("frontend/src/components/ClinicianSummaryView.tsx", "r") as f:
    content = f.read()

content = re.sub(
    r'function formatHandoff.*',
    '''function formatHandoff(summary: ClinicianSummary, t: ReturnType<typeof strings>): string {
  const { structured_case, fired_rules, triage_decision, timeline, generated_at, model_attribution } = summary;
  
  const lines: string[] = [];
  
  lines.push(t.handoffTitle);
  lines.push("");
  lines.push(t.handoffDisclaimer1);
  lines.push(t.handoffDisclaimer2);
  lines.push("");
  
  lines.push(`${t.chiefComplaintLabel}:`);
  lines.push(structured_case.chief_complaint || t.notProvided);
  lines.push("");
  
  lines.push(`${t.symptomsLabel}:`);
  if (structured_case.symptoms && structured_case.symptoms.length > 0) {
    for (const sym of structured_case.symptoms) {
      lines.push(`- ${sym.name}`);
      if (sym.severity !== null) {
        lines.push(`  ${t.severityLabel}: ${sym.severity}/10`);
      }
      if (sym.duration) {
        lines.push(`  ${t.durationLabel}: ${sym.duration}`);
      }
      if (sym.progression && sym.progression !== "unknown") {
        lines.push(`  ${t.progressionLabel}: ${sym.progression}`);
      }
    }
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.demographicsLabel}:`);
  const hasAge = structured_case.demographics?.age_group && structured_case.demographics.age_group !== "unknown";
  const hasPregnancy = structured_case.demographics?.pregnant !== null && structured_case.demographics?.pregnant !== undefined;
  
  if (hasAge || hasPregnancy) {
    if (hasAge) lines.push(`- ${t.ageGroupLabel}: ${structured_case.demographics.age_group}`);
    if (hasPregnancy) lines.push(`- ${t.pregnancyLabel}: ${structured_case.demographics.pregnant ? t.pregnantYes : t.pregnantNo}`);
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.redFlagsLabel}:`);
  if (structured_case.red_flag_signals && structured_case.red_flag_signals.length > 0) {
    for (const signal of structured_case.red_flag_signals) {
      lines.push(`- ${signal}`);
    }
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.firedRulesLabel}:`);
  if (fired_rules && fired_rules.length > 0) {
    for (const rule of fired_rules) {
      lines.push(`- ${rule.description}${rule.level ? ` (${rule.level.toUpperCase()})` : ""}`);
    }
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.triageDecisionLabel}:`);
  if (triage_decision && triage_decision.level) {
    lines.push(t.triageLabels[triage_decision.level]);
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.timelineLabel}:`);
  if (timeline && timeline.length > 0) {
    for (const entry of timeline) {
      lines.push(`- ${entry}`);
    }
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  if (generated_at) {
    lines.push(`${t.generatedLabel}:`);
    lines.push(generated_at);
    lines.push("");
  }
  
  if (model_attribution) {
    lines.push(`${t.modelAttributionLabel}:`);
    lines.push(model_attribution);
    lines.push("");
  }
  
  lines.push(t.handoffFooter);
  
  return lines.join("\\n");
}
''',
    content,
    flags=re.DOTALL
)

with open("frontend/src/components/ClinicianSummaryView.tsx", "w") as f:
    f.write(content)

