[CmdletBinding()]
param(
    [switch]$Plan,
    [switch]$UseExistingOracle,
    [string]$OracleDsn = '127.0.0.1:1521/orcl',
    [string]$OracleArchive,
    [switch]$NoStart
)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
. (Join-Path $PSScriptRoot 'retail_case_install\common.ps1')
$paths = Get-InstallPaths $root
$download = 'https://download.oracle.com/otn-pub/otn_software/db-express/OracleXE213_Win64.zip'
$oracleHash = '939742c3305c466566a55f607638621b6aa7033a183175f6bcd6cffb48e6bc3f'

if ($OracleDsn -notmatch '^[A-Za-z0-9.\-]+:\d{1,5}/orcl$') { throw 'OracleDsn must be host:port/orcl.' }
if (-not [Environment]::Is64BitOperatingSystem) { throw 'A 64-bit Windows installation is required.' }
foreach ($required in @('scripts\install_oracle_release.py','db\releases\2026-10-14\manifest.json','admin\wms_admin_frontend\package-lock.json','terminal\wms_terminal_web\package-lock.json')) {
    if (-not (Test-Path -LiteralPath (Join-Path $root $required))) { throw "Incomplete archive: $required" }
}
if ($Plan) {
    [ordered]@{
        Product='retailcase'; Root=$root; DatabaseMode=$(if($UseExistingOracle){'Existing Oracle / new RABAEV'}else{'New Oracle XE 21c'})
        OracleDsn=$OracleDsn; OracleDownload=$download; OracleSHA256=$oracleHash
        Python='3.13'; Node='22 LTS'; Ports=@(8088,3000,3010)
        Steps=@('Check existing Oracle and ports','Install prerequisites','Download and verify Oracle when needed','Create service and empty RABAEV','Install schema and minimal data','Install UI dependencies','Save encrypted local configuration','Start API and UI')
        MutationsPerformed=$false
    } | ConvertTo-Json -Depth 5
    exit 0
}
if (-not $UseExistingOracle -and $OracleDsn -ne '127.0.0.1:1521/orcl') { throw 'New Oracle XE mode uses 127.0.0.1:1521/orcl.' }
if (Test-Path -LiteralPath $paths.State) {
    $state = Get-Content -Raw -Encoding UTF8 -LiteralPath $paths.State | ConvertFrom-Json
    if ($state.complete) {
        Write-Host 'retailcase is already installed. No database reinstall will be performed.'
        if (-not $NoStart) { & (Join-Path $PSScriptRoot 'start-retail-case.ps1') }
        exit 0
    }
    if ($state.phase -eq 'frontend') {
        Write-Host 'Continue UI dependency installation; Oracle will not be changed.'
        $npm = (Get-Command npm.cmd -ErrorAction Stop).Source
        foreach ($project in @('admin\wms_admin_frontend','terminal\wms_terminal_web')) {
            Invoke-Checked $npm @('--prefix',(Join-Path $root $project),'ci')
        }
        $state.complete=$true; $state.phase='complete'; Save-InstallState $paths $state
        if (-not $NoStart) { & (Join-Path $PSScriptRoot 'start-retail-case.ps1') }
        exit 0
    }
    if ($state.phase -eq 'prerequisites') {
        # No Oracle DDL has started in this phase. Remove only this known state file.
        Remove-Item -LiteralPath $paths.State
        Write-Host 'Retry prerequisite setup; no Oracle installation had started.'
    } else {
        throw "A previous installation stopped at phase '$($state.phase)'. State: $($paths.State). Existing Oracle/schema will not be deleted. See docs/install-retail-case.md."
    }
}
if (-not $UseExistingOracle) {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Run INSTALL-RETAIL-CASE.cmd as administrator. Oracle needs Windows administrator privileges.'
    }
    $oracleServices = @(Get-Service -Name 'OracleService*' -ErrorAction SilentlyContinue)
    if ($oracleServices.Count -gt 0 -or (Test-LocalPort 1521)) {
        throw 'An Oracle service or listener already exists. Use -UseExistingOracle with an empty target, or install on another computer. Existing Oracle will not be replaced.'
    }
    if ($env:ORACLE_HOME -or $env:TNS_ADMIN) { throw 'ORACLE_HOME/TNS_ADMIN is already set. Use a clean installation session or existing-Oracle mode.' }
}
foreach ($port in @(8088,3000,3010)) {
    if (Test-LocalPort $port) { throw "Port $port is occupied. Stop that application yourself or choose a different computer; no process will be killed." }
}
$drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($root).Substring(0,1))
if ($drive.Free -lt 15GB) { throw 'At least 15 GB free space is required for Oracle, its archive and application dependencies.' }
Protect-LocalDirectory $paths.Private
$state = [ordered]@{version=1;complete=$false;phase='prerequisites';mode=$(if($UseExistingOracle){'existing'}else{'xe21'});dsn=$OracleDsn}
Save-InstallState $paths $state
$sysPlain = $null
$schemaPlain = New-DatabaseSecret
$responseFile = Join-Path $paths.Private 'XEInstall.rsp'
try {
    Write-Host '[1/7] Python 3.13 and Node.js 22'
    $python = Resolve-Python313
    $node = Get-Command node.exe -ErrorAction SilentlyContinue
    $node22 = $false
    if ($node) { $node22 = ((& $node.Source --version) -match '^v22\.') }
    if (-not $python -or -not $node22) {
        $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
        if (-not $winget) { throw 'Install Microsoft App Installer (winget), then run again. Official link: https://apps.microsoft.com/detail/9nblggh4nns1' }
        if (-not $python) { Invoke-Checked $winget.Source @('install','--id','Python.Python.3.13','--exact','--source','winget','--silent','--accept-source-agreements','--accept-package-agreements') }
        if (-not $node22) { Invoke-Checked $winget.Source @('install','--id','OpenJS.NodeJS.LTS','--version','22.15.0','--exact','--source','winget','--silent','--accept-source-agreements','--accept-package-agreements') }
        Refresh-ProcessPath
        $python = Resolve-Python313
        $node = Get-Command node.exe -ErrorAction Stop
    }
    if (-not $python) { throw 'Python 3.13 was not found after installation.' }
    if ((& $node.Source --version) -notmatch '^v22\.') { throw 'Node.js 22 is required. Install it and retry the prerequisites step.' }
    Invoke-Checked $python @('-m','venv',(Join-Path $root 'api\wms_api_server\.venv'))
    $apiPython = $paths.Python
    Invoke-Checked $apiPython @('-m','pip','install','-r',(Join-Path $root 'api\wms_api_server\requirements-release-20261014.txt'))
    Invoke-Checked $apiPython @((Join-Path $root 'scripts\install_oracle_release.py'))

    Write-Host '[2/7] Application administrator password'
    $adminSecure = Read-Host 'Set admin password (12-50 printable English letters, digits or symbols; no spaces)' -AsSecureString
    $confirmSecure = Read-Host 'Repeat the admin password' -AsSecureString
    $adminPlain = ConvertTo-PlainSecret $adminSecure
    $confirmPlain = ConvertTo-PlainSecret $confirmSecure
    if ($adminPlain -cne $confirmPlain -or $adminPlain -notmatch '^[\x21-\x7E]{12,50}$') { throw 'Passwords differ or do not fit the required length.' }
    $confirmPlain = $null
    if ($UseExistingOracle) {
        $sysSecure = Read-Host 'SYS password of the target Oracle (SYSDBA)' -AsSecureString
        $sysPlain = ConvertTo-PlainSecret $sysSecure
        $adminDsn = $OracleDsn
    } else {
        $sysPlain = New-DatabaseSecret
        $adminDsn = '127.0.0.1:1521/XEPDB1'
    }
    $secrets = [ordered]@{
        schema = (ConvertTo-SecureString $schemaPlain -AsPlainText -Force | ConvertFrom-SecureString)
        applicationAdmin = ($adminSecure | ConvertFrom-SecureString)
        oracleSys = (ConvertTo-SecureString $sysPlain -AsPlainText -Force | ConvertFrom-SecureString)
    }
    $secrets | ConvertTo-Json | Set-Content -LiteralPath $paths.Secrets -Encoding UTF8

    if (-not $UseExistingOracle) {
        $state.phase='oracle'; Save-InstallState $paths $state
        Write-Host '[3/7] Oracle XE 21c: official archive, about 2 GB'
        $cache = Join-Path $paths.Runtime 'downloads'
        New-Item -ItemType Directory -Force -Path $cache | Out-Null
        $archive = Join-Path $cache 'OracleXE213_Win64.zip'
        if ($OracleArchive) { $archive = (Resolve-Path -LiteralPath $OracleArchive).Path }
        elseif (-not (Test-Path -LiteralPath $archive)) {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Start-BitsTransfer -Source $download -Destination ($archive+'.partial')
            Move-Item -LiteralPath ($archive+'.partial') -Destination $archive
        }
        if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $oracleHash) { throw 'Oracle archive SHA-256 differs from the official checksum. No executable was started.' }
        $extract = Join-Path $cache 'oracle-xe'
        if (-not (Test-Path -LiteralPath (Join-Path $extract 'setup.exe'))) { Expand-Archive -LiteralPath $archive -DestinationPath $extract -Force }
        $setup = Join-Path $extract 'setup.exe'
        if (-not (Test-Path -LiteralPath $setup)) { throw 'setup.exe is missing in the Oracle archive.' }
        # Use the vendor response template to retain required installer sections.
        $template = Join-Path $extract 'response\XEInstall.rsp'
        if (-not (Test-Path -LiteralPath $template)) { throw 'Oracle response template is missing.' }
        $response = Get-Content -Raw -LiteralPath $template
        $values = @{INSTALLDIR='C:\app\retail_case\product\21.0.0';PASSWORD=$sysPlain;LISTENER_PORT='1521';EMEXPRESS_PORT='5500';CHAR_SET='AL32UTF8';DB_DOMAIN=''}
        foreach ($key in $values.Keys) {
            $pattern = '(?m)^\s*'+$key+'\s*=.*$'
            if ($response -notmatch $pattern) { throw "Oracle response template lacks $key." }
            $replacement = $key+'='+$values[$key]
            $response = [regex]::Replace($response,$pattern,[Text.RegularExpressions.MatchEvaluator]{param($m) $replacement})
        }
        $response | Set-Content -LiteralPath $responseFile -Encoding ASCII
        $oracleLog = Join-Path $paths.Private 'oracle-setup.log'
        $arguments = '/s /v"RSP_FILE=\"'+$responseFile+'\"" /v"/L*v \"'+$oracleLog+'\"" /v"/qn"'
        $process = Start-Process -FilePath $setup -ArgumentList $arguments -WorkingDirectory $extract -WindowStyle Hidden -PassThru
        $deadline = [DateTime]::UtcNow.AddMinutes(45)
        do {
            Start-Sleep -Seconds 5
            $ready = Test-LocalPort 1521
            if (-not $ready -and $process.HasExited -and $process.ExitCode -notin @(0,3010)) { throw "Oracle installer failed ($($process.ExitCode)). See protected oracle-setup.log." }
            if ([DateTime]::UtcNow -gt $deadline) { throw 'Oracle setup did not become ready within 45 minutes. See protected oracle-setup.log.' }
        } until ($ready)
        # Listener readiness is not PDB readiness; the next bounded probe checks SYS login.
    } else { Write-Host '[3/7] Use the specified Oracle; no database software installation' }
    $env:RETAIL_ORACLE_SYS_PASSWORD = $sysPlain
    $env:RETAIL_ORACLE_ADMIN_DSN = $adminDsn
    $env:WMS_ORACLE_PASSWORD = $schemaPlain
    $env:WMS_ORACLE_USER = 'RABAEV'
    $env:WMS_ORACLE_DSN = $OracleDsn
    $env:RETAILCASE_INITIAL_ADMIN_PASSWORD = $adminPlain
    $probe = Join-Path $PSScriptRoot 'retail_case_install\wait_oracle.py'
    Invoke-Checked $apiPython @($probe,'--timeout','600')

    $state.phase='schema'; Save-InstallState $paths $state
    Write-Host '[4/7] Create empty RABAEV, install structure and minimal data'
    $provisionArgs = @((Join-Path $PSScriptRoot 'retail_case_install\provision_oracle.py'))
    if (-not $UseExistingOracle) { $provisionArgs += '--create-xe-service' }
    Invoke-Checked $apiPython $provisionArgs
    Invoke-Checked $apiPython @((Join-Path $root 'scripts\install_oracle_release.py'),'--install-empty-rabaev')

    $state.phase='frontend'; Save-InstallState $paths $state
    Write-Host '[5/7] Administrative UI and terminal dependencies'
    $npm = (Get-Command npm.cmd -ErrorAction Stop).Source
    foreach ($project in @('admin\wms_admin_frontend','terminal\wms_terminal_web')) {
        Invoke-Checked $npm @('--prefix',(Join-Path $root $project),'ci')
    }
    $state.phase='complete'; $state.complete=$true
    Save-InstallState $paths $state
    Write-Host '[6/7] Local encrypted configuration saved'
    Write-Host 'Database: RABAEV / orcl. Application login: admin and your chosen password.'
    Write-Host '[7/7] Start the application'
    if (-not $NoStart) { & (Join-Path $PSScriptRoot 'start-retail-case.ps1') }
    Write-Host 'Installation completed. Use START-RETAIL-CASE.cmd for later starts.'
} finally {
    if (Test-Path -LiteralPath $responseFile) {
        $resolved = [IO.Path]::GetFullPath($responseFile)
        if (-not $resolved.StartsWith([IO.Path]::GetFullPath($paths.Private)+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Response file cleanup escaped the installer directory.' }
        Remove-Item -LiteralPath $resolved -Force
    }
    foreach ($name in @('RETAIL_ORACLE_SYS_PASSWORD','RETAIL_ORACLE_ADMIN_DSN','WMS_ORACLE_PASSWORD','RETAILCASE_INITIAL_ADMIN_PASSWORD')) { [Environment]::SetEnvironmentVariable($name,$null,'Process') }
    $sysPlain=$null; $schemaPlain=$null; $adminPlain=$null
}
