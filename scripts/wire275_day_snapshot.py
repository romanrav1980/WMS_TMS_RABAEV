from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reconciliation.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .reconciliation_task_times import task_time_coverage","from .reconciliation_task_times import task_time_coverage\nfrom .shipping_register import read_snapshot")
s=s.replace("            task_times=task_time_coverage(cur,ware)","            task_times=task_time_coverage(cur,ware)\n            shipping=read_snapshot(cur,ware,day,0,20)")
s=s.replace('            invalid=sum','            if shipping["has_more"]:blockers.append({"code":"shipping_register_page_incomplete","count":1})\n            occupied=sum(row["occupied"]for row in shipping["cells"])\n            if occupied:blockers.append({"code":"shipping_declared_cells_occupied","count":occupied})\n            pending=sum(not row["physical_departure_confirmed"]for row in shipping["rows"])\n            if pending:blockers.append({"code":"shipping_members_not_departed_in_page","count":pending})\n            invalid=sum',1)
s=s.replace('"warehouse_task_time_coverage":task_times,','"warehouse_task_time_coverage":task_times,"shipping_register":shipping,',1)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/day-review-history.js");s=p.read_text(encoding="utf-8").replace(" const labels={"," const labels={shipping_register_page_incomplete:'Реестр СТ показан частично',shipping_declared_cells_occupied:'Занятые зарегистрированные ячейки грузовой зоны',shipping_members_not_departed_in_page:'Строки СТ без подтверждённого выезда на показанной странице',",1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
