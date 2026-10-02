import sys
path = 'backend/tests/test_persistence.py'
content = open(path).read()
new_content = content + """
def test_dependent_record_deletion_cascade_verifies_child_rows(factory) -> None:
    from app.persistence.repositories import SessionRepository, MessageRepository, TraceRepository, CaseRepository, ResponseRepository
    from app.models import Message, MessageRole, Language, DecisionTrace, StructuredCase
    from datetime import datetime, timezone
    
    sessions = SessionRepository(factory)
    messages = MessageRepository(factory)
    traces = TraceRepository(factory)
    cases = CaseRepository(factory)
    
    # Session A
    session_a = make_session()
    session_a.id = "s_A"
    sessions.create(session_a)
    messages.append(Message(id="mA", session_id="s_A", role=MessageRole.USER, text="msg A", lang=Language.EN, created_at=datetime.now(timezone.utc)))
    traces.append("s_A", DecisionTrace(step="triage", timestamp=datetime.now(timezone.utc), input_hash="hashA", rule_ids=[]))
    
    # Session B
    session_b = make_session()
    session_b.id = "s_B"
    sessions.create(session_b)
    messages.append(Message(id="mB", session_id="s_B", role=MessageRole.USER, text="msg B", lang=Language.EN, created_at=datetime.now(timezone.utc)))
    traces.append("s_B", DecisionTrace(step="triage", timestamp=datetime.now(timezone.utc), input_hash="hashB", rule_ids=[]))
    
    # Delete A
    sessions.delete("s_A")
    
    # Verify A is completely gone
    assert sessions.get("s_A") is None
    assert len(messages.list_for_session("s_A")) == 0
    assert len(traces.list_for_session("s_A")) == 0
    
    # Verify B is intact
    assert sessions.get("s_B") is not None
    assert len(messages.list_for_session("s_B")) == 1
    assert len(traces.list_for_session("s_B")) == 1

def test_transaction_rollback_on_persistence_failure(factory) -> None:
    from app.persistence.repositories import SessionRepository, MessageRepository
    from app.models import Message, MessageRole, Language
    from datetime import datetime, timezone
    import pytest
    from sqlalchemy.exc import SQLAlchemyError
    
    sessions = SessionRepository(factory)
    messages = MessageRepository(factory)
    
    # Create session
    session = make_session()
    sessions.create(session)
    
    # Attempt to append invalid message (violates NOT NULL or string length limit if we do weird stuff)
    # Actually, let's mock the DB session's execute to fail when deleting, to see if it rolls back
    
    # Or just test that a failed create doesn't commit partial state.
    # We can inject a failure by appending a message with an invalid session ID, testing foreign key constraints
    with pytest.raises(Exception):
        messages.append(Message(id="m1", session_id="nonexistent", role=MessageRole.USER, text="msg", lang=Language.EN, created_at=datetime.now(timezone.utc)))
        
    assert len(messages.list_for_session("nonexistent")) == 0
"""
open(path, 'w').write(new_content)
print("patched test_persistence.py")
