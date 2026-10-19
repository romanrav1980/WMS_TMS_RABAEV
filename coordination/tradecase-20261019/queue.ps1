param([Parameter(Mandatory=$true)][ValidateSet('analysis','execute','stop')][string]$Phase)
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$deadline = [DateTimeOffset]::Parse('2026-10-19T18:00:00+03:00')
if ($Phase -ne 'stop' -and [DateTimeOffset]::UtcNow -ge $deadline) { exit 0 }
if ($Phase -eq 'stop' -and (Test-Path -LiteralPath (Join-Path $taskRoot 'DONE.json'))) {
    $done = Get-Content -LiteralPath (Join-Path $taskRoot 'DONE.json') -Encoding UTF8 -Raw | ConvertFrom-Json
    if ($done.status -eq 'complete') { exit 0 }
}
$codexPath = 'C:\Users\roma\.vscode\extensions\openai.chatgpt-26.930.61225-win32-x64\bin\windows-x86_64\codex.exe'
$thread = '01a13c0f-ad67-70f3-91bc-4e3d5b4bf93e'
$message = Get-Content -LiteralPath (Join-Path $taskRoot ($Phase + '.txt')) -Encoding UTF8 -Raw
Set-Location -LiteralPath 'C:\projects\TMS'
for ($attempt=1; $attempt -le 3; $attempt++) {
    $savedPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = & $codexPath queue --thread $thread --message $message 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $savedPreference
    @((Get-Date -Format o), ('phase=' + $Phase + ' attempt=' + $attempt + ' exit=' + $code), $output) | Out-File -LiteralPath (Join-Path $taskRoot ($Phase + '-queue.log')) -Encoding UTF8 -Append
    if ($code -eq 0) { exit 0 }
    Start-Sleep -Seconds 5
}
exit 1
