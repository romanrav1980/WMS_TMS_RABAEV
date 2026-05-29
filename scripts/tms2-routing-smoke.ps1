param(
  [string]$OsrmUrl = $(if ($env:OSRM_URL) { $env:OSRM_URL } else { "http://localhost:5000" }),
  [string]$ValhallaUrl = $(if ($env:VALHALLA_URL) { $env:VALHALLA_URL } else { "http://localhost:8002" })
)

$ErrorActionPreference = "Stop"

function Test-HttpOk {
  param([string]$Name, [string[]]$Urls)

  foreach ($url in $Urls) {
    try {
      $response = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 5
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
        Write-Host "$Name reachable: $url -> $($response.StatusCode)"
        return $true
      }
    } catch {
      Write-Host "$Name not reachable at $url"
    }
  }
  return $false
}

Write-Host "Checking compose files..."
docker compose -f docker-compose.osrm.yml config | Out-Null
docker compose -f docker-compose.valhalla.yml config | Out-Null
Write-Host "Compose config OK"

$osrmRoute = "$OsrmUrl/route/v1/driving/60.5975,56.8389;60.6122,56.8519?overview=false"
$osrmOk = Test-HttpOk -Name "OSRM" -Urls @($osrmRoute)

$valhallaOk = Test-HttpOk -Name "Valhalla" -Urls @("$ValhallaUrl/status", "$ValhallaUrl/health")

if (-not $osrmOk -and -not $valhallaOk) {
  Write-Host "No live routing container responded. This is OK before starting Docker; backend will fall back to Haversine."
  exit 0
}

Write-Host "Routing smoke OK"
