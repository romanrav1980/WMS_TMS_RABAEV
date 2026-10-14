from pathlib import Path
import json
out={};p=Path("api/wms_api_server/app/modules/finance/infrastructure/box_costs.py");s=p.read_text(encoding="utf-8");out["tmp/356_before_box_costs.py"]=s
s=s.replace("from ..domain.amount import cost_amount","from ..domain.amount import cost_amount\nfrom ..domain.physical_boxes import physical_box_count",1)
old='                physical=sum(1 for node in tree.get("nodes",[])if node.get("kind")=="CONTAINER" and node.get("type")=="BOX")\n                if boxes<=0 or physical!=boxes:raise LogisticsCostError("COST_COMPLETE_PHYSICAL_BOX_PROOF_REQUIRED","Нужен подтверждённый полный состав физических коробок")'
new="""                cur.execute(\"\"\"select BOX_UID,BOX_CONTENT_VERSION,CASE_BOX_TASK_ID,MEASUREMENT_ORIGIN,
                  FINAL_SCALE_CAPTURE,WAREHOUSE_QC_OPERATION,GROSS_WEIGHT_KG,TARE_WEIGHT_KG,NET_WEIGHT_KG,
                  SIGNATURE_VERSION,MEASURED_CONTENT_VERSION,COVERAGE_COMPLETE
                  from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:load_id order by BOX_UID fetch first 201 rows only\"\"\",load_id=load)
                columns=[x[0].lower()for x in cur.description]
                proofs=[dict(zip(columns,row))for row in cur.fetchall()]
                try:physical=physical_box_count(tree,proofs)
                except ValueError as exc:raise LogisticsCostError("COST_COMPLETE_PHYSICAL_BOX_PROOF_REQUIRED",str(exc))from exc
                if physical!=boxes:raise LogisticsCostError("COST_COMPLETE_PHYSICAL_BOX_PROOF_REQUIRED","Количество физических коробок изменилось")"""
assert old in s;s=s.replace(old,new);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");s=p.read_text(encoding="utf-8");s=s.replace("c.VERSION_NO,c.BASIS\n","c.VERSION_NO,c.BASIS,h.COMPONENTS_JSON COMPONENTS\n",1).replace("        join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=c.LOAD_OPERATION_ID","        join RRL_LOGISTICS_RATE_HISTORY h on h.RATE_KEY=c.RATE_KEY and h.VERSION_NO=c.VERSION_NO\n        join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=c.LOAD_OPERATION_ID",1);out[p.as_posix()]=s
p=Path("admin/wms_admin_frontend/src/features/finance/BillingWarehouseCosts.tsx");s=p.read_text(encoding="utf-8").replace("basis:string};","basis:string;components?:{picking_rate:string;common_work_rate:string;month:string}|null};",1);s=s.replace("<td>{r.rate_value}</td>","<td>{r.rate_value}{r.components&&<small> · комплектация {r.components.picking_rate} + общие работы {r.components.common_work_rate} ({r.components.month})</small>}</td>",1);out[p.as_posix()]=s
print(json.dumps(out))
