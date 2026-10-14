import sys
from pathlib import Path
from decimal import Decimal
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
from app.modules.delivery.domain.receipt_totals import combine_receipts
base=dict(load_operation_id="original",original_lot_uid="orig",lot_uid="part1",actual_final_load_operation_id="load1",receipt_operation="rec1",shipped="1",accepted="1",missing="0",refused="0",damaged="0",confirmed_transport_shortage="2",recovered_transport_quantity="2",initial_shipped_quantity="1",transport_shortage_operation_id="loss",is_corrective_receipt=0,case_status=None)
second=dict(base,lot_uid="found2",actual_final_load_operation_id="load2",receipt_operation="rec2",shipped="2",accepted="2",is_corrective_receipt=1)
result=combine_receipts([base,second],Decimal(3));assert result["accepted"]==3 and result["historical_transport_shortage"]==2 and result["unreceived"]==0
for rows in [[base,base],[base,dict(second,shipped="3",accepted="3")],[base,dict(second,transport_shortage_operation_id="foreign")],[base,dict(second,accepted="1")]]:
 try:combine_receipts(rows,Decimal(3))
 except ValueError:pass
 else:raise AssertionError("invalid corrective credit accepted")
print("PASS303 duplicate/excess/foreignloss/disposition conservation and explicit1+2")
