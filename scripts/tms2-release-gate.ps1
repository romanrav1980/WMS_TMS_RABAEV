param(
  [string]$SeedDate = "2026-05-25",
  [switch]$IncludeMutatingVrpApply
)

$ErrorActionPreference = "Stop"

$env:TMS_SPRINT1_STDATE = $SeedDate
$env:TMS_SPRINT2_STDATE = $SeedDate
$env:TMS_SPRINT3_STDATE = $SeedDate
$env:TMS_SPRINT8_DATE  = $SeedDate
$env:TMS_SPRINT9_DATE  = $SeedDate  # Sprint 9 cluster/template solver uses same seed date

if ($IncludeMutatingVrpApply) {
  $env:TMS_RUN_MUTATING_VRP_APPLY = "1"
  Write-Host "Mutating Sprint 8 apply gate ENABLED for seed date $SeedDate"
} else {
  Remove-Item Env:\TMS_RUN_MUTATING_VRP_APPLY -ErrorAction SilentlyContinue
  Write-Host "Mutating Sprint 8 apply gate disabled. Use -IncludeMutatingVrpApply only on an isolated Oracle fixture."
}

powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-routing-smoke.ps1

python -m pytest `
  tests\transport\test_sprint1_functional.py `
  tests\transport\test_sprint2_functional.py `
  tests\transport\test_sprint3_functional.py `
  tests\transport\test_sprint4_functional.py `
  tests\transport\test_sprint5_functional.py `
  tests\transport\test_sprint6_functional.py `
  tests\transport\test_sprint7_functional.py `
  tests\transport\test_sprint8_functional.py `
  tests\transport\test_sprint9_functional.py `
  tests\transport\test_sprint10_functional.py `
  tests\transport\test_sprint11_functional.py `
  tests\transport\test_sprint12_functional.py `
  tests\transport\test_sprint13_functional.py `
  tests\transport\test_sprint14_functional.py `
  tests\transport\test_sprint15_functional.py `
  tests\transport\test_sprint16_functional.py `
  tests\transport\test_sprint17_functional.py `
  tests\transport\test_sprint18_functional.py `
  tests\transport\test_sprint19_functional.py `
  tests\transport\test_sprint20_functional.py `
  tests\transport\test_routing_infrastructure.py `
  tests\transport\test_frontend_virtualization_nfr.py `
  tests\transport\test_sprint96_functional.py `
  tests\transport\test_sprint97_98_functional.py `
  tests\transport\test_sprint99_100_functional.py `
  tests\transport\test_sprint101_102_functional.py `
  tests\transport\test_sprint103_107_functional.py `
  tests\transport\test_sprint108_114_functional.py `
  tests\transport\test_sprint115_119_functional.py `
  -q -ra --tb=short
