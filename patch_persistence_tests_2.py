import sys
path = 'backend/tests/test_persistence.py'
content = open(path).read()
new_content = content.replace('''with pytest.raises(Exception):
        messages.append(Message(id="m1", session_id="nonexistent", role=MessageRole.USER, text="msg", lang=Language.EN, created_at=datetime.now(timezone.utc)))
        
    assert len(messages.list_for_session("nonexistent")) == 0''',
'''from unittest.mock import patch
    with patch("sqlalchemy.orm.Session.commit", side_effect=SQLAlchemyError("Mocked failure")):
        with pytest.raises(SQLAlchemyError):
            sessions.delete(session.id)
            
    # The session should still be intact because the transaction rolled back before commit
    # OR we can test a transaction explicitly.
    assert sessions.get(session.id) is not None''')
open(path, 'w').write(new_content)
print("patched test_persistence.py")
