import sys
sys.path.insert(0,"api/wms_api_server")
from app.modules.delivery.domain.order_delivery import project_delivery
legs=[dict(shipping_operation="source",shipment_id=1,leg_no=1,lot_uid="original",article="sku",base_uom="EA",quantity="3",owner_order_id=1)]
ffs=[dict(status="SHIPPED",shipping_operation="source",shipment_id=1,load_operation_id="source")]
receipt=dict(load_operation_id="source",lot_uid="new",original_lot_uid="original",receipt_operation="ack",case_status=None,shipped="1",accepted="1",missing="0",refused="0",damaged="0",confirmed_transport_shortage="2")
x=project_delivery(1,legs,ffs,[receipt]);assert x["delivery_status"]=="PARTIALLY_ACCEPTED"and x["quantities"][0]["confirmed_transport_shortage"]=="2"and x["quantities"][0]["accepted"]=="1"
try:project_delivery(1,legs,ffs,[dict(receipt,confirmed_transport_shortage="1")])
except ValueError:pass
else:raise AssertionError("unaccounted source credited")
shared=[dict(legs[0],quantity="1"),dict(legs[0],quantity="2",owner_order_id=2,shipment_id=2)]
x=project_delivery(1,shared,ffs,[receipt]);assert x["delivery_status"]=="NEEDS_OWNER_ALLOCATION"and x["quantities"][0]["accepted"]=="0"
print("PASS297 exact source-accounted oneowner only, mismatched quantity refused, sharedpartial remains explicitly unallocated")
