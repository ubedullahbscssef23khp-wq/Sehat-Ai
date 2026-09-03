"""Response construction for the conversation API (ARCHITECTURE.md §7, §9).

User-facing copy here is product safety framing, not clinical content.
Disclaimers are server-injected and mandatory: GuidanceResponse validation
rejects an empty disclaimer list, so no client can strip the boundary.
"""

from __future__ import annotations

from app.models import (
    Citation,
    GuidanceResponse,
    LocalizedText,
    SafetyAssessment,
    StructuredCase,
    TriageDecision,
    TriageLevel,
)
from app.triage.engine import decide

DISCLAIMER = LocalizedText(
    en=(
        "Sehat AI provides general next-step guidance only. It is not a medical "
        "diagnosis and does not replace a qualified healthcare professional."
    ),
    ur=(
        "صحت اے آئی صرف اگلے قدم کی عمومی رہنمائی فراہم کرتا ہے۔ یہ طبی تشخیص "
        "نہیں ہے اور کسی مستند طبی پیشہ ور کا متبادل نہیں۔"
    ),
    sd=(
        "صحت اي آءِ صرف ايندڙ قدم جي عام رهنمائي مهيا ڪري ٿو. هي طبي تشخيص "
        "ناهي ۽ ڪنهن مستند طبي ماهر جو متبادل ناهي."
    ),
)

NO_EVIDENCE_NOTE = LocalizedText(
    en=(
        "No reliable information is available in the curated knowledge base for "
        "this topic yet. Please rely on the next-step guidance above and consult "
        "a healthcare professional for details."
    ),
    ur=(
        "اس موضوع کے لیے ابھی مرتب کردہ معلوماتی ذخیرے میں قابل اعتماد معلومات "
        "موجود نہیں۔ اوپر دی گئی اگلے قدم کی رہنمائی پر عمل کریں اور مزید تفصیل "
        "کے لیے کسی طبی پیشہ ور سے مشورہ کریں۔"
    ),
    sd=(
        "هن موضوع لاءِ هن وقت مرتب ڪيل معلوماتي ذخيري ۾ قابل اعتماد معلومات "
        "موجود ناهي. مٿي ڏنل ايندڙ قدم جي رهنمائي تي ڀروسو ڪريو ۽ وڌيڪ تفصيل "
        "لاءِ ڪنهن طبي ماهر سان صلاح ڪريو."
    ),
)

_USER_MESSAGES: dict[TriageLevel, LocalizedText] = {
    TriageLevel.EMERGENCY: LocalizedText(
        en="This may be an emergency. Please follow the emergency actions below now.",
        ur="یہ ہنگامی صورتحال ہو سکتی ہے۔ براہ کرم ابھی نیچے دیے گئے ہنگامی اقدامات کریں۔",
        sd="هي ايمرجنسي واري صورتحال ٿي سگهي ٿي. مهرباني ڪري هاڻي هيٺ ڏنل ايمرجنسي وارا قدم کڻو.",
    ),
    TriageLevel.URGENT_SAME_DAY: LocalizedText(
        en="These symptoms should be assessed in person by a healthcare professional today.",
        ur="ان علامات کا آج ہی کسی طبی پیشہ ور سے بالمشافہ جائزہ کروانا چاہیے۔",
        sd="انهن علامتن جو اڄ ئي ڪنهن طبي ماهر کان روبرو جائزو وٺڻ گهرجي.",
    ),
    TriageLevel.ROUTINE: LocalizedText(
        en="These symptoms should be reviewed by a healthcare professional; this does not look urgent.",
        ur="ان علامات کا کسی طبی پیشہ ور سے جائزہ کروائیں؛ یہ فوری نوعیت کی نہیں لگتیں۔",
        sd="انهن علامتن جو ڪنهن طبي ماهر کان جائزو وٺرايو؛ هي فوري نوعيت جون نٿيون لڳن.",
    ),
    TriageLevel.SELF_CARE: LocalizedText(
        en="Based on what you described, self-care at home is reasonable for now.",
        ur="آپ کی بیان کردہ معلومات کی بنیاد پر فی الحال گھر پر اپنی دیکھ بھال مناسب ہے۔",
        sd="توهان جي ٻڌايل ڳالهين جي بنياد تي هن وقت گهر ۾ پنهنجي سنڀال مناسب آهي.",
    ),
    TriageLevel.NEEDS_MORE_INFO: LocalizedText(
        en="Please answer the follow-up questions so the guidance can be completed.",
        ur="براہ کرم مزید سوالات کے جواب دیں تاکہ رہنمائی مکمل کی جا سکے۔",
        sd="مهرباني ڪري وڌيڪ سوالن جا جواب ڏيو ته جيئن رهنمائي مڪمل ٿي سگهي.",
    ),
}

_REPHRASE_MESSAGE = LocalizedText(
    en="I could not fully understand that message. Please describe the symptoms again in your own words.",
    ur="میں اس پیغام کو پوری طرح نہیں سمجھ سکا۔ براہ کرم اپنی علامات اپنے الفاظ میں دوبارہ بیان کریں۔",
    sd="مان ان پيغام کي مڪمل طور سمجهي نه سگهيس. مهرباني ڪري پنهنجون علامتون پنهنجن لفظن ۾ ٻيهر بيان ڪريو.",
)


def fallback_user_message(level: TriageLevel) -> LocalizedText:
    """Deterministic templated message: the safe fallback whenever a composed
    message is unavailable or rejected by the output-policy filter."""
    return _USER_MESSAGES[level]


def build_guidance(
    session_id: str,
    decision: TriageDecision,
    follow_up_questions: tuple[LocalizedText, ...] = (),
    *,
    user_message: LocalizedText | None = None,
    evidence: list[Citation] | None = None,
    evidence_note: LocalizedText | None = None,
) -> GuidanceResponse:
    return GuidanceResponse(
        session_id=session_id,
        user_message=user_message if user_message is not None else _USER_MESSAGES[decision.level],
        triage=decision,
        follow_up_questions=list(follow_up_questions),
        evidence=list(evidence) if evidence is not None else [],
        evidence_note=evidence_note,
        disclaimers=[DISCLAIMER],
    )


def build_rephrase_guidance(session_id: str) -> GuidanceResponse:
    """Graceful path when model output stayed unusable after one retry.

    The decision is still produced by the deterministic triage engine
    (NEEDS_MORE_INFO), never by the LLM.
    """
    placeholder = StructuredCase(chief_complaint="(awaiting rephrase)", missing_fields=["chief_complaint"])
    decision = decide(placeholder, SafetyAssessment())
    return GuidanceResponse(
        session_id=session_id,
        user_message=_REPHRASE_MESSAGE,
        triage=decision,
        follow_up_questions=[],
        evidence=[],
        disclaimers=[DISCLAIMER],
    )
