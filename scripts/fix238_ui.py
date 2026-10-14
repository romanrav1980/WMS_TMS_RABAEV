from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
a=s.index(";if(r.arrival_timing");b=s.index(";return p;",a)
s=s[:a]+';if(r.arrival_timing&&r.gate_timing)p.textContent+=" · "+timingText(r.arrival_timing)+" · "+timingText(r.gate_timing)'+s[b:]
i=s.index(" async function load()")
helper=""" function timingText(value){
  const labels={UNLOADED_ON_TIME:"Выгружено вовремя",UNLOADED_LATE:"Выгружено с задержкой",AT_GATE_ON_TIME:"Поставлено у ворот вовремя",AT_GATE_LATE:"Поставлено у ворот с задержкой",OVERDUE:"Срок прошёл, факт не подтверждён",EXPECTED:"Ожидается в срок"};
  return (labels[value.state]||"Срок не определён")+(value.delay_seconds!=="0"?" · задержка "+value.delay_seconds+" с":"");
 }
"""
s=s[:i]+helper+s[i:]
s=s.replace('(r.receipt_operation_id?"Принято, требуется размещение":','(r.onward_st_identifier?"Подготовлено следующее плечо":r.placed_task_id?"Поставлено у исходящих ворот":r.receipt_operation_id?"Принято, требуется размещение":',1)
print(json.dumps({str(p):s},ensure_ascii=True))
