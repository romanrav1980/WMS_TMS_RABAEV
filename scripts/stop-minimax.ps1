[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$state=Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..')).Path 'runtime/minimax_worker'
$identity=Join-Path $state 'worker.json'
if(!(Test-Path -LiteralPath $identity)){Write-Output 'No minimax worker identity';return}
$previous=Get-Content -LiteralPath $identity -Encoding UTF8 | ConvertFrom-Json
$live=Get-Process -Id $previous.pid -ErrorAction SilentlyContinue
if(!$live -or $live.StartTime.ToUniversalTime().ToString('o') -ne $previous.started_at){Write-Output 'Recorded minimax worker is not running';return}
[IO.File]::WriteAllText((Join-Path $state 'worker.stop'),'stop',[Text.UTF8Encoding]::new($false))
Write-Output "Graceful stop requested for minimax worker $($previous.pid)"
