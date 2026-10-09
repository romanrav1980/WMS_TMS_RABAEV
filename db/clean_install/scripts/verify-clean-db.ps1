param(
    [ValidateSet('legacy-runtime', 'legacy-master', 'modern-prod', 'tms2-acceptance')]
    [string]$Profile = 'modern-prod',

    [string]$ConnectionEnv = 'TMS_ORACLE_ADMIN'
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$installDir = Resolve-Path (Join-Path $scriptDir '..')
$repoRoot = Resolve-Path (Join-Path $installDir '..\..')

$verifyScripts = @{
    'legacy-runtime' = @(
        'verify\10_legacy_core_assert.sql',
        'verify\20_runtime_settings_assert.sql'
    )
    'legacy-master' = @(
        'verify\10_legacy_core_assert.sql',
        'verify\20_runtime_settings_assert.sql',
        'verify\30_master_data_assert.sql'
    )
    'modern-prod' = @(
        'verify\10_legacy_core_assert.sql',
        'verify\20_runtime_settings_assert.sql',
        'verify\30_master_data_assert.sql',
        'verify\40_modern_wms_mes_assert.sql',
        'verify\50_tms2_prod_assert.sql'
    )
    'tms2-acceptance' = @(
        'verify\10_legacy_core_assert.sql',
        'verify\20_runtime_settings_assert.sql',
        'verify\30_master_data_assert.sql',
        'verify\40_modern_wms_mes_assert.sql',
        'verify\50_tms2_prod_assert.sql',
        'verify\60_tms2_acceptance_assert.sql'
    )
}

$connectionString = [Environment]::GetEnvironmentVariable($ConnectionEnv)
if ([string]::IsNullOrWhiteSpace($connectionString)) {
    throw "Environment variable $ConnectionEnv is not set."
}

$oracleApply = Join-Path $repoRoot 'tools\oracle_apply\OracleApply.csproj'

Write-Host "[clean-install verify] Profile: $Profile"

foreach ($relativeScript in $verifyScripts[$Profile]) {
    $scriptPath = Join-Path $installDir $relativeScript
    Write-Host "[clean-install verify] Running $relativeScript"
    & dotnet run --project $oracleApply -- $ConnectionEnv $scriptPath --encoding=utf8 --stop-on-error
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Write-Host "[clean-install verify] OK"
