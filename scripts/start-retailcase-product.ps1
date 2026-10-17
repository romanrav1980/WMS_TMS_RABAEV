param([switch]$SkipBuild)
$ErrorActionPreference='Stop'
$workspaceRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$launchRoot=Join-Path $workspaceRoot 'runtime\product-launch'
New-Item -ItemType Directory -Path $launchRoot -Force | Out-Null
$lock=[IO.File]::Open((Join-Path $launchRoot 'launch.lock'),'OpenOrCreate','ReadWrite','None')
try {
    $runRoot=Join-Path $launchRoot ((Get-Date -Format 'yyyyMMdd-HHmmss')+'-'+[guid]::NewGuid().ToString('N').Substring(0,6))
    New-Item -ItemType Directory -Path $runRoot | Out-Null
    $apps=@(@{Name='admin';Path='admin\wms_admin_frontend'},@{Name='terminal';Path='terminal\wms_terminal_web'})
    foreach($app in $apps) {
        $appRoot=Join-Path $workspaceRoot $app.Path
        if(-not $SkipBuild) {
            Write-Output ('Building '+$app.Name+'...')
            $build=Start-Process -FilePath $env:ComSpec -ArgumentList '/d /s /c "npm.cmd run build"' -WorkingDirectory $appRoot -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput (Join-Path $runRoot ($app.Name+'.build.log')) -RedirectStandardError (Join-Path $runRoot ($app.Name+'.build.stderr.log'))
            if($build.ExitCode -ne 0){throw ($app.Name+' build failed; current services were not restarted. Logs: '+$runRoot)}
        }
        if(-not(Test-Path -LiteralPath (Join-Path $appRoot 'dist\index.html'))){throw ($app.Name+' production build missing')}
    }
    $env:TMS_API_RELOAD='0'
    $env:TMS_FRONT_MODE='preview'
    $env:TMS_TERMINAL_MODE='preview'
    $services=@(@{Name='api';Bat='serv.bat';Url='http://127.0.0.1:8088/docs'},@{Name='admin';Bat='front.bat';Url='http://127.0.0.1:3000/'},@{Name='terminal';Bat='terminal.bat';Url='http://127.0.0.1:3010/store/'})
    $started=@()
    foreach($service in $services) {
        $batPath=Join-Path $workspaceRoot $service.Bat
        $child=Start-Process -FilePath $env:ComSpec -ArgumentList ('/d /s /c ""{0}""' -f $batPath) -WorkingDirectory $workspaceRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runRoot ($service.Name+'.log')) -RedirectStandardError (Join-Path $runRoot ($service.Name+'.stderr.log'))
        $started+=@{name=$service.Name;pid=$child.Id;url=$service.Url}
    }
    foreach($service in $services) {
        $ready=$false
        for($attempt=0;$attempt -lt 60;$attempt++) {
            try {
                $response=Invoke-WebRequest -UseBasicParsing -Uri $service.Url -TimeoutSec 3
                $ready=($response.StatusCode -eq 200)
                if($service.Name -ne 'api'){$ready=$ready -and ($response.Content -match '/assets/') -and ($response.Content -notmatch '/@vite/client')}
            } catch {$ready=$false}
            if($ready){break}
            Start-Sleep -Milliseconds 500
        }
        if(-not $ready){throw ($service.Name+' is not ready; logs: '+$runRoot)}
    }
    $manifest=@{state='RUNNING_LOCAL_BUILT_PRODUCT';created_at_utc=[DateTime]::UtcNow.ToString('o');workspace=$workspaceRoot;services=$started;builds=@();logs=$runRoot;scope='Local compiled software; not production warehouse cutover or hardware acceptance'}
    foreach($app in $apps) {
        $index=Join-Path (Join-Path $workspaceRoot $app.Path) 'dist\index.html'
        $manifest.builds+=@{name=$app.Name;index_sha256=(Get-FileHash -LiteralPath $index -Algorithm SHA256).Hash}
    }
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $runRoot 'launch.json')
    Write-Output 'READY: admin http://127.0.0.1:3000/ ; store http://127.0.0.1:3010/store/ ; API http://127.0.0.1:8088/docs'
    Write-Output ('Logs: '+$runRoot)
} finally {$lock.Dispose()}
