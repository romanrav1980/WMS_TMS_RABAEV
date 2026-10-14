from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="api/wms_api_server/app/services/warehouse_task_service.py";src=read(p)
needle="""            if queue_group != "SHIPPING":
                raise HTTPException(422, detail="Unknown warehouse task queue group")
            conditions.append("(TASK_TYPE='PICKING_MOVE' or (TASK_TYPE='REPLENISHMENT' and SOURCE_DOC_TYPE='SHIPMENT'))")"""
assert src.count(needle)==1
src=src.replace(needle,"""            if queue_group == "SHIPPING":
                conditions.append("(TASK_TYPE='PICKING_MOVE' or (TASK_TYPE='REPLENISHMENT' and SOURCE_DOC_TYPE='SHIPMENT'))")
            elif queue_group == "DEFER_WAITING":
                conditions.append("(TASK_TYPE='PUTAWAY' and TASK_SOURCE='MANUAL' and SOURCE_DOC_TYPE in('ST_DEFER','ST_DEFER_CASE'))")
            else:
                raise HTTPException(422, detail="Unknown warehouse task queue group")""")
files[p]=src
p="api/wms_api_server/app/routers/warehouse_tasks.py";src=read(p);assert src.count('Literal["SHIPPING"]')==1;files[p]=src.replace('Literal["SHIPPING"]','Literal["SHIPPING","DEFER_WAITING"]')
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.js";src=read(p)
needle='  if(warehouseTaskState.preset==="shipping-zone")params.set("queue_group","SHIPPING");';assert src.count(needle)==1
src=src.replace(needle,needle+'\n  if(warehouseTaskState.preset==="waiting")params.set("queue_group","DEFER_WAITING");')
src=src.replace('    warehouseTaskEl("warehouseTaskDocType").value = "ST_DEFER";','    warehouseTaskEl("warehouseTaskDocType").value = "";')
src=src.replace('task.source_doc_type === "ST_DEFER") return "Перемещение в ожидание рейса";','["ST_DEFER","ST_DEFER_CASE"].includes(task.source_doc_type)) return task.source_doc_type==="ST_DEFER_CASE" ? "CASE в ожидание рейса" : "Перемещение в ожидание рейса";')
src=src.replace('task.source_doc_type === "ST_DEFER" ? "Перенос СТ" : task.source_doc_type','task.source_doc_type === "ST_DEFER_CASE" ? "Перенос СТ · CASE" : task.source_doc_type === "ST_DEFER" ? "Перенос СТ" : task.source_doc_type')
needle='function qtyModeText(task) {\n';assert src.count(needle)==1
src=src.replace(needle,needle+'  if(task.source_doc_type==="ST_DEFER_CASE" && task.unit_code==="CASE")return "CASE · одно место";\n')
needle='  warehouseTaskEl("warehouseTaskDetailQty").textContent = task ? formatTaskQty(task) : "-";'
assert src.count(needle)==1
src=src.replace(needle,needle+'\n  const caseNote=warehouseTaskEl("warehouseTaskCaseNote");\n  if(caseNote)caseNote.hidden=task?.source_doc_type!=="ST_DEFER_CASE";')
files[p]=src
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html";src=read(p)
src=src.replace('<option value="ST_DEFER">Перенос СТ</option>','<option value="ST_DEFER">Перенос СТ · паллета</option><option value="ST_DEFER_CASE">Перенос СТ · CASE</option>')
needle='<div class="rights-summary"><span id="warehouseTaskDetailStatus">Выберите задание</span></div>'
assert src.count(needle)==1
src=src.replace(needle,needle+'\n            <p id="warehouseTaskCaseNote" hidden class="subtle">Перемещается одно готовое грузовое место CASE целиком. Товарные количества и резервы каждой партии сохраняются; «1 CASE» означает число мест, а не одну единицу товара.</p>')
src=src.replace('warehouse-tasks.js?v=20261013-862','warehouse-tasks.js?v=20261013-969')
files[p]=src
# Keep receiving history heading visible below the fixed shell header.
p="wiki-raw/wms_admin_ui_reference/receiving.html";src=read(p)
needle='<article class="panel" id="receiptHistory"';assert needle in src
src=src.replace(needle,'<article class="panel" style="scroll-margin-top:90px" id="receiptHistory"',1).replace("20261013-946","20261013-969");files[p]=src
print(json.dumps(files,ensure_ascii=True))
