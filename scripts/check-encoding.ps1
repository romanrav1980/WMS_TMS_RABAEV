[CmdletBinding()]
param(
  [switch]$All
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).ProviderPath
$rootWithSlash = $root.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
$skipDirs = @(
  ".git", ".vs", "bin", "obj", "node_modules", "__pycache__", ".pytest_cache",
  "runtime", "dist", "build"
)
$maintainedPrefixes = @(
  "api/",
  "db/migrations/",
  "scripts/",
  "terminal/",
  "tests/",
  "tools/",
  "tmp/oracle_apply/",
  "wiki/",
  "wiki-raw/"
)
$maintainedRootFiles = @(
  ".editorconfig",
  ".gitignore",
  "AGENTS.md",
  "front.bat",
  "serv.bat",
  "stop-listeners.bat",
  "terminal.bat",
  "worker.bat"
)
$textExtensions = @(
  ".md", ".txt", ".sql", ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css",
  ".json", ".env", ".bat", ".cmd", ".ps1", ".cs", ".config", ".xml", ".yml",
  ".yaml", ".editorconfig"
)

try {
  Add-Type -AssemblyName System.Text.Encoding.CodePages -ErrorAction SilentlyContinue
  $providerType = [type]::GetType("System.Text.CodePagesEncodingProvider, System.Text.Encoding.CodePages")
  if ($providerType) {
    [System.Text.Encoding]::RegisterProvider($providerType::Instance)
  }
} catch {
  # Windows PowerShell already has code pages available.
}

function New-MojibakeSamples {
  $utf8 = [System.Text.Encoding]::UTF8
  $cp1251 = [System.Text.Encoding]::GetEncoding(1251)
  $codes = @()
  $codes += 0x0401
  $codes += 0x0451
  for ($code = 0x0410; $code -le 0x044F; $code++) {
    $codes += $code
  }
  foreach ($code in $codes) {
    $char = [string][char]$code
    $bad = $cp1251.GetString($utf8.GetBytes($char))
    if ($bad -ne $char) {
      $bad
    }
  }
}

function Get-RepoRelativePath([string]$path) {
  $rootUri = New-Object System.Uri($rootWithSlash)
  $fileUri = New-Object System.Uri($path)
  return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($fileUri).ToString()).Replace("/", "\")
}

$badSamples = @(New-MojibakeSamples | Where-Object { $_ } | Sort-Object -Unique)
$extraBad = @(
  ([string][char]0xFFFD),
  ([string][char]0x00D0),
  ([string][char]0x00D1),
  ([string][char]0x00C3),
  ([string][char]0x00E2 + [string][char]0x20AC)
)
$badSamples = @($badSamples + $extraBad | Where-Object { $_ })

$problems = New-Object System.Collections.Generic.List[string]
if ($All) {
  $repoFiles = & git -C $root -c core.quotepath=false -c core.autocrlf=false -c core.safecrlf=false ls-files --cached --others --exclude-standard 2>$null
} else {
  $changed = & git -C $root -c core.quotepath=false -c core.autocrlf=false -c core.safecrlf=false diff --name-only HEAD -- 2>$null
  $untracked = & git -C $root -c core.quotepath=false -c core.autocrlf=false -c core.safecrlf=false ls-files --others --exclude-standard 2>$null
  $repoFiles = @($changed + $untracked | Sort-Object -Unique)
}

foreach ($relative in $repoFiles) {
  $relativeSlash = $relative.Replace("\", "/")
  $isMaintainedPath =
    ($maintainedRootFiles -contains $relativeSlash) -or
    ($maintainedPrefixes | Where-Object { $relativeSlash.StartsWith($_, [StringComparison]::OrdinalIgnoreCase) })
  if (-not $isMaintainedPath) {
    continue
  }
  $parts = $relative -split "[\\/]"
  if ($parts | Where-Object { $skipDirs -contains $_ }) {
    continue
  }
  $fullName = Join-Path $root $relative
  if (-not (Test-Path -LiteralPath $fullName -PathType Leaf)) {
    continue
  }
  $extension = [System.IO.Path]::GetExtension($fullName).ToLowerInvariant()
  if ($textExtensions -notcontains $extension) {
    continue
  }

  $content = Get-Content -LiteralPath $fullName -Raw -Encoding UTF8
  if ($null -eq $content) {
    $content = ""
  }
  foreach ($sample in $badSamples) {
    if ($sample.Length -gt 0 -and $content.Contains($sample)) {
      $problems.Add("$relative contains possible mojibake sample [$sample]")
      break
    }
  }
}

if ($problems.Count -gt 0) {
  Write-Host "Encoding check failed:" -ForegroundColor Red
  $problems | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
  exit 1
}

Write-Host "Encoding check passed: UTF-8 text files have no common mojibake markers." -ForegroundColor Green
