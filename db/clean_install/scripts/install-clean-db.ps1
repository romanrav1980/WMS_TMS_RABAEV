param(
    [ValidateSet('legacy-runtime', 'legacy-master', 'modern-prod', 'tms2-acceptance')]
    [string]$Profile = 'modern-prod',

    [string]$ConnectionEnv = 'TMS_ORACLE_ADMIN',

    [switch]$IUnderstandThisRebuildsRabaev,

    [switch]$NoVerify,

    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$installDir = Resolve-Path (Join-Path $scriptDir '..')
$repoRoot = Resolve-Path (Join-Path $installDir '..\..')

$profiles = @{
    'legacy-runtime' = 'profiles\01_legacy_runtime.sql'
    'legacy-master' = 'profiles\02_legacy_master.sql'
    'modern-prod' = 'profiles\03_modern_prod.sql'
    'tms2-acceptance' = 'profiles\04_tms2_acceptance.sql'
}

if (-not $IUnderstandThisRebuildsRabaev) {
    throw 'Clean install profiles are destructive for the target RABAEV schema. Re-run with -IUnderstandThisRebuildsRabaev only against an empty/disposable Oracle target.'
}

$connectionString = [Environment]::GetEnvironmentVariable($ConnectionEnv)
if ([string]::IsNullOrWhiteSpace($connectionString)) {
    throw "Environment variable $ConnectionEnv is not set."
}

$profilePath = Join-Path $installDir $profiles[$Profile]
$oracleApply = Join-Path $repoRoot 'tools\oracle_apply\OracleApply.csproj'

Write-Host "[clean-install] Profile: $Profile"
Write-Host "[clean-install] Connection env: $ConnectionEnv"
Write-Host "[clean-install] Script: $profilePath"

if ($DryRun) {
    Write-Host '[clean-install] Dry run only; no SQL executed.'
    exit 0
}

& dotnet run --project $oracleApply -- $ConnectionEnv $profilePath --encoding=utf8 --stop-on-error --allow-absent-cleanup "--source-encoding-manifest=$(Join-Path $installDir 'legacy_source_encodings.json')"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

if (-not $NoVerify) {
    & (Join-Path $scriptDir 'verify-clean-db.ps1') -Profile $Profile -ConnectionEnv $ConnectionEnv
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Write-Host "[clean-install] Completed profile $Profile"
