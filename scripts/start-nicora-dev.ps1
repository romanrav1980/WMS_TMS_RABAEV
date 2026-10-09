param(
    [string]$PythonExe = 'api\wms_api_server\.venv\Scripts\python.exe',
    [string]$FrontendRoot = 'tmp\nicora_ns00_install\frontends_online',
    [string]$Evidence = 'runtime\test-evidence\nicora_ns00',
    [switch]$Restart
)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
function Resolve-ProjectPath([string]$Relative) {
    $resolved = [IO.Path]::GetFullPath((Join-Path $repoRoot $Relative))
    if (-not $resolved.StartsWith($repoRoot+'\',[StringComparison]::OrdinalIgnoreCase)) {
        throw 'Prepared dependencies and evidence must remain in the workspace.'
    }
    return $resolved
}
$preparedPython = Resolve-ProjectPath $PythonExe
$preparedFrontends = Resolve-ProjectPath $FrontendRoot
$evidenceRoot = Resolve-ProjectPath $Evidence
if (-not (Test-Path -LiteralPath $preparedPython)) { throw 'Run the NS00 Python preparation first.' }
foreach ($relative in @('admin\wms_admin_frontend','terminal\wms_terminal_web')) {
    if (-not (Test-Path -LiteralPath (Join-Path $preparedFrontends "$relative\node_modules\vite\bin\vite.js"))) {
        throw "Prepared frontend dependencies missing: $relative"
    }
}
New-Item -ItemType Directory -Path $evidenceRoot -Force | Out-Null
$ports = @(8088,3000,3010)
$before = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in $ports } | Select-Object LocalPort,OwningProcess)
if ($Restart) {
    & (Join-Path $repoRoot 'scripts\kill-port.ps1') -Port $ports -CommandLineLike '*uvicorn app.main:app*--port 8088*' -WaitSeconds 2 -FailIfBusy
    if ($LASTEXITCODE -ne 0) { throw 'Previous processes could not be stopped.' }
    $left = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in $ports })
    if ($left.Count) { throw 'A listener survived shutdown.' }
} elseif ($before.Count) { throw 'Use -Restart to explicitly replace the existing dev applications.' }
$env:TMS_PYTHON_CMD = $preparedPython
$env:TMS_ADMIN_FRONTEND_DIR = Join-Path $preparedFrontends 'admin\wms_admin_frontend'
$env:TMS_TERMINAL_FRONTEND_DIR = Join-Path $preparedFrontends 'terminal\wms_terminal_web'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$launches = @()
foreach ($entry in @('serv.bat','front.bat','terminal.bat')) {
    $output = Join-Path $evidenceRoot "$stamp-$entry.stdout.log"
    $errors = Join-Path $evidenceRoot "$stamp-$entry.stderr.log"
    $process = Start-Process -FilePath $env:ComSpec -ArgumentList @('/d','/c',('"'+(Join-Path $repoRoot $entry)+'"')) -WorkingDirectory $repoRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput $output -RedirectStandardError $errors
    $launches += @{launcher=$entry;wrapperPid=$process.Id;stdout=$output;stderr=$errors}
}
$ready = $false
for ($attempt=0; $attempt -lt 45; $attempt++) {
    $checks = @()
    foreach ($url in @('http://127.0.0.1:8088/health','http://127.0.0.1:3000','http://127.0.0.1:3010')) {
        try { $checks += (Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2).StatusCode -eq 200 }
        catch { $checks += $false }
    }
    if ($checks -notcontains $false) { $ready=$true; break }
    Start-Sleep -Milliseconds 750
}
if (-not $ready) { throw 'Startup failed; inspect the saved launcher logs.' }
$after = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -in $ports } | Select-Object LocalPort,OwningProcess)
if ($Restart) {
    foreach ($old in $before) {
        if ($after.OwningProcess -contains $old.OwningProcess) { throw 'A former listener PID was reused without restart evidence.' }
    }
}
@{before=$before;after=$after;allPortsStoppedBeforeStart=[bool]$Restart;launches=$launches;python=$preparedPython;frontends=$preparedFrontends;ready=$ready} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $evidenceRoot "launch-$stamp.json") -Encoding UTF8
Write-Host 'NS00 prepared API/ARM/TSD launch PASS'
