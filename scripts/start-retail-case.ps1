[CmdletBinding()]
param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
. (Join-Path $PSScriptRoot 'retail_case_install\common.ps1')
$paths = Get-InstallPaths $root
if (-not (Test-Path -LiteralPath $paths.State)) { throw 'Run INSTALL-RETAIL-CASE.cmd first.' }
$state = Get-Content -Raw -Encoding UTF8 -LiteralPath $paths.State | ConvertFrom-Json
if (-not $state.complete) { throw "Installation is incomplete: $($state.phase)." }
$secrets = Get-Content -Raw -Encoding UTF8 -LiteralPath $paths.Secrets | ConvertFrom-Json
$schema = ConvertTo-PlainSecret ($secrets.schema | ConvertTo-SecureString)
$admin = ConvertTo-PlainSecret ($secrets.applicationAdmin | ConvertTo-SecureString)
$processFile = Join-Path $paths.Private 'processes.json'
$known = @()
if (Test-Path -LiteralPath $processFile) { $known = @(Get-Content -Raw -Encoding UTF8 -LiteralPath $processFile | ConvertFrom-Json) }
$components = @(@{name='Api';port=8088},@{name='Admin';port=3000},@{name='Terminal';port=3010})
$running = @{}
foreach ($component in $components) {
    $entry = @($known | Where-Object { $_.component -eq $component.name }) | Select-Object -First 1
    $process = $null
    if ($entry) { $process = Get-Process -Id $entry.pid -ErrorAction SilentlyContinue }
    $owned = $process -and ($process.StartTime.ToUniversalTime().ToString('o') -eq $entry.startedAt)
    if ((Test-LocalPort $component.port) -and -not $owned) { throw "Port $($component.port) belongs to another process. No existing application will be stopped." }
    $running[$component.name] = $owned
}
try {
    $env:WMS_ORACLE_USER='RABAEV'; $env:WMS_ORACLE_PASSWORD=$schema; $env:WMS_ORACLE_DSN=$state.dsn
    $env:TMS_API_BIND_HOST='127.0.0.1'; $env:TMS_TERMINAL_BIND_HOST='127.0.0.1'
    $env:WMS_CORS_ORIGINS='http://127.0.0.1:3000,http://localhost:3000,http://127.0.0.1:3010,http://localhost:3010'
    $env:VITE_ADMIN_BASIC_AUTH='admin:'+$admin
    $env:TMS_PYTHON_CMD=$paths.Python
    $newEntries = @()
    foreach ($component in $components) {
        if ($running[$component.name]) {
            $newEntries += @($known | Where-Object { $_.component -eq $component.name }) | Select-Object -First 1
            continue
        }
        $worker = Join-Path $PSScriptRoot 'retail_case_install\run_component.ps1'
        $log = Join-Path $paths.Private ($component.name.ToLowerInvariant()+'.log')
        $errLog = Join-Path $paths.Private ($component.name.ToLowerInvariant()+'.error.log')
        $args = '-NoProfile -ExecutionPolicy Bypass -File "'+$worker+'" -Component '+$component.name
        $process = Start-Process -FilePath (Join-Path $PSHOME 'powershell.exe') -ArgumentList $args -WorkingDirectory $root -WindowStyle Hidden -RedirectStandardOutput $log -RedirectStandardError $errLog -PassThru
        $newEntries += [ordered]@{component=$component.name;pid=$process.Id;startedAt=$process.StartTime.ToUniversalTime().ToString('o')}
    }
    ConvertTo-Json -InputObject @($newEntries) -Depth 5 | Set-Content -LiteralPath $processFile -Encoding UTF8
    $deadline = [DateTime]::UtcNow.AddSeconds(90)
    $ready = $false
    do {
        Start-Sleep -Seconds 2
        try {
            $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8088/health' -TimeoutSec 3
            $ping = Invoke-RestMethod -Uri 'http://127.0.0.1:8088/db/ping' -TimeoutSec 5
            $ready = ($health.status -eq 'ok') -and (Test-LocalPort 3000) -and (Test-LocalPort 3010)
        } catch { $ready=$false }
    } until ($ready -or [DateTime]::UtcNow -gt $deadline)
    if (-not $ready) { throw "Application did not become ready. Logs: $($paths.Private). Oracle has not been reinstalled." }
    Write-Host 'retailcase: http://127.0.0.1:3000'
    Write-Host 'Terminal: http://127.0.0.1:3010 | API: http://127.0.0.1:8088/docs'
    if (-not $NoBrowser) { Start-Process 'http://127.0.0.1:3000' }
} finally {
    foreach ($name in @('WMS_ORACLE_PASSWORD','VITE_ADMIN_BASIC_AUTH')) { [Environment]::SetEnvironmentVariable($name,$null,'Process') }
    $schema=$null; $admin=$null
}
