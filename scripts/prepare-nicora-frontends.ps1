param(
    [string]$Destination = 'tmp\nicora_ns00_install\frontends_online',
    [switch]$Offline
)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$stageRoot = [IO.Path]::GetFullPath((Join-Path $repoRoot $Destination))
if (-not $stageRoot.StartsWith($repoRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'NS00 staging must remain inside the repository.'
}
if (Test-Path -LiteralPath $stageRoot) { throw 'Choose a fresh destination; existing staging is never deleted.' }
New-Item -ItemType Directory -Path (Join-Path $stageRoot 'config') -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $repoRoot 'config\project.defaults.json') -Destination (Join-Path $stageRoot 'config')
$results = @()
foreach ($relative in @('admin\wms_admin_frontend','terminal\wms_terminal_web')) {
    $source = Join-Path $repoRoot $relative
    $target = Join-Path $stageRoot $relative
    New-Item -ItemType Directory -Path $target -Force | Out-Null
    Get-ChildItem -LiteralPath $source -File | Where-Object {
        $_.Name -match '^(package(-lock)?\.json|tsconfig.*\.json|vite\.config\..*|index\.html|\.npmrc)$'
    } | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $target }
    foreach ($folder in @('src','public')) {
        $sourceFolder = Join-Path $source $folder
        if (Test-Path -LiteralPath $sourceFolder) { Copy-Item -LiteralPath $sourceFolder -Destination $target -Recurse }
    }
    Push-Location $target
    try {
        $argsList = @('ci','--legacy-peer-deps','--no-audit','--no-fund')
        if ($Offline) { $argsList += '--offline' }
        & npm.cmd @argsList
        if ($LASTEXITCODE -ne 0) { throw "Fresh npm ci failed: $relative" }
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw "Fresh build failed: $relative" }
        $results += [ordered]@{project=$relative;path=$target;install='npm ci';build='PASS';offline=[bool]$Offline;
            lockSha256=(Get-FileHash -LiteralPath (Join-Path $target 'package-lock.json') -Algorithm SHA256).Hash}
    } finally { Pop-Location }
}
$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $stageRoot 'build-report.json') -Encoding UTF8
Write-Host 'NS00 fresh frontend installation/build PASS'
