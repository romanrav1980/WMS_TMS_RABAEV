[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$Actor,
  [ValidateRange(1,60)][int]$Interval=2
)
$ErrorActionPreference="Stop"
$projectRoot=(Resolve-Path (Join-Path $PSScriptRoot "..")).ProviderPath
$workerPath=Join-Path $PSScriptRoot "short_recovery_worker.py"
$pythonPath=Join-Path $projectRoot "api\wms_api_server\.venv\Scripts\python.exe"
$logFolder=Join-Path $projectRoot "runtime\short_recovery"
[IO.Directory]::CreateDirectory($logFolder) | Out-Null
$statePath=Join-Path $logFolder "worker.json"
if(Test-Path -LiteralPath $statePath) {
  $state=Get-Content -Raw -Encoding UTF8 -LiteralPath $statePath | ConvertFrom-Json
  $existing=Get-Process -Id $state.processId -ErrorAction SilentlyContinue
  if($existing -and $existing.ProcessName -eq "python" -and $existing.StartTime.ToUniversalTime().ToString("o") -eq $state.startedUtc) {
    Write-Output ("Worker already running: "+$existing.Id);exit 0
  }
}
if($Actor -notmatch '^[A-Za-z0-9_.-]{1,100}$'){throw "Actor must be an existing Oracle user identifier"}
$stopPath=Join-Path $logFolder "worker.stop"
if(Test-Path -LiteralPath $stopPath){Remove-Item -LiteralPath $stopPath}
$arguments=@("-B",('"'+$workerPath+'"'),"--actor",$Actor,"--loop","--interval",$Interval)
$process=Start-Process -FilePath $pythonPath -ArgumentList $arguments -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logFolder "worker.out.log") -RedirectStandardError (Join-Path $logFolder "worker.err.log")
[IO.File]::WriteAllText((Join-Path $logFolder "worker.pid"),[string]$process.Id,[Text.UTF8Encoding]::new($false))
$state=@{processId=$process.Id;startedUtc=$process.StartTime.ToUniversalTime().ToString("o")}
[IO.File]::WriteAllText($statePath,($state | ConvertTo-Json),[Text.UTF8Encoding]::new($false))

Write-Output ("Started short recovery worker: "+$process.Id)
