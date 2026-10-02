from backend.app.safety.prescreen import normalize_query

q = "b\u00e9fast"
print(q)
print(normalize_query(q))
