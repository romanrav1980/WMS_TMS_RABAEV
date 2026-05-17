[CmdletBinding()]
param(
  [switch]$All,
  [switch]$Api,
  [switch]$Front,
  [switch]$Terminal,
  [switch]$Worker
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not ($All -or $Api -or $Front -or $Terminal -or $Worker)) {
  $All = $true
}

$killPort = Join-Path $PSScriptRoot "kill-port.ps1"
if (-not (Test-Path -LiteralPath $killPort -PathType Leaf)) {
  throw "kill-port.ps1 was not found: $killPort"
}

function Stop-WmsListener {
  param(
    [string]$Name,
    [int[]]$Port = @(),
    [string[]]$Pattern = @()
  )

  Write-Host "Stopping $Name listener(s)..." -ForegroundColor Cyan
  $args = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $killPort, "-WaitSeconds", "2")
  foreach ($item in $Port) {
    $args += @("-Port", [string]$item)
  }
  foreach ($item in $Pattern) {
    $args += @("-CommandLineLike", $item)
  }
  & powershell.exe @args
  if ($LASTEXITCODE -ne 0) {
    throw "$Name listener cleanup failed."
  }
}

if ($All -or $Api) {
  Stop-WmsListener `
    -Name "API" `
    -Port @(8088) `
    -Pattern @("*uvicorn app.main:app*--port 8088*")
}

if ($All -or $Front) {
  Stop-WmsListener `
    -Name "admin frontend" `
    -Port @(3000) `
    -Pattern @("*http.server 3000*", "*--port 3000*")
}

if ($All -or $Terminal) {
  Stop-WmsListener `
    -Name "terminal frontend" `
    -Port @(3010) `
    -Pattern @("*--port 3010*")
}

if ($All -or $Worker) {
  Stop-WmsListener `
    -Name "outbox worker" `
    -Pattern @("*app.workers.outbox_worker*")
}

Write-Host "Listener cleanup completed." -ForegroundColor Green
