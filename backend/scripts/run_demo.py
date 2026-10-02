import sys
import json
import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

# Add backend directory and tests directory to python path
backend_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "tests"))

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.main import create_app
from app.core.config import Settings
from app.persistence.database import build_engine, init_db
from app.models import ReviewStatus, SafetyLevel, SessionStatus, KnowledgeEntry, RedFlagRule, EmergencyPattern
from app.triage.engine import TriageLevel

# Import testing support
from tests.test_conversation_api import inject_orchestrator
from tests.conversation_support import (
    case_json,
    incomplete_case_json,
    questions_json,
    make_knowledge_entry,
    make_pattern,
    make_signal_rule,
)
import app.safety.signals as signals
from app.llm.provider import LLMUnavailableError
from app.llm.mock import MockProvider

def print_result(name: str, passed: bool):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name}")

def run_scenarios():
    passed_count = 0
    total_count = 8
    
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "demo.sqlite"
        settings = Settings(
            sehat_env="development",
            sehat_llm_provider="mock",
            sehat_db_path=db_path,
            _env_file=None,
        )
        
        # Init DB
        engine = build_engine(db_path)
        init_db(engine)
        
        app = create_app(settings=settings)
        client = TestClient(app)
        
        # Scenario A: english_normal
        try:
            inject_orchestrator(
                app, settings,
                scripts=(
                    case_json(chief_complaint="mild headache", age_group="adult"),
                    '{"response": "Guidance text"}'
                )
            )
            
            resp = client.post("/sessions", json={"preferred_language": "en"})
            assert resp.status_code in (200, 201), resp.text
            session_id = resp.json()["id"]
            
            resp = client.post(f"/sessions/{session_id}/messages", json={"text": "I have a mild headache. I am 30 years old. I am not pregnant."})
            assert resp.status_code in (200, 201), resp.text
            data = resp.json()
            if data["triage"]["level"] == "needs_more_info":
                raise AssertionError(f"Expected final triage, got needs_more_info. Data: {data}")
            assert "clinician_summary" in data and data["clinician_summary"] is not None
            assert len(data["disclaimers"]) > 0
            
            print_result("A — English normal", True)
            passed_count += 1
        except Exception as e:
            print_result("A — English normal", False)
            print(f"  Error: {e}")

        # Scenario B: missing_information
        try:
            inject_orchestrator(
                app, settings,
                scripts=(
                    incomplete_case_json(missing_age=True),
                    questions_json(1),
                    case_json(chief_complaint="mild headache", age_group="adult"),
                    '{"response": "Guidance text"}'
                )
            )
            resp = client.post("/sessions", json={"preferred_language": "en"})
            session_id = resp.json()["id"]
            
            resp = client.post(f"/sessions/{session_id}/messages", json={"text": "I have a mild headache"})
            assert resp.status_code in (200, 201)
            data = resp.json()
            if data["triage"]["level"] != "needs_more_info":
                raise AssertionError(f"Expected needs_more_info, got {data['triage']['level']}")
            
            resp = client.post(f"/sessions/{session_id}/messages", json={"text": "I am 30 years old."})
            assert resp.status_code in (200, 201)
            data = resp.json()
            if data["triage"]["level"] == "needs_more_info":
                raise AssertionError("Expected final triage")
            
            print_result("B — Missing information", True)
            passed_count += 1
        except Exception as e:
            print_result("B — Missing information", False)
            print(f"  Error: {e}")
            
        # Scenario C: emergency_safety_test_only
        try:
            class FailingMockProvider(MockProvider):
                async def complete(self, request):
                    raise AssertionError("LLM should not be called on emergency prescreen match")
                async def extract(self, text, history=None):
                    raise AssertionError("LLM should not be called on emergency prescreen match")
            
            from app.conversation.orchestrator import ConversationOrchestrator
            session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
            test_pattern = make_pattern(pattern_id="TEST-EMERG", text="sudden vision change")
            
            app.state.orchestrator = ConversationOrchestrator(
                provider=FailingMockProvider(),
                session_factory=session_factory,
                rules=[],
                prescreen_patterns=[test_pattern],
                max_followup_rounds=settings.sehat_max_followup_rounds,
                knowledge=[],
            )
            
            resp = client.post("/sessions", json={"preferred_language": "en"})
            session_id = resp.json()["id"]
            
            resp = client.post(f"/sessions/{session_id}/messages", json={"text": "sudden vision change"})
            assert resp.status_code in (200, 201)
            data = resp.json()
            if data["triage"]["level"] != "emergency":
                raise AssertionError("Expected emergency")
            
            print_result("C — Emergency safety (test-only)", True)
            passed_count += 1
        except Exception as e:
            print_result("C — Emergency safety (test-only)", False)
            print(f"  Error: {e}")

        # Scenario D: urdu
        try:
            inject_orchestrator(
                app, settings,
                scripts=(
                    case_json(chief_complaint="مجھے ہلکا سر درد ہے"),
                    '{"response": "رہنمائی کا متن"}'
                )
            )
            resp = client.post("/sessions", json={"preferred_language": "ur"})
            session_id = resp.json()["id"]
            
            resp = client.post(f"/sessions/{session_id}/messages", json={"text": "مجھے ہلکا سر درد ہے۔ میں 30 سال کا ہوں، حاملہ نہیں ہوں۔"})
            assert resp.status_code in (200, 201)
            data = resp.json()
            assert data["triage"]["level"] != "needs_more_info"
            
            print_result("D — Urdu", True)
            passed_count += 1
        except Exception as e:
            print_result("D — Urdu", False)
            print(f"  Error: {e}")
            
        # Scenario E: sindhi
        try:
            inject_orchestrator(
                app, settings,
                scripts=(
                    case_json(chief_complaint="مون کي هلڪو مٿي جو سور آهي"),
                    '{"response": "رهنمائي جو متن"}'
                )
            )
            resp = client.post("/sessions", json={"preferred_language": "sd"})
            session_id = resp.json()["id"]
            
            resp = client.post(f"/sessions/{session_id}/messages", json={"text": "مون کي هلڪو مٿي جو سور آهي."})
            assert resp.status_code in (200, 201)
            data = resp.json()
            assert data["triage"]["level"] != "needs_more_info"
            
            print_result("E — Sindhi", True)
            passed_count += 1
        except Exception as e:
            print_result("E — Sindhi", False)
            print(f"  Error: {e}")

        # Scenario F: knowledge_governance
        try:
            from app.knowledge.loader import load_entries_dir
            
            
            kb_dir = Path(tmpdir) / "kb"
            kb_dir.mkdir()
            
            approved = make_knowledge_entry(entry_id="K-APP-1")
            
            approved_md = f"""---
id: {approved.id}
title: {approved.title}
terms:
  - {approved.terms[0]}
source: {approved.source}
date_reviewed: '{approved.date_reviewed.isoformat()}'
review_status: approved
content_hash: '{approved.content_hash}'
---
{approved.content}"""
            (kb_dir / "k1.md").write_text(approved_md)
            
            pending = make_knowledge_entry(entry_id="K-PEN-1")
            pending_md = f"""---
id: {pending.id}
title: {pending.title}
terms:
  - {pending.terms[0]}
source: {pending.source}
date_reviewed: '{pending.date_reviewed.isoformat()}'
review_status: pending_domain_review
content_hash: '{pending.content_hash}'
---
{pending.content}"""
            (kb_dir / "k2.md").write_text(pending_md)
            
            # Load entries
            loaded = load_entries_dir(kb_dir)
            assert len(loaded) == 1
            assert loaded[0].id == "K-APP-1"
            
            print_result("F — Knowledge governance", True)
            passed_count += 1
        except Exception as e:
            print_result("F — Knowledge governance", False)
            print(f"  Error: {e}")
            
        # Scenario G: clinician_summary
        try:
            inject_orchestrator(
                app, settings,
                scripts=(
                    case_json(chief_complaint="mild headache", age_group="adult"),
                    '{"response": "Guidance text"}'
                )
            )
            resp = client.post("/sessions", json={"preferred_language": "en"})
            session_id = resp.json()["id"]
            resp = client.post(f"/sessions/{session_id}/messages", json={"text": "I have a mild headache."})
            data = resp.json()
            summary = data.get("clinician_summary", {})
            assert "structured_case" in summary
            assert "chief_complaint" in summary["structured_case"]
            assert "symptoms" in summary["structured_case"]
            assert "timeline" in summary
            assert "model_attribution" not in summary or summary["model_attribution"] is None
            
            print_result("G — Clinician summary", True)
            passed_count += 1
        except Exception as e:
            print_result("G — Clinician summary", False)
            print(f"  Error: {e}")

        # Scenario H: provider_failure
        try:
            inject_orchestrator(
                app, settings,
                scripts=()
            )
            resp = client.post("/sessions", json={"preferred_language": "en"})
            session_id = resp.json()["id"]
            resp = client.post(f"/sessions/{session_id}/messages", json={"text": "I have a mild headache."})
            
            assert resp.status_code == 503
            assert "error" in resp.json()
            
            print_result("H — Provider failure", True)
            passed_count += 1
        except Exception as e:
            print_result("H — Provider failure", False)
            print(f"  Error: {e}")

    print(f"\n{passed_count}/{total_count} scenarios passed")
    sys.exit(0 if passed_count == total_count else 1)

if __name__ == "__main__":
    print("==================================================")
    print("SehatAI Deterministic Demo Runner")
    print("==================================================")
    run_scenarios()
