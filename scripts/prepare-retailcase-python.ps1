param(
    [string]$Destination = 'api\wms_api_server\.venv',
    [string]$Wheelhouse = '',
    [string]$PythonCommand = 'python.exe'
)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$target = [IO.Path]::GetFullPath((Join-Path $repoRoot $Destination))
if (-not $target.StartsWith($repoRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'NS00 venv must remain in the repository.' }
if (Test-Path -LiteralPath $target) { throw 'Choose an empty destination; existing environments are never deleted.' }
& $PythonCommand -c "import sys,platform; assert sys.version_info[:2]==(3,13) and sys.platform=='win32' and platform.machine().lower() in ('amd64','x86_64'), 'NS00 lock targets Windows x64 Python 3.13'"
if ($LASTEXITCODE -ne 0) { throw 'Python does not match the tested lock platform.' }
& $PythonCommand -m venv $target
if ($LASTEXITCODE -ne 0) { throw 'venv creation failed.' }
$venvPython = Join-Path $target 'Scripts\python.exe'
$lock = Join-Path $repoRoot 'api\wms_api_server\requirements-ns00-win-py313.lock'
$pipArgs = @('-m','pip','install','--require-hashes','-r',$lock)
if ($Wheelhouse) {
    $wheels = [IO.Path]::GetFullPath((Join-Path $repoRoot $Wheelhouse))
    if (-not $wheels.StartsWith($repoRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Wheelhouse must remain in the repository.' }
    $pipArgs += @('--no-index','--find-links',$wheels)
}
Push-Location $repoRoot
try {
    & $venvPython @pipArgs
    if ($LASTEXITCODE -ne 0) { throw 'Pinned dependency installation failed.' }
    & $venvPython -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency failed.' }
    & $venvPython -c "import api.wms_api_server.app.main; print('Fresh API import PASS')"
    if ($LASTEXITCODE -ne 0) { throw 'Fresh API import failed.' }
} finally { Pop-Location }
@{python=$venvPython;lockSha256=(Get-FileHash -LiteralPath $lock -Algorithm SHA256).Hash;systemSitePackages=$false;dependencyCheck='PASS';apiImport='PASS'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $target 'ns00-install-report.json') -Encoding UTF8
Write-Host 'NS00 isolated Python installation PASS'
