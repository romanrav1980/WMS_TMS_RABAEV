$ErrorActionPreference = 'Stop'
$qpRoot = Split-Path -Parent $PSScriptRoot
$qpDocx = Join-Path $qpRoot 'wiki/requirements/tobacco_regional_hubs/supplier_questionnaire_v2/questionnaire.docx'
$qpQa = Join-Path $qpRoot 'tmp/tobacco-questionnaire-v2-qa'
[void][System.IO.Directory]::CreateDirectory($qpQa)
$qpWord=$null
$qpDoc=$null
try {
    $qpWord=New-Object -ComObject Word.Application
    $qpWord.Visible=$false
    $qpWord.DisplayAlerts=0
    $qpWord.AutomationSecurity=3
    $qpDoc=$qpWord.Documents.Open($qpDocx,$false,$true,$false)
    $qpPdf=Join-Path $qpQa 'questionnaire.pdf'
    $qpDoc.SaveAs2([string]$qpPdf,17)
    Write-Output $qpPdf
} finally {
    if($null -ne $qpDoc){$qpDoc.Close(0);[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($qpDoc)}
    if($null -ne $qpWord){$qpWord.Quit();[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($qpWord)}
}
