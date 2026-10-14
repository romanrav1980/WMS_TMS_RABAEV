$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$files=@('scripts\install-retail-case.ps1','scripts\start-retail-case.ps1','scripts\stop-retail-case.ps1') + @(Get-ChildItem (Join-Path $root 'scripts\retail_case_install') -Filter '*.ps1' | ForEach-Object { $_.FullName })
foreach ($file in $files) {
    $path=if([IO.Path]::IsPathRooted($file)){$file}else{Join-Path $root $file}
    $parseTokens=$null; $parseErrors=$null
    [Management.Automation.Language.Parser]::ParseFile($path,[ref]$parseTokens,[ref]$parseErrors)|Out-Null
    if ($parseErrors.Count) { throw ($parseErrors.Message -join '; ') }
}
. (Join-Path $root 'scripts\retail_case_install\common.ps1')
$testPath=Join-Path $root 'tmp\retail-installer-check'
Protect-LocalDirectory $testPath
$value=New-DatabaseSecret
if($value -notmatch '^[A-Za-z][A-Za-z0-9]{32}$'){throw 'Invalid generated password'}
$secure=ConvertTo-SecureString $value -AsPlainText -Force
$encrypted=$secure|ConvertFrom-SecureString
$roundtrip=ConvertTo-PlainSecret ($encrypted|ConvertTo-SecureString)
if($roundtrip -cne $value){throw 'DPAPI roundtrip failed'}
$paths=Get-InstallPaths $root
$hadState=Test-Path -LiteralPath $paths.State
$plan=& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'scripts\install-retail-case.ps1') -Plan
if($LASTEXITCODE -ne 0){throw 'Plan execution failed'}
$parsed=($plan -join [Environment]::NewLine)|ConvertFrom-Json
if($parsed.MutationsPerformed -ne $false -or $parsed.OracleDsn -ne '127.0.0.1:1521/orcl'){throw 'Plan contract failed'}
if((Test-Path -LiteralPath $paths.State) -ne $hadState){throw 'Plan wrote installation state'}
Write-Output 'PASS: PowerShell syntax, DPAPI roundtrip, generated secrets, side-effect-free installation plan'
