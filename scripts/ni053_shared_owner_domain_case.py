"""The only ambiguous case is intentionally unresolved, never proportional credit."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.modules.delivery.domain.order_delivery import project_delivery
legs=[{"shipping_operation":"OP","lot_uid":"LOT","article":"SKU","base_uom":"EA","owner_order_id":1,"shipment_id":11,"quantity":"1"},
      {"shipping_operation":"OP","lot_uid":"LOT","article":"SKU","base_uom":"EA","owner_order_id":2,"shipment_id":22,"quantity":"2"}]
fulfillment=[{"shipment_id":11,"status":"SHIPPED","shipping_operation":"OP","load_operation_id":"LOAD"}]
receipt=[{"load_operation_id":"LOAD","lot_uid":"LOT","receipt_operation":"RECEIPT","case_status":"OPEN","shipped":"3","accepted":"2","missing":"1","refused":"0","damaged":"0"}]
partial=project_delivery(1,legs,fulfillment,receipt)
assert partial["delivery_status"]=="NEEDS_OWNER_ALLOCATION"
assert partial["quantities"][0]["accepted"]=="0" and partial["quantities"][0]["unattributed"]=="1"
receipt[0].update(accepted="3",missing="0",case_status=None)
full=project_delivery(1,legs,fulfillment,receipt)
assert full["quantities"][0]["accepted"]=="1" and not full["needs_owner_allocation"]
print("PASS090 exact domain shared partial leaf remains uncredited; fully accepted original leaf credits original owner1 only")
