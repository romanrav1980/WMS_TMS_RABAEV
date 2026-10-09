param(
    [string]$SourceDocx = 'Nikora_business_processes_v55.docx',
    [string]$OutputDocx = 'Nikora_business_processes_v56.docx'
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression, System.IO.Compression.FileSystem
$projectDocRoot = $PSScriptRoot
$sourcePath = Join-Path $projectDocRoot $SourceDocx
$outputPath = Join-Path $projectDocRoot $OutputDocx
if ([IO.Path]::GetFullPath($sourcePath) -eq [IO.Path]::GetFullPath($outputPath)) { throw 'Input and output must differ' }
$utf8 = [Text.UTF8Encoding]::new($false)
$w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
$r = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
function Read-ZipText($zip,$name) {
    $entry = $zip.GetEntry($name)
    if (-not $entry) { throw "Missing package part: $name" }
    $reader = [IO.StreamReader]::new($entry.Open(),[Text.Encoding]::UTF8)
    try { return $reader.ReadToEnd() } finally { $reader.Dispose() }
}
function Write-ZipXml($zip,$name,[xml]$xml) {
    $old = $zip.GetEntry($name)
    if ($old) { $old.Delete() }
    $entry = $zip.CreateEntry($name,[IO.Compression.CompressionLevel]::Optimal)
    $settings = [Xml.XmlWriterSettings]::new(); $settings.Encoding = $utf8; $settings.Indent = $false
    $writer = [Xml.XmlWriter]::Create($entry.Open(),$settings)
    try { $xml.Save($writer) } finally { $writer.Dispose() }
}
function Paragraph-Text($p) { return (($p.SelectNodes('.//w:t',$ns) | ForEach-Object { $_.InnerText }) -join '') }
function New-Run([string]$text,[bool]$link=$false) {
    $run=$xml.CreateElement('w','r',$w)
    if ($link) {
        $rp=$xml.CreateElement('w','rPr',$w)
        $color=$xml.CreateElement('w','color',$w); [void]$color.SetAttribute('val',$w,'0563C1'); [void]$rp.AppendChild($color)
        $under=$xml.CreateElement('w','u',$w); [void]$under.SetAttribute('val',$w,'single'); [void]$rp.AppendChild($under)
        [void]$run.AppendChild($rp)
    }
    $t=$xml.CreateElement('w','t',$w); [void]$t.SetAttribute('space','http://www.w3.org/XML/1998/namespace','preserve'); $t.InnerText=$text
    [void]$run.AppendChild($t); return ,$run
}
function New-Paragraph([string]$text,[string]$style='') {
    $p=$xml.CreateElement('w','p',$w)
    if ($style) {
        $pp=$xml.CreateElement('w','pPr',$w); $ps=$xml.CreateElement('w','pStyle',$w); [void]$ps.SetAttribute('val',$w,$style)
        [void]$pp.AppendChild($ps); [void]$p.AppendChild($pp)
    }
    $offset=0
    foreach ($match in [regex]::Matches($text,'\[([^\]]+)\]\((https://[^)]+)\)')) {
        if ($match.Index -gt $offset) { [void]$p.AppendChild((New-Run $text.Substring($offset,$match.Index-$offset))) }
        if ($match.Groups[2].Value -ne $erpUrl) { throw 'Unregistered external hyperlink' }
        $hl=$xml.CreateElement('w','hyperlink',$w); [void]$hl.SetAttribute('id',$r,$erpRelId)
        [void]$hl.AppendChild((New-Run $match.Groups[1].Value $true)); [void]$p.AppendChild($hl)
        $offset=$match.Index+$match.Length
    }
    if ($offset -lt $text.Length) { [void]$p.AppendChild((New-Run $text.Substring($offset))) }
    return ,$p
}
function Replace-Section([string]$prefix,[string]$sourceFile,[string]$newTitle) {
    $nodes=@($body.ChildNodes)
    $start=-1; $end=$nodes.Count
    for ($i=0;$i -lt $nodes.Count;$i++) {
        $style=$nodes[$i].SelectSingleNode('w:pPr/w:pStyle',$ns)
        if ($style -and $style.GetAttribute('val',$w) -eq 'Heading1') {
            if ($start -ge 0) { $end=$i; break }
            if ((Paragraph-Text $nodes[$i]).StartsWith($prefix)) { $start=$i }
        }
    }
    if ($start -lt 0) { throw "Section not found: $prefix" }
    $anchor=$nodes[$end]
    for ($i=$start;$i -lt $end;$i++) { [void]$body.RemoveChild($nodes[$i]) }
    [void]$body.InsertBefore((New-Paragraph $newTitle 'Heading1'),$anchor)
    $source=[IO.File]::ReadAllText((Join-Path $projectDocRoot $sourceFile),[Text.Encoding]::UTF8)
    $blocks=[regex]::Split($source.Trim(),'\r?\n\s*\r?\n')
    foreach ($block in $blocks | Select-Object -Skip 1) {
        $block=$block.Trim()
        if (-not $block -or $block.StartsWith('[Оглавление')) { continue }
        if ($block.StartsWith('## ')) { [void]$body.InsertBefore((New-Paragraph $block.Substring(3) 'Heading2'),$anchor) }
        elseif ($block.StartsWith('- ')) {
            foreach ($line in ($block -split '\r?\n')) {
                if (-not $line.StartsWith('- ')) { throw 'Invalid bullet block' }
                [void]$body.InsertBefore((New-Paragraph $line.Substring(2) 'ListBullet'),$anchor)
            }
        }
        elseif ($block.StartsWith('|')) { throw 'Table generation is outside this surgical updater' }
        else { [void]$body.InsertBefore((New-Paragraph $block),$anchor) }
    }
}
Copy-Item -LiteralPath $sourcePath -Destination $outputPath -Force
$zip=[IO.Compression.ZipFile]::Open($outputPath,[IO.Compression.ZipArchiveMode]::Update)
try {
    [xml]$xml=Read-ZipText $zip 'word/document.xml'
    [xml]$rels=Read-ZipText $zip 'word/_rels/document.xml.rels'
    [xml]$core=Read-ZipText $zip 'docProps/core.xml'
    $ns=[Xml.XmlNamespaceManager]::new($xml.NameTable); $ns.AddNamespace('w',$w)
    $body=$xml.SelectSingleNode('/w:document/w:body',$ns)
    $erpUrl='https://docs.google.com/document/d/1GY9T1PyJhKsw_Rm6TJTmqyhNQMFpEBnbWrSLGVA4xLs/edit?usp=drive_link'
    $erpRelId='rIdNikoraERPv56'
    if ($rels.DocumentElement.SelectSingleNode("*[@Id='$erpRelId']")) { throw 'Relationship ID already used' }
    $rel=$rels.CreateElement('Relationship',$rels.DocumentElement.NamespaceURI)
    [void]$rel.SetAttribute('Id',$erpRelId); [void]$rel.SetAttribute('Type',$r+'/hyperlink'); [void]$rel.SetAttribute('Target',$erpUrl); [void]$rel.SetAttribute('TargetMode','External')
    [void]$rels.DocumentElement.AppendChild($rel)
    foreach ($p in @($body.SelectNodes('w:p',$ns))) {
        $text=Paragraph-Text $p
        if ($text -eq 'Редакция 55 от 7 октября 2026 года') {
            [void]$body.ReplaceChild((New-Paragraph 'Редакция 56 от 7 октября 2026 года'),$p)
        }
        elseif ($text -eq '15. Приёмка и размещение запаса') {
            [void]$body.ReplaceChild((New-Paragraph '15. Приёмка товара по документам SAP и размещение паллет'),$p)
        }
    }
    Replace-Section '5 Комплектация' '04_storage_replenishment_picking.md' '5 Комплектация заказов по обеспеченным волнам'
    Replace-Section '11 Возвраты' '11_returns_and_assets.md' '11 Возвраты товара и оборотной тары'
    Replace-Section '13 Подготовка справочных' '01_master_data.md' '13 Подготовка справочных данных для планирования'
    Replace-Section '15 Приёмка' '03_warehouse_receipt.md' '15 Приёмка товара по документам SAP и размещение паллет'
    $termHeading=@($body.SelectNodes('w:p',$ns)) | Where-Object { (Paragraph-Text $_) -eq 'Термины' } | Select-Object -First 1
    if (-not $termHeading) { throw 'Terms anchor missing' }
    $readme=[IO.File]::ReadAllText((Join-Path $projectDocRoot 'README.md'),[Text.Encoding]::UTF8)
    foreach ($block in [regex]::Split($readme,'\r?\n\s*\r?\n')) {
        if ($block.StartsWith('Входящий запас') -or $block.StartsWith('Связанный документ')) { [void]$body.InsertBefore((New-Paragraph $block.Trim()),$termHeading) }
    }
    $contentsHeading=@($body.SelectNodes('w:p',$ns)) | Where-Object { (Paragraph-Text $_) -eq 'Содержание' } | Select-Object -First 1
    $contentsPr=$contentsHeading.SelectSingleNode('w:pPr',$ns)
    if (-not $contentsPr) { $contentsPr=$xml.CreateElement('w','pPr',$w); [void]$contentsHeading.PrependChild($contentsPr) }
    [void]$contentsPr.AppendChild($xml.CreateElement('w','pageBreakBefore',$w))
    $coreNs=[Xml.XmlNamespaceManager]::new($core.NameTable); $coreNs.AddNamespace('dc','http://purl.org/dc/elements/1.1/'); $coreNs.AddNamespace('dcterms','http://purl.org/dc/terms/')
    $core.SelectSingleNode('//dc:subject',$coreNs).InnerText='Общее ТЗ логистических процессов с приёмкой по SAP маркировкой и размещением'
    $core.SelectSingleNode('//dc:description',$coreNs).InnerText='Редакция 56 от 7 октября 2026 года; процесс 15 расширен; редакция 55 сохранена'
    $modified=$core.SelectSingleNode('//dcterms:modified',$coreNs)
    if ($modified) { $modified.InnerText=[DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ') }
    Write-ZipXml $zip 'word/document.xml' $xml
    Write-ZipXml $zip 'word/_rels/document.xml.rels' $rels
    Write-ZipXml $zip 'docProps/core.xml' $core
} finally { $zip.Dispose() }
Write-Output $outputPath