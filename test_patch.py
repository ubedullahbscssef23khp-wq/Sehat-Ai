with open('backend/tests/test_safety_invariants.py', 'r') as f:
    c = f.read()
c = c.replace('incomplete_case_json,\n    make_pattern,', 'incomplete_case_json,\n    questions_json,\n    make_pattern,')
with open('backend/tests/test_safety_invariants.py', 'w') as f:
    f.write(c)
