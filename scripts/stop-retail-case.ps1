[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$processFile=Join-Path $root 'runtime\install\private\processes.json'
if (-not (Test-Path -LiteralPath $processFile)) { Write-Host 'No managed application processes.'; exit 0 }
$entries=@(Get-Content -Raw -Encoding UTF8 -LiteralPath $processFile | ConvertFrom-Json)
foreach ($entry in $entries) {
    $process=Get-Process -Id $entry.pid -ErrorAction SilentlyContinue
    if ($process -and $process.StartTime.ToUniversalTime().ToString('o') -eq $entry.startedAt) {
        & taskkill.exe /PID $entry.pid /T /F | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Unable to stop managed component $($entry.component)." }
        Write-Host "Stopped: $($entry.component)"
    }
}
Remove-Item -LiteralPath $processFile
Write-Host 'Oracle Windows service remains running; database data retained.'
