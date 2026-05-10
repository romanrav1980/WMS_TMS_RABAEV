$msbuild = "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\amd64\MSBuild.exe"
$project = "C:\projects\TMS\MINI WMS\WindowsApplication2\WindowsApplication2\WindowsApplication2.csproj"

if (-not (Test-Path $msbuild)) {
    throw "MSBuild not found at: $msbuild"
}

& $msbuild $project /t:Rebuild /p:Configuration=Release /p:Platform=x64 /p:SignManifests=false /p:GenerateManifests=false

if ($LASTEXITCODE -ne 0) {
    throw "Build failed with exit code $LASTEXITCODE"
}
