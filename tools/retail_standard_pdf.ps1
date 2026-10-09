param([string]$Only = "")
$ErrorActionPreference = 'Stop'
$retailRoot = Split-Path -Parent $PSScriptRoot
$retailSrc = Join-Path $retailRoot 'wiki/requirements/retail_convenience_standard/docx'
$retailQa = Join-Path $retailRoot 'tmp/retail-standard-qa'
[void][System.IO.Directory]::CreateDirectory($retailQa)
$retailWord = $null
$retailReports = @()
try {
    $retailWord = New-Object -ComObject Word.Application
    $retailWord.Visible = $false
    $retailWord.DisplayAlerts = 0
    $retailWord.AutomationSecurity = 3
    $retailFiles = Get-ChildItem -LiteralPath $retailSrc -Filter '*.docx' -File
    if($Only){$retailFiles=$retailFiles | Where-Object {$_.BaseName -eq $Only}}
    foreach($retailFile in $retailFiles){
        $retailDoc=$null
        try {
            Write-Output ('Opening '+$retailFile.Name)
            $retailDoc=$retailWord.Documents.Open($retailFile.FullName,$false,$true,$false)
            Write-Output ('Opened '+$retailFile.Name)
            $retailPdf=Join-Path $retailQa ($retailFile.BaseName+'.pdf')
            $retailDoc.SaveAs2([string]$retailPdf,17)
            $retailReports += [pscustomobject]@{name=$retailFile.Name;pdf=$retailPdf;renderer='Microsoft Word 16 SaveAs2 PDF'}
            Write-Output ('Saved '+$retailFile.Name)
        } finally {
            if($null -ne $retailDoc){$retailDoc.Close(0);[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($retailDoc)}
        }
    }
} finally {
    if($null -ne $retailWord){$retailWord.Quit();[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($retailWord)}
}
$retailReports | ConvertTo-Json -Depth 4 | Out-File -LiteralPath (Join-Path $retailQa 'word_pdf_render.json') -Encoding utf8
