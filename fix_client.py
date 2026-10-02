import re

with open('frontend/src/api/client.ts', 'r') as f:
    content = f.read()

content = content.replace('request<GuidanceResponse>(`/v1/conversation/message`,', 'request<GuidanceResponse>(`${BASE}/v1/conversation/message`,')
content = content.replace('request<any>(`/v1/clinical/summary/', 'request<any>(`${BASE}/v1/clinical/summary/')
content = content.replace('request<SessionListItem[]>(`/v1/history/sessions`);', 'request<SessionListItem[]>(`${BASE}/v1/history/sessions`);')

with open('frontend/src/api/client.ts', 'w') as f:
    f.write(content)

