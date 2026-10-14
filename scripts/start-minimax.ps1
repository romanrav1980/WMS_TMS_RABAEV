[CmdletBinding()]
param([Parameter(Mandatory=$true)][int[]]$Warehouse,[string]$Actor='admin',[int]$Interval=30)
$ErrorActionPreference='Stop'
if($Warehouse.Count -lt 1 -or $Warehouse.Count -gt 10 -or ($Warehouse | Where-Object {$_ -lt 1}) -or $Interval -lt 15 -or $Actor -notmatch '^[a-zA-Z0-9_.-]+$'){throw 'Invalid worker arguments'}
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$state=Join-Path $repo 'runtime/minimax_worker'
[IO.Directory]::CreateDirectory($state) | Out-Null
$identity=Join-Path $state 'worker.json'
if(Test-Path -LiteralPath $identity){
 $previous=Get-Content -LiteralPath $identity -Encoding UTF8 | ConvertFrom-Json
 $live=Get-Process -Id $previous.pid -ErrorAction SilentlyContinue
 if($live -and $live.StartTime.ToUniversalTime().ToString('o') -eq $previous.started_at){throw "Minimax worker already running: $($previous.pid)"}
}
$marker=Join-Path $state 'worker.stop'
if(Test-Path -LiteralPath $marker){Remove-Item -LiteralPath $marker}
$python=Join-Path $repo 'api/wms_api_server/.venv/Scripts/python.exe'
$argsList=@('-B','scripts/minimax_worker.py','--actor',$Actor,'--interval',"$Interval")
foreach($number in ($Warehouse | Sort-Object -Unique)){$argsList+=@('--warehouse',"$number")}
$proc=Start-Process -FilePath $python -ArgumentList $argsList -WorkingDirectory $repo -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $state 'stdout.log') -RedirectStandardError (Join-Path $state 'stderr.log')
@{pid=$proc.Id;started_at=$proc.StartTime.ToUniversalTime().ToString('o');warehouses=$Warehouse;actor=$Actor} | ConvertTo-Json | Set-Content -LiteralPath $identity -Encoding UTF8
Write-Output "Minimax worker started: $($proc.Id)"
