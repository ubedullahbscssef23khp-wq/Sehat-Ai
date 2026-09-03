"""Deterministic triage-level computation (ARCHITECTURE.md §6 step 6, §8).

Pure function of the structured case plus the safety assessment. Safety flags
always take precedence over information completeness: an emergency or urgent
flag must never be delayed by follow-up questions.
"""

from __future__ import annotations

from app.models import (
    LocalizedText,
    SafetyAssessment,
    SafetyLevel,
    StructuredCase,
    TriageDecision,
    TriageLevel,
)

# Generic care-seeking copy per level. These are product safety statements,
# not clinical claims; localized variants are added in Phase 6.
_ACTIONS: dict[TriageLevel, list[LocalizedText]] = {
    TriageLevel.EMERGENCY: [
        LocalizedText(en="Call emergency services or go to the nearest emergency department now.", ur="ایمرجنسی سروسز کو کال کریں یا ابھی قریبی ایمرجنسی شعبے میں جائیں۔", sd="ايمرجنسي سروسز کي فون ڪريو يا هاڻي ويجهي ايمرجنسي کاتي وڃو."),
        LocalizedText(en="Do not wait to see if the symptoms settle on their own.", ur="علامات خود ٹھیک ہونے کا انتظار نہ کریں۔", sd="علامتن جي پاڻ ٺيڪ ٿيڻ جو انتظار نه ڪريو."),
    ],
    TriageLevel.URGENT_SAME_DAY: [
        LocalizedText(en="Arrange an in-person assessment with a healthcare professional today.", ur="آج ہی کسی طبی پیشہ ور سے بالمشافہ معائنہ کروائیں۔", sd="اڄ ئي ڪنهن طبي ماهر کان روبرو معائنو ڪرايو."),
    ],
    TriageLevel.ROUTINE: [
        LocalizedText(en="Arrange a non-urgent appointment with a healthcare professional to review these symptoms.", ur="ان علامات کے جائزے کے لیے کسی طبی پیشہ ور سے معمول کی ملاقات طے کریں۔", sd="انهن علامتن جي جائزي لاءِ ڪنهن طبي ماهر سان غير فوري ملاقات طئي ڪريو."),
    ],
    TriageLevel.SELF_CARE: [
        LocalizedText(en="Self-care at home is reasonable based on the information provided.", ur="فراہم کردہ معلومات کی بنیاد پر گھر پر اپنی دیکھ بھال مناسب ہے۔", sd="مهيا ڪيل معلومات جي بنياد تي گهر ۾ پنهنجي سنڀال مناسب آهي."),
    ],
    TriageLevel.NEEDS_MORE_INFO: [
        LocalizedText(en="Answer the follow-up questions so the guidance can be completed.", ur="مزید سوالات کے جواب دیں تاکہ رہنمائی مکمل ہو سکے۔", sd="وڌيڪ سوالن جا جواب ڏيو ته جيئن رهنمائي مڪمل ٿي سگهي."),
    ],
}

_SELF_CARE_LIMITS: list[LocalizedText] = [
    LocalizedText(en="Seek medical care if symptoms worsen, new symptoms appear, or you are concerned.", ur="اگر علامات بڑھیں، نئی علامات ظاہر ہوں، یا آپ کو تشویش ہو تو طبی مدد حاصل کریں۔", sd="جيڪڏهن علامتون وڌن، نيون علامتون ظاهر ٿين يا توهان کي ڳڻتي هجي ته طبي مدد وٺو."),
]

_RECHECK_ADVICE = LocalizedText(
    en="If symptoms worsen, persist, or you become concerned, seek medical care promptly.",
    ur="اگر علامات بڑھیں، برقرار رہیں، یا آپ کو تشویش ہو تو فوراً طبی مدد حاصل کریں۔",
    sd="جيڪڏهن علامتون وڌن، جاري رهن يا توهان کي ڳڻتي ٿئي ته ترت طبي مدد وٺو.",
)


def decide(case: StructuredCase, assessment: SafetyAssessment, best_effort: bool = False) -> TriageDecision:
    levels = {fired.level for fired in assessment.fired_rules}

    if SafetyLevel.EMERGENCY in levels:
        level = TriageLevel.EMERGENCY
    elif SafetyLevel.URGENT in levels:
        level = TriageLevel.URGENT_SAME_DAY
    elif case.missing_fields and not best_effort:
        level = TriageLevel.NEEDS_MORE_INFO
    elif SafetyLevel.MONITOR in levels:
        level = TriageLevel.ROUTINE
    else:
        level = TriageLevel.SELF_CARE

    return TriageDecision(
        level=level,
        fired_rule_ids=[fired.rule_id for fired in assessment.fired_rules],
        next_actions=_ACTIONS[level],
        self_care_limits=list(_SELF_CARE_LIMITS) if level == TriageLevel.SELF_CARE else [],
        recheck_advice=_RECHECK_ADVICE
        if level in (TriageLevel.SELF_CARE, TriageLevel.ROUTINE)
        else None,
        limited_confidence=best_effort,
    )
