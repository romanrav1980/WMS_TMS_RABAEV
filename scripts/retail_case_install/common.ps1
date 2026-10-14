# Shared helpers. All local state stays under ignored runtime/install.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $([IO.Path]::GetFileName($Executable)). See the output above." }
}

function ConvertTo-PlainSecret {
    param([Security.SecureString]$Value)
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($Value)
    try { [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}

function New-DatabaseSecret {
    $bytes = New-Object byte[] 16
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    'R' + ([BitConverter]::ToString($bytes).Replace('-',''))
}

function Protect-LocalDirectory {
    param([string]$Path)
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $systemSid = 'S-1-5-18'
    $userGrant = '*' + $sid + ':(OI)(CI)F'
    $systemGrant = '*' + $systemSid + ':(OI)(CI)F'
    & icacls.exe $Path /inheritance:r /grant:r $userGrant $systemGrant | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Unable to restrict local secret directory.' }
    $acl = Get-Acl -LiteralPath $Path
    foreach ($rule in @($acl.Access)) {
        $identity = $rule.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value
        if ($identity -ne $sid -and $identity -ne $systemSid) {
            & icacls.exe $Path /remove ('*'+$identity) | Out-Null
            if ($LASTEXITCODE -ne 0) { throw 'Unable to remove an extra secret-directory permission.' }
        }
    }
}

function Test-LocalPort {
    param([int]$Port)
    $client = New-Object Net.Sockets.TcpClient
    try {
        $pending = $client.BeginConnect('127.0.0.1',$Port,$null,$null)
        if (-not $pending.AsyncWaitHandle.WaitOne(500)) { return $false }
        $client.EndConnect($pending)
        return $true
    } catch { return $false } finally { $client.Dispose() }
}

function Get-InstallPaths {
    param([string]$Root)
    @{
        Root = $Root
        Runtime = Join-Path $Root 'runtime\install'
        Private = Join-Path $Root 'runtime\install\private'
        State = Join-Path $Root 'runtime\install\private\state.json'
        Secrets = Join-Path $Root 'runtime\install\private\secrets.json'
        Python = Join-Path $Root 'api\wms_api_server\.venv\Scripts\python.exe'
    }
}

function Save-InstallState {
    param($Paths, $State)
    $temporary = $Paths.State + '.tmp'
    $State | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $temporary -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $Paths.State -Force
}

function Resolve-Python313 {
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) {
        $answer = & $py.Source -3.13 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $answer) { return $answer.Trim() }
    }
    foreach ($path in @((Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'), 'C:\Program Files\Python313\python.exe')) {
        if (Test-Path -LiteralPath $path) { return $path }
    }
    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($python) {
        $version = & $python.Source -c "import sys; print('%s.%s'%sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $version -eq '3.13') { return $python.Source }
    }
    return $null
}

function Refresh-ProcessPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
}
