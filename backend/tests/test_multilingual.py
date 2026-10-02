from __future__ import annotations
import asyncio
import json
import hashlib
from app.llm.mock import MockProvider
from app.extraction.service import ExtractionService
from app.models import Language

EN_TEXT = "severe headache and fever"
UR_TEXT = "شدید سر درد اور بخار"
SD_TEXT = "سخت مٿي جو سور ۽ بخار"
MIXED_TEXT = "headache and بخار"

# The mock LLM acts as the ideal extraction model returning structured JSON.
# We configure it to return the exact same structured case regardless of language.
COMMON_CASE = {
    "chief_complaint": "headache and fever",
    "symptoms": [
        {
            "name": "headache",
            "body_system": "neurological",
            "severity": None,
            "progression": "unknown",
            "duration": None,
        },
        {
            "name": "fever",
            "body_system": "systemic",
            "severity": None,
            "progression": "unknown",
            "duration": None,
        }
    ],
    "demographics": {"age_group": None, "pregnant": None},
    "associated_factors": [],
    "red_flag_signals": [],
    "missing_fields": ["demographics.age_group", "symptoms[0].severity"],
    "confidence": 0.85,
    "raw_excerpt": ""
}

def _service(json_response: dict) -> tuple[ExtractionService, MockProvider]:
    provider = MockProvider(scripts=[json.dumps(json_response)])
    return ExtractionService(provider), provider

def test_multilingual_structured_extraction_yields_same_case() -> None:
    """Equivalent concepts in EN/UR/SD map to the same validated StructuredCase fields."""
    for text in (EN_TEXT, UR_TEXT, SD_TEXT, MIXED_TEXT):
        case_data = dict(COMMON_CASE, raw_excerpt=text)
        service, provider = _service(case_data)
        outcome = asyncio.run(service.extract(text))
        
        assert outcome.case is not None
        assert outcome.case.symptoms[0].name == "headache"
        assert outcome.case.symptoms[1].name == "fever"
        assert outcome.case.missing_fields == ["demographics.age_group", "symptoms[0].severity"]
        
        # Verify language text reached the prompt verbatim
        assert text in provider.requests[0].messages[-1].content
        
        # Verify Unicode input hashing is stable for traces
        expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert outcome.trace.input_hash == expected_hash

def test_multilingual_extraction_maintains_schema_validation() -> None:
    """Multilingual text cannot bypass schema validation rules."""
    invalid_case = dict(COMMON_CASE, raw_excerpt=UR_TEXT, symptoms=[{"name": ""}]) # invalid symptom
    
    # We provide 1 invalid script, and 1 valid script to test retry
    valid_case = dict(COMMON_CASE, raw_excerpt=UR_TEXT)
    provider = MockProvider(scripts=[json.dumps(invalid_case), json.dumps(valid_case)])
    service = ExtractionService(provider)
    
    outcome = asyncio.run(service.extract(UR_TEXT))
    
    assert outcome.case is not None
    assert outcome.trace.llm_calls[0].valid is False
    assert outcome.trace.llm_calls[1].valid is True

def test_followup_phrasing_uses_language_appropriately() -> None:
    from app.conversation.followups import FollowUpPhraser
    from app.llm.trace import TraceCollector
    
    # We provide a mock LLM that returns a JSON list with one question
    provider_ur = MockProvider(scripts=['["درد کتنا ہے؟"]'])
    phraser_ur = FollowUpPhraser(provider_ur)
    collector = TraceCollector(step="followup", input_hash="hash")
    
    q_ur, used_fallback = asyncio.run(phraser_ur.phrase(["symptoms[0].severity"], Language.UR, collector))
    assert not used_fallback
    assert len(q_ur) == 1
    # Check that localized text was constructed with english fallback (or empty) and urdu output
    assert q_ur[0].ur == "درد کتنا ہے؟"
    assert q_ur[0].en != "درد کتنا ہے؟"
    
    provider_sd = MockProvider(scripts=['["سور ڪيترو آهي؟"]'])
    phraser_sd = FollowUpPhraser(provider_sd)
    q_sd, used_fallback_sd = asyncio.run(phraser_sd.phrase(["symptoms[0].severity"], Language.SD, collector))
    assert not used_fallback_sd
    assert len(q_sd) == 1
    assert q_sd[0].sd == "سور ڪيترو آهي؟"

def test_fallback_questions_provide_all_languages() -> None:
    from app.conversation.followups import _fallback_questions
    
    fallbacks = _fallback_questions(["symptoms"])
    assert len(fallbacks) == 1
    # Check that localized text contains EN, UR, SD for known field
    assert fallbacks[0].en
    assert fallbacks[0].ur
    assert fallbacks[0].sd
    
    # Check that unknown fields also generate localized texts dynamically
    unknown = _fallback_questions(["some.unknown.field"])
    assert unknown[0].en == "Can you tell me more about: some.unknown.field?"
    assert unknown[0].ur
    assert unknown[0].sd
