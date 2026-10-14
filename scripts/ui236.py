from pathlib import Path
import json
out={};p=Path("wiki-raw/wms_admin_ui_reference/return-disposal.html");s=p.read_text(encoding="utf-8").replace('<button id="rdDispose">','<fieldset id="rdUnitScans" hidden><legend>Уникальные коды утилизируемого товара</legend></fieldset><button id="rdDispose">',1).replace('<script src="return-disposal.js">','<script src="unit-scan-draft.js"></script><script src="return-disposal.js">',1).replace('Маркированный товар требует отдельного допустимого жизненного цикла.','Для маркированного товара сканируются все обязательные профили согласованных единиц. Физический акт не является государственной квитанцией; сообщения системам маркировки остаются в очереди до внешнего подтверждения.');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/return-disposal.js");s=p.read_text(encoding="utf-8").replace(' let pending=null',' const markDraft=window.wmsUnitScanDraft(document.getElementById("rdUnitScans"));\n function selectMarks(){const row=rows.find(r=>r.request_operation_id===el("rdRequest").value);markDraft.setContext(row?.marked_unit_control||null,key()+":"+row?.receipt_operation_id+":"+row?.stock_version);}\n let pending=null',1)
s=s.replace('function clear(){rows=[];','function clear(){rows=[];markDraft.setContext(null,"");',1)
s=s.replace('say("Возвраты обновлены.");','selectMarks();say("Возвраты обновлены.");',1)
s=s.replace('decision_reference:el("rdDecision").value.trim()};','decision_reference:el("rdDecision").value.trim(),...(row.marked_unit_control?{scans:markDraft.getScans()}:{})};',1)
s=s.replace(' el("rdLoad").addEventListener',' el("rdRequest").addEventListener("change",selectMarks);\n el("rdLoad").addEventListener',1)
s=s.replace('Сообщение SAP в очереди.','Сообщение SAP в очереди. Государственная квитанция не подтверждена.');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
