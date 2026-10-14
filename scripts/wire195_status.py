from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py");t=p.read_text(encoding="utf-8")
a='                return read_oracle_json(q.callfunc("RRL_WEIGHT_BOX_PLANNING_READ.snapshot_json", oracledb.DB_TYPE_CLOB, [row, actor, permission]))'
b='''                result = read_oracle_json(q.callfunc("RRL_WEIGHT_BOX_PLANNING_READ.snapshot_json", oracledb.DB_TYPE_CLOB, [row, actor, permission]))
                q.execute("""select CHOICE_ID,STATUS,RRL_STOCK_PLAN_HELPER.decimal_text(NET_WEIGHT_KG),PICK_PLAN_ID
                    from RRL_PICK_WEIGHT_CHOICE where CUSTOMER_ORDER_ROW_ID=:p_row and WARE_ID=:p_ware
                      and STATUS in('ACCEPTED','USED') fetch first 2 rows only""", p_row=row,p_ware=result["warehouse_id"])
                choices = q.fetchall()
                if len(choices)>1:
                    raise StockPostingError("WEIGHT_BOX_ACTIVE_CHOICE_AMBIGUOUS", None, 20887)
                result["active_choice"] = ({"choice_id": choices[0][0], "status": choices[0][1],
                    "selected_net_weight_kg": choices[0][2], "pick_plan_id": choices[0][3]} if choices else None)
                return result'''
assert a in t;out[str(p)]=t.replace(a,b)
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");t=p.read_text(encoding="utf-8").replace('row.unit_code === "KG" && orderCan("pick_plan_create")','row.unit_code === "KG" && (orderCan("pick_plan_create") || orderCan("case_pick_short_approve"))');out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/weighted-plan-choice.js");t=p.read_text(encoding="utf-8")
t=t.replace(' + row + "/weighted-box-options"',' + row + (orderCan("case_pick_short_approve") ? "/weighted-box-approval-preview" : "/weighted-box-options")')
t=t.replace('      window.orderWeightedChoice = {row, source: data, panel, body};','      window.orderWeightedChoice = {row, source: data, panel, body};\n      document.dispatchEvent(new CustomEvent("nicora-weighted-options", {detail: window.orderWeightedChoice}));')
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");t=p.read_text(encoding="utf-8");a='<script src="weighted-plan-choice.js"></script>';assert a in t
out[str(p)]=t.replace(a,a+'<script src="weighted-plan-approval.js"></script>')
print(json.dumps(out,ensure_ascii=True))
