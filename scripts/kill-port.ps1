param(
  [int[]]$Port = @(),
  [string[]]$CommandLineLike = @(),
  [int]$WaitSeconds = 3,
  [switch]$FailIfBusy
)

$ErrorActionPreference = "Stop"

function Get-ListeningPid {
  param([int]$TargetPort)
  $lines = netstat -ano | Select-String -Pattern "LISTENING" | Where-Object {
    $_.Line -match "[:.]$TargetPort\s"
  }
  foreach ($line in $lines) {
    $tokens = ($line.Line -split "\s+") | Where-Object { $_ }
    if ($tokens.Count -ge 5) {
      $pidText = $tokens[$tokens.Count - 1]
      $parsed = 0
      if ([int]::TryParse($pidText, [ref]$parsed) -and $parsed -gt 0) {
        $parsed
      }
    }
  }
}

function Stop-ProcessTree {
  param([int]$ProcessId)

  $children = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
      $_.ParentProcessId -eq $ProcessId -or
      ($_.CommandLine -and $_.CommandLine -like "*parent_pid=$ProcessId*")
    }

  foreach ($child in $children) {
    Stop-ProcessTree -ProcessId ([int]$child.ProcessId)
  }

  $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
  if ($process) {
    Write-Host "Stopping process PID $ProcessId ($($process.ProcessName))..."
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 300
    $stillRunning = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($stillRunning) {
      Write-Host "Stop-Process did not finish PID $ProcessId, trying taskkill tree..."
      & taskkill.exe /PID $ProcessId /T /F | Out-Host
    }
  } else {
    Write-Host "Process PID $ProcessId is not visible to Get-Process, trying taskkill tree..."
    & taskkill.exe /PID $ProcessId /T /F | Out-Host
  }
}

function Stop-CommandLineMatch {
  param([string]$Pattern)

  $currentPid = $PID
  $ignoredNames = @("powershell.exe", "pwsh.exe", "cmd.exe")
  $matches = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
      $_.ProcessId -ne $currentPid -and
      $ignoredNames -notcontains $_.Name.ToLowerInvariant() -and
      $_.CommandLine -and
      $_.CommandLine -like $Pattern
    }

  foreach ($match in $matches) {
    Write-Host "Found matching process '$Pattern': PID $($match.ProcessId)"
    Stop-ProcessTree -ProcessId ([int]$match.ProcessId)
  }
}

foreach ($pattern in $CommandLineLike) {
  if ($pattern) {
    Stop-CommandLineMatch -Pattern $pattern
  }
}

foreach ($targetPort in $Port) {
  if ($targetPort -le 0) {
    continue
  }

  Write-Host "Checking port $targetPort..."
  $pids = @(Get-ListeningPid -TargetPort $targetPort | Sort-Object -Unique)
  foreach ($pidToStop in $pids) {
    Write-Host "Found listener on port ${targetPort}: PID $pidToStop"
    Stop-ProcessTree -ProcessId $pidToStop
  }
}

if ($WaitSeconds -gt 0) {
  Start-Sleep -Seconds $WaitSeconds
}

$busy = @()
foreach ($targetPort in $Port) {
  $remaining = @(Get-ListeningPid -TargetPort $targetPort | Sort-Object -Unique)
  foreach ($pidStillBusy in $remaining) {
    $busy += "port $targetPort PID $pidStillBusy"
  }
}

if ($busy.Count -gt 0) {
  $message = "Port cleanup failed: " + ($busy -join "; ")
  if ($FailIfBusy) {
    Write-Error $message
    exit 1
  }
  Write-Warning $message
}

exit 0
