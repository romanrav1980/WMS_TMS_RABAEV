param(
  [string]$SeedDate = "2026-05-25",
  [switch]$IncludeMutatingVrpApply,
  [switch]$IncludeSprint60To95,
  [switch]$IncludeUiSmoke,
  [switch]$IncludeLoadSmoke
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

if ($IncludeSprint60To95) {
  python -m pytest `
    tests\transport\test_sprint60_functional.py `
    tests\transport\test_sprint61_functional.py `
    tests\transport\test_sprint62_functional.py `
    tests\transport\test_sprint63_functional.py `
    tests\transport\test_sprint64_functional.py `
    tests\transport\test_sprint65_functional.py `
    tests\transport\test_sprint66_functional.py `
    tests\transport\test_sprint67_functional.py `
    tests\transport\test_sprint68_functional.py `
    tests\transport\test_sprint69_functional.py `
    tests\transport\test_sprint70_functional.py `
    tests\transport\test_sprint71_functional.py `
    tests\transport\test_sprint72_functional.py `
    tests\transport\test_sprint73_functional.py `
    tests\transport\test_sprint74_functional.py `
    tests\transport\test_sprint75_functional.py `
    tests\transport\test_sprint76_functional.py `
    tests\transport\test_sprint77_functional.py `
    tests\transport\test_sprint78_functional.py `
    tests\transport\test_sprint79_functional.py `
    tests\transport\test_sprint80_functional.py `
    tests\transport\test_sprint81_functional.py `
    tests\transport\test_sprint82_functional.py `
    tests\transport\test_sprint83_functional.py `
    tests\transport\test_sprint84_functional.py `
    tests\transport\test_sprint85_functional.py `
    tests\transport\test_sprint86_functional.py `
    tests\transport\test_sprint87_functional.py `
    tests\transport\test_sprint88_functional.py `
    tests\transport\test_sprint89_functional.py `
    tests\transport\test_sprint90_functional.py `
    tests\transport\test_sprint91_functional.py `
    tests\transport\test_sprint92_functional.py `
    tests\transport\test_sprint93_functional.py `
    tests\transport\test_sprint94_functional.py `
    tests\transport\test_sprint95_functional.py `
    -q -ra --tb=short
}

if ($IncludeLoadSmoke) {
  foreach ($i in 60..95) {
    python "tests\transport\transport_sprint${i}_load_test.py"
  }
}

if ($IncludeUiSmoke) {
  node tests\ui\transport_sprint60_95_ui_smoke.cjs
  node tests\ui\transport_table_2000_nfr_smoke.cjs
}
