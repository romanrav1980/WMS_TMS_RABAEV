param(
  [Parameter(Mandatory = $true)]
  [string]$PbfUrl,
  [string]$PbfName = "russia-latest.osm.pbf",
  [switch]$SkipDownload,
  [switch]$SkipOsrmBuild
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path "."
$osrmDir = Join-Path $root "osrm-data"
$valhallaDir = Join-Path $root "valhalla-data"
$pbfPath = Join-Path $osrmDir $PbfName

New-Item -ItemType Directory -Force -Path $osrmDir | Out-Null
New-Item -ItemType Directory -Force -Path $valhallaDir | Out-Null

if (-not $SkipDownload) {
  Write-Host "Downloading $PbfUrl to $pbfPath"
  curl.exe -L --fail --output $pbfPath $PbfUrl
  if ($LASTEXITCODE -ne 0) {
    throw "curl.exe failed with exit code $LASTEXITCODE"
  }
} elseif (-not (Test-Path $pbfPath)) {
  throw "PBF file not found: $pbfPath"
}

Copy-Item -Force -Path $pbfPath -Destination (Join-Path $valhallaDir $PbfName)

if (-not $SkipOsrmBuild) {
  Write-Host "Building OSRM data. This can take a while for Russia-scale extracts."
  docker run --rm -v "${osrmDir}:/data" osrm/osrm-backend:latest `
    osrm-extract -p /opt/car.lua "/data/$PbfName"
  if ($LASTEXITCODE -ne 0) {
    throw "osrm-extract failed with exit code $LASTEXITCODE"
  }
  $osrmBase = $PbfName -replace '\.osm\.pbf$', '.osrm'
  docker run --rm -v "${osrmDir}:/data" osrm/osrm-backend:latest `
    osrm-partition "/data/$osrmBase"
  if ($LASTEXITCODE -ne 0) {
    throw "osrm-partition failed with exit code $LASTEXITCODE"
  }
  docker run --rm -v "${osrmDir}:/data" osrm/osrm-backend:latest `
    osrm-customize "/data/$osrmBase"
  if ($LASTEXITCODE -ne 0) {
    throw "osrm-customize failed with exit code $LASTEXITCODE"
  }
}

Write-Host "Routing data preparation finished."
Write-Host "Next:"
Write-Host "  docker compose -f docker-compose.osrm.yml up -d"
Write-Host "  `$env:VALHALLA_FORCE_REBUILD='True'; `$env:VALHALLA_USE_TILES_IGNORE_PBF='False'; docker compose -f docker-compose.valhalla.yml up -d"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-routing-smoke.ps1"
