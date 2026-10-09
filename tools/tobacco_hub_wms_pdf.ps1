param([string]$Only = '')
$ErrorActionPreference = 'Stop'
$tobaccoRoot = Split-Path -Parent $PSScriptRoot
$tobaccoSrc = Join-Path $tobaccoRoot 'wiki/requirements/tobacco_regional_hubs/docx'
$tobaccoQa = Join-Path $tobaccoRoot 'tmp/tobacco-hub-wms-qa'
[void][System.IO.Directory]::CreateDirectory($tobaccoQa)
$tobaccoWord = $null
$tobaccoReports = @()
try {
    $tobaccoWord = New-Object -ComObject Word.Application
    $tobaccoWord.Visible = $false
    $tobaccoWord.DisplayAlerts = 0
    $tobaccoWord.AutomationSecurity = 3
    $tobaccoFiles = Get-ChildItem -LiteralPath $tobaccoSrc -Filter '*.docx' -File
    if($Only){$tobaccoFiles=$tobaccoFiles | Where-Object {$_.BaseName -eq $Only}}
    foreach($tobaccoFile in $tobaccoFiles){
        $tobaccoDoc=$null
        try {
            Write-Output ('Opening '+$tobaccoFile.Name)
            $tobaccoDoc=$tobaccoWord.Documents.Open($tobaccoFile.FullName,$false,$true,$false)
            $tobaccoPdf=Join-Path $tobaccoQa ($tobaccoFile.BaseName+'.pdf')
            $tobaccoDoc.SaveAs2([string]$tobaccoPdf,17)
            $tobaccoReports += [pscustomobject]@{name=$tobaccoFile.Name;pdf=$tobaccoPdf;renderer='Microsoft Word 16 SaveAs2 PDF'}
            Write-Output ('Saved '+$tobaccoFile.Name)
        } finally {
            if($null -ne $tobaccoDoc){$tobaccoDoc.Close(0);[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($tobaccoDoc)}
        }
    }
} finally {
    if($null -ne $tobaccoWord){$tobaccoWord.Quit();[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($tobaccoWord)}
}
$tobaccoReports | ConvertTo-Json -Depth 4 | Out-File -LiteralPath (Join-Path $tobaccoQa 'word_pdf_render.json') -Encoding utf8
