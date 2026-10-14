from pathlib import Path
import ast,json
files={};p="api/wms_api_server/app/modules/fulfillment/infrastructure/order_fulfillment_read.py";v=Path(p).read_text(encoding="utf-8")
tree=ast.parse(v);call=next(x for x in ast.walk(tree)if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and x.func.attr=="fetch_all")
arg=call.args[0];query=arg.value
assert "CASE_CURRENT_STATUS"not in query
inner=query.strip().replace("FACT_QTY,","FACT_QTY,to_char(FACT_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_QTY_EXACT,",1).replace("FACT_WEIGHT,","FACT_WEIGHT,to_char(FACT_WEIGHT,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') FACT_WEIGHT_EXACT,",1)
sql="select f.*,ct.SSCC CASE_IDENTIFIER,ct.CURRENT_CELL CASE_CURRENT_CELL,ct.CONTENT_VERSION CASE_CURRENT_VERSION,ct.STATUS CASE_CURRENT_STATUS from ("+inner+") f left join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=f.PICKED_CASE_TASK_ID and ct.CUSTOMER_ORDER_ID=f.CUSTOMER_ORDER_ID and ct.WARE_ID=:p_warehouse order by f.FULFILLMENT_ID"
v=v.replace(ast.get_source_segment(v,arg),repr(sql),1);files[p]=v
p="api/wms_api_server/app/modules/fulfillment/public.py";v=Path(p).read_text(encoding="utf-8")
v="from typing import Any\n"+v
v=v.replace("def build_fulfillment_read_service(gateway=None)","def build_fulfillment_read_service(gateway: Any | None = None)",1);files[p]=v
print(json.dumps(files,ensure_ascii=True))
