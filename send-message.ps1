$sessionId = "40f13d3556614317aa0b9b68589a2400"
$messageText = "I have a headache and fever for the past 2 days. The headache is throbbing and gets worse with light."
$messagePayload = @{text = $messageText} | ConvertTo-Json
$msgResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/sessions/$sessionId/messages" -Method Post -UseBasicParsing -ContentType 'application/json' -Body $messagePayload -ErrorAction Stop
$msgData = $msgResponse.Content | ConvertFrom-Json
Write-Host "Guidance Response:" -ForegroundColor Green
$msgData | ConvertTo-Json -Depth 20
