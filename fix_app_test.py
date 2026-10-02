import re

with open('frontend/src/__tests__/App.test.tsx', 'r') as f:
    content = f.read()

content = re.sub(r'vi\.mocked\(\/\/ client\.createSession\).*?\n', '', content)
content = re.sub(r'expect\(\/\/ client\.createSession\).*?\n', '', content)
content = re.sub(r'vi\.mocked\(client\.v1SendMessage\)', 'vi.mocked(client.v1SendMessage as any)', content)

# ensure v1GetHistorySessions is mocked
if 'v1GetHistorySessions' not in content:
    content = content.replace('const actual = await importOriginal<typeof import("../api/client")>();', 'const actual = await importOriginal<typeof import("../api/client")>();\n  return { ...actual, v1GetHistorySessions: vi.fn().mockResolvedValue([]), v1GetClinicalSummary: vi.fn().mockResolvedValue(null), v1SendMessage: vi.fn() };')

with open('frontend/src/__tests__/App.test.tsx', 'w') as f:
    f.write(content)
