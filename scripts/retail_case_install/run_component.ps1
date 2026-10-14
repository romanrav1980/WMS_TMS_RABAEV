param([ValidateSet('Api','Admin','Terminal')][string]$Component)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
Set-Location -LiteralPath $root
$script=@{Api='serv.bat';Admin='front.bat';Terminal='terminal.bat'}[$Component]
& (Join-Path $root $script)
exit $LASTEXITCODE
