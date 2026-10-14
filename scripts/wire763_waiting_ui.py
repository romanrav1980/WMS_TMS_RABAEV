from pathlib import Path
import json
files={}
p=Path("wiki-raw/wms_admin_ui_reference/receiving.html");t=p.read_text(encoding="utf-8")
anchor='<label>Единица ограничения высоты ячейки'
assert anchor in t and 'receiptDeferWaitCell' not in t
files[str(p)]=t.replace(anchor,'<label>Ячейка ожидания перенесённых СТ<input id="receiptDeferWaitCell" maxlength="50" placeholder="Ячейка этого склада вне зоны отгрузки"></label>\n'+anchor)
p=Path("wiki-raw/wms_admin_ui_reference/receiving.js");t=p.read_text(encoding="utf-8")
t=t.replace("[['receiptQcSamplePercent'","[['receiptDeferWaitCell','defer_wait_cell'],['receiptQcSamplePercent'")
t=t.replace("{outgoing_qc_sample_percent:el('receiptQcSamplePercent').value","{defer_wait_cell:el('receiptDeferWaitCell').value.trim()||null,outgoing_qc_sample_percent:el('receiptQcSamplePercent').value")
assert t.count("receiptDeferWaitCell")==2
files[str(p)]=t
files["db/migrations/2026-10-12_ni072_waiting_cell/apply.sql"]="@@001_waiting_cell.sql\n@@003_recompile.sql\n@@002_ledger.sql\n"
print(json.dumps(files,ensure_ascii=True))
