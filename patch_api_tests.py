import sys
path = 'backend/tests/test_conversation_api.py'
content = open(path).read()
new_content = content + """
def test_get_history_isolation(app_and_client):
    app, client, settings = app_and_client
    from conversation_support import case_json
    inject_orchestrator(app, settings, scripts=(case_json(), case_json()))
    
    # Session A
    resp_a = client.post("/sessions", json={"preferred_language": "en"})
    session_a = resp_a.json()["id"]
    client.post(f"/sessions/{session_a}/messages", json={"text": "message A"})
    
    # Session B
    resp_b = client.post("/sessions", json={"preferred_language": "en"})
    session_b = resp_b.json()["id"]
    client.post(f"/sessions/{session_b}/messages", json={"text": "message B"})
    
    # Retrieve A
    hist_a = client.get(f"/sessions/{session_a}/history").json()
    assert len(hist_a["messages"]) == 1
    assert hist_a["messages"][0]["text"] == "message A"
    
    # Retrieve B
    hist_b = client.get(f"/sessions/{session_b}/history").json()
    assert len(hist_b["messages"]) == 1
    assert hist_b["messages"][0]["text"] == "message B"
"""
open(path, 'w').write(new_content)
print("patched test_conversation_api.py")
