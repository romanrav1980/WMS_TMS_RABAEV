from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/fulfillment/infrastructure/legacy_preparation.py")
s=p.read_text(encoding="utf-8").replace("            from .automatic_preparation import lock_layout_inputs\n            lock_layout_inputs(cur, order_id)\n","")
needle="        st_number='SAP_'+str(order_id)"
s=s.replace(needle,"        from .automatic_preparation import lock_layout_inputs\n        lock_layout_inputs(cur, order_id)\n"+needle)
# One shared writer records the operation for explicit/manual and automatic receipts.
s=s.replace("'status':'ST_PREPARED','layout_source':'OPERATOR'","'operation_id':payload['operation_id'],'status':'ST_PREPARED','layout_source':'OPERATOR'")
print(json.dumps({str(p):s},ensure_ascii=True))
