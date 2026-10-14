from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py");s=p.read_text(encoding="utf-8")
assert s.count('"erp_unacknowledged":erp,')==1;out[str(p)]=s.replace('"erp_unacknowledged":erp,','"erp_unacknowledged":erp,"regulatory":regulatory,')
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.html");s=p.read_text(encoding="utf-8")
needle='<section class="panel"><a href="store-investigations.html">'
assert s.count(needle)==1;out[str(p)]=s.replace(needle,'<section class="panel"><h2>Сообщения систем маркировки</h2><div id="drRegulatory"></div><p>Показаны сообщения с подтверждённой привязкой к исходному складу. Количество сообщений не является количеством товара. Отправка сообщения сама по себе не подтверждает принятие государственной системой.</p></section>'+needle)
p=Path("wiki-raw/wms_admin_ui_reference/day-reconciliation.js");s=p.read_text(encoding="utf-8")
s=s.replace('["drFacts","drBacklog","drStock","drErp"]','["drFacts","drBacklog","drStock","drErp","drRegulatory"]')
needle='el("drMessage").textContent="Период "'
assert s.count(needle)==1
s=s.replace(needle,'el("drRegulatory").replaceChildren(...d.regulatory.groups.map(r=>paragraph(r.system_code+" · "+r.event_type+" · "+r.delivery_status+" · сообщений "+r.message_count+" · госответ не сверён"+(r.source_operation_unverified_count?" · исходных проводок не подтверждено "+r.source_operation_unverified_count:""))),paragraph("Полнота привязки всех государственных сообщений к складу ещё не подтверждена."));'+needle)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
