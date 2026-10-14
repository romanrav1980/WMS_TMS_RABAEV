from pathlib import Path
import json
files={};p=Path('api/wms_api_server/app/services/warehouse_task_service.py');t=p.read_text(encoding='utf-8')
t=t.replace('                       QTY_MODE, FACT_QTY, PARENT_TASK_ID,',"""                       QTY_MODE, FACT_QTY, PARENT_TASK_ID,
                       to_char(QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QTY_EXACT,
                       to_char(FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QTY_EXACT,""",1)
t=t.replace("""            select *
              from RRL_WAREHOUSE_TASK
             where TASK_ID = :task_id""","""            select t.*,
                   to_char(t.QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') QTY_EXACT,
                   to_char(t.FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QTY_EXACT
              from RRL_WAREHOUSE_TASK t
             where t.TASK_ID = :task_id""",1)
files[str(p)]=t
tick=chr(96)
for name in ['warehouse-tasks.js','reachtruck-tsd.js']:
 p=Path('wiki-raw/wms_admin_ui_reference')/name;t=p.read_text(encoding='utf-8')
 old='  const value = Number(qty || 0);\n  return '+tick+'\u0024{Number.isInteger(value) ? value : value.toFixed(3)} \u0024{unitCode || ""}'+tick+'.trim();'
 new='  return '+tick+'\u0024{String(qty ?? "0")} \u0024{unitCode || ""}'+tick+'.trim();'
 assert old in t;t=t.replace(old,new,1)
 t=t.replace('formatQty(task.qty, task.unit_code)','formatQty(task.qty_exact ?? task.qty, task.unit_code)').replace('formatQty(task.fact_qty, task.unit_code)','formatQty(task.fact_qty_exact ?? task.fact_qty, task.unit_code)').replace('rtTsdQty(task.qty, task.unit_code)','rtTsdQty(task.qty_exact ?? task.qty, task.unit_code)').replace('task?.qty ?? ""','task?.qty_exact ?? task?.qty ?? ""')
 if name=='warehouse-tasks.js':t=t.replace('warehouseTaskEl("warehouseTaskFactQty").value = task?.qty_exact ?? task?.qty ?? "";','warehouseTaskEl("warehouseTaskFactQty").value = task?.qty_exact ?? task?.qty ?? "";\n  warehouseTaskEl("warehouseTaskFactQty").disabled = !task || task.qty_mode === "PALLET" || terminal;')
 files[str(p)]=t
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.html');files[str(p)]=p.read_text(encoding='utf-8').replace('20261013-819','20261013-821').replace('min="0" step="0.001"','min="0" step="any"')
p=Path('wiki-raw/wms_admin_ui_reference/reachtruck-tsd.html');files[str(p)]=p.read_text(encoding='utf-8').replace('src="reachtruck-tsd.js"','src="reachtruck-tsd.js?v=20261013-821"').replace('step="0.001"','step="any"')
print(json.dumps(files,ensure_ascii=True))
