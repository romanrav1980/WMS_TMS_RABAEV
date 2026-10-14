[CmdletBinding()]
param()
$ErrorActionPreference="Stop"
$projectRoot=(Resolve-Path (Join-Path $PSScriptRoot "..")).ProviderPath
$logFolder=Join-Path $projectRoot "runtime\short_recovery"
$statePath=Join-Path $logFolder "worker.json"
if(!(Test-Path -LiteralPath $statePath)){Write-Output "Worker state absent";exit 0}
$state=Get-Content -Raw -Encoding UTF8 -LiteralPath $statePath|ConvertFrom-Json
$worker=Get-Process -Id $state.processId -ErrorAction SilentlyContinue
if(!$worker -or $worker.ProcessName -ne "python" -or $worker.StartTime.ToUniversalTime().ToString("o") -ne $state.startedUtc){
  Write-Output "Recorded worker no longer running";exit 0
}
[IO.File]::WriteAllText((Join-Path $logFolder "worker.stop"),"stop after current iteration",[Text.UTF8Encoding]::new($false))
Write-Output ("Graceful stop requested: "+$worker.Id)
