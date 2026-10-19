$ErrorActionPreference='Stop'
$scriptPath=Join-Path $PSScriptRoot 'queue.ps1'
$owner=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal=New-ScheduledTaskPrincipal -UserId $owner -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 3)
foreach ($item in @(@{Phase='analysis';At='08:30'},@{Phase='execute';At='09:00'},@{Phase='stop';At='18:00'})) {
    $at=[DateTimeOffset]::Parse(('2026-10-19T'+$item.At+':00+03:00')).LocalDateTime
    $trigger=New-ScheduledTaskTrigger -Once -At $at
    $arguments='-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "'+$scriptPath+'" -Phase '+$item.Phase
    $action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arguments -WorkingDirectory 'C:\projects\TMS'
    $name='TMS-TRADECASE-20261019-'+$item.Phase
    if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) { throw ('Task already exists: '+$name) }
    Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'Owner-authorized one-time TRADECASE work, Moscow time; queue existing Codex thread' | Select-Object TaskName,State
}
