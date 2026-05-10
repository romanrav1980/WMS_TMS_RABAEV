[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch]$Apply,
    [switch]$RemoveLegacyXeServer,
    [switch]$RemoveOracleJavaPaths
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-IsAdministrator {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-PathParts([string]$value) {
    if ([string]::IsNullOrWhiteSpace($value)) {
        return @()
    }

    return @($value -split ";" | Where-Object { $_ -and $_.Trim() -ne "" })
}

function Remove-PathEntry([string]$scope, [string]$entry, [switch]$applyChange) {
    $currentValue = [Environment]::GetEnvironmentVariable("Path", $scope)
    $parts = @(Get-PathParts $currentValue)
    $normalizedEntry = $entry.TrimEnd("\")
    $filtered = @($parts | Where-Object { $_.TrimEnd("\") -ne $normalizedEntry })

    if (@($filtered).Length -eq @($parts).Length) {
        return $false
    }

    Write-Host (("PATH {0}: remove {1}") -f $scope, $entry) -ForegroundColor Yellow
    if ($applyChange) {
        [Environment]::SetEnvironmentVariable("Path", ($filtered -join ";"), $scope)
    }

    return $true
}

function Backup-Text([string]$path, [string]$content) {
    $parent = Split-Path -Parent $path
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Set-Content -LiteralPath $path -Value $content -Encoding UTF8
}

$backupRoot = Join-Path $PSScriptRoot "..\tmp\oracle-cleanup-admin"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$stateDir = Join-Path $backupRoot $timestamp

$staleClientHome = "C:\oraclexe\app\oracle\product\11.1.0\client_1"
$legacyXeHome = "C:\oraclexe\app\oracle\product\10.2.0\server"
$legacyXeBin = Join-Path $legacyXeHome "bin"
$inventoryRoot = "C:\Program Files (x86)\Oracle\Inventory"
$inventoryXml = Join-Path $inventoryRoot "ContentsXML\inventory.xml"
$oracleJavaPaths = @(
    "C:\Program Files\Common Files\Oracle\Java\javapath",
    "C:\Program Files (x86)\Common Files\Oracle\Java\java8path",
    "C:\Program Files (x86)\Common Files\Oracle\Java\javapath"
)

if ($Apply -and -not (Test-IsAdministrator)) {
    throw "Run this script as Administrator when using -Apply."
}

New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$services = @(Get-Service | Where-Object { $_.Name -match "Oracle|Ora" -or $_.DisplayName -match "Oracle" })
$uninstallEntries = @(
    Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue
    Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue
    Get-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue
) | Where-Object {
    $_.PSObject.Properties["DisplayName"] -and $_.DisplayName -match "Oracle"
}

Backup-Text (Join-Path $stateDir "machine-path.txt") $machinePath
Backup-Text (Join-Path $stateDir "user-path.txt") $userPath
Backup-Text (Join-Path $stateDir "services.txt") (($services | Select-Object Status, Name, DisplayName | Out-String).Trim())
Backup-Text (Join-Path $stateDir "uninstall-entries.txt") (($uninstallEntries | Select-Object DisplayName, DisplayVersion, Publisher, InstallLocation, UninstallString | Out-String).Trim())

if (Test-Path -LiteralPath $inventoryXml) {
    Copy-Item -LiteralPath $inventoryXml -Destination (Join-Path $stateDir "inventory.xml.bak") -Force
}

Write-Host (("Backup saved to {0}") -f $stateDir) -ForegroundColor Cyan

$removedAnything = $false
$removedAnything = (Remove-PathEntry -scope "Machine" -entry $staleClientHome -applyChange:$Apply) -or $removedAnything
$removedAnything = (Remove-PathEntry -scope "User" -entry $staleClientHome -applyChange:$Apply) -or $removedAnything

if ($RemoveOracleJavaPaths) {
    foreach ($oracleJavaPath in $oracleJavaPaths) {
        $removedAnything = (Remove-PathEntry -scope "Machine" -entry $oracleJavaPath -applyChange:$Apply) -or $removedAnything
        $removedAnything = (Remove-PathEntry -scope "User" -entry $oracleJavaPath -applyChange:$Apply) -or $removedAnything
    }
}

if (Test-Path -LiteralPath $inventoryXml) {
    [xml]$inventory = Get-Content -LiteralPath $inventoryXml
    $homes = @($inventory.INVENTORY.HOME_LIST.HOME)
    $homeCount = @($homes).Length
    $canRemoveInventory = $homeCount -eq 1 -and
        $homes[0].NAME -eq "OraClient11g_home1" -and
        $homes[0].LOC -eq $staleClientHome -and
        -not (Test-Path -LiteralPath $staleClientHome)

    if ($canRemoveInventory) {
        Write-Host (("Stale 32-bit client inventory detected: {0}") -f $inventoryRoot) -ForegroundColor Yellow
        if ($Apply -and $PSCmdlet.ShouldProcess($inventoryRoot, "Remove stale Oracle client inventory")) {
            Remove-Item -LiteralPath $inventoryRoot -Recurse -Force
            $removedAnything = $true
        }
    }
    else {
        Write-Host "Inventory removal skipped: inventory is not a single stale 32-bit client home." -ForegroundColor Yellow
    }
}

if ($RemoveLegacyXeServer) {
    if (@($services).Length -gt 0) {
        throw "Legacy XE cleanup requested, but Oracle services still exist. Stop and remove them first."
    }

    if (Test-Path -LiteralPath $legacyXeHome) {
        Write-Host (("Legacy Oracle XE home detected: {0}") -f $legacyXeHome) -ForegroundColor Yellow
        $removedAnything = (Remove-PathEntry -scope "Machine" -entry $legacyXeBin -applyChange:$Apply) -or $removedAnything
        $removedAnything = (Remove-PathEntry -scope "User" -entry $legacyXeBin -applyChange:$Apply) -or $removedAnything

        if ($Apply -and $PSCmdlet.ShouldProcess($legacyXeHome, "Remove legacy Oracle XE home")) {
            Remove-Item -LiteralPath "HKLM:\SOFTWARE\WOW6432Node\Oracle\KEY_XE" -Recurse -Force -ErrorAction SilentlyContinue

            $legacyXeUninstall = Get-ChildItem "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall" -ErrorAction SilentlyContinue |
                Where-Object {
                    $item = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
                    $item.PSObject.Properties["DisplayName"] -and $item.DisplayName -eq "Oracle Database 10g Express Edition"
                }

            foreach ($key in @($legacyXeUninstall)) {
                Remove-Item -LiteralPath $key.PSPath -Recurse -Force -ErrorAction SilentlyContinue
            }

            Remove-Item -LiteralPath "C:\oraclexe" -Recurse -Force
            $removedAnything = $true
        }
    }
}

if (-not $Apply) {
    Write-Host "Dry run completed. Re-run with -Apply to perform the cleanup." -ForegroundColor Green
    exit 0
}

if ($removedAnything) {
    Write-Host "Oracle remnants cleanup completed." -ForegroundColor Green
}
else {
    Write-Host "Nothing was removed." -ForegroundColor Green
}
