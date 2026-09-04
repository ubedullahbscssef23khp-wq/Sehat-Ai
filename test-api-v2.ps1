# Phase 10 API Runtime Test - Version 2

# Section 3.2: Create Session (English)
Write-Host "=== Section 3.2: Create Session (English) ===" -ForegroundColor Cyan
$payload = ConvertTo-Json @{ preferred_language = 'en' }
Write-Host "Request: $payload" -ForegroundColor Gray
$response = Invoke-WebRequest -Uri http://127.0.0.1:8000/sessions -Method Post -UseBasicParsing -ContentType 'application/json' -Body $payload -ErrorAction Stop
$sessionData = $response.Content | ConvertFrom-Json
$sessionId = $sessionData.id
Write-Host "Session Created:" -ForegroundColor Green
Write-Host ($sessionData | ConvertTo-Json -Depth 10)

# Section 3.3: Send first message in English (symptom description)
Write-Host "`n=== Section 3.3: First Message (English) ===" -ForegroundColor Cyan
$messagePayload = ConvertTo-Json @{ text = 'I have a headache and fever for the past 2 days. The headache is throbbing and gets worse with light.' }
Write-Host "Request: $messagePayload" -ForegroundColor Gray
$msgResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/sessions/$sessionId/messages" -Method Post -UseBasicParsing -ContentType 'application/json' -Body $messagePayload -ErrorAction Stop
$msgData = $msgResponse.Content | ConvertFrom-Json
Write-Host "Guidance Response:" -ForegroundColor Green
Write-Host ($msgData | ConvertTo-Json -Depth 10)

# Check for clinician_summary
Write-Host "`n=== Clinician Summary Check ===" -ForegroundColor Cyan
if ($null -ne $msgData.clinician_summary) {
    Write-Host "[PASS] clinician_summary IS PRESENT" -ForegroundColor Green
    Write-Host ($msgData.clinician_summary | ConvertTo-Json -Depth 10)
} else {
    Write-Host "[FAIL] clinician_summary IS NULL" -ForegroundColor Red
}

# Save session ID for later use
Write-Host "`n[INFO] Session ID: $sessionId"
$sessionId | Out-File -FilePath "d:\Sehat-Ai\session-id.txt" -Encoding UTF8
