import sys
path = 'backend/tests/test_conversation_api.py'
content = open(path).read()
new_content = content + """
def test_history_does_not_invoke_llm_or_triage(app_and_client):
    app, client, settings = app_and_client
    from unittest.mock import patch
    
    resp = client.post("/sessions", json={"preferred_language": "en"})
    session_id = resp.json()["id"]
    
    with patch("app.api.conversation.ConversationOrchestrator") as mock_orch:
        hist_resp = client.get(f"/sessions/{session_id}/history")
        assert hist_resp.status_code == 200
        # Check that no LLM or triage actions occurred
        # History is fetched through SessionRepository directly in API, not orchestrator
        mock_orch.assert_not_called()
"""
open(path, 'w').write(new_content)
print("patched test_conversation_api.py")
