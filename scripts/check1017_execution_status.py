from pathlib import Path
import sys,json
sys.path.insert(0,str(Path("api/wms_api_server").resolve()))
from app.modules.fulfillment.domain.execution_progress import line_progress,order_progress_status,line_is_cancelled
base={"customer_order_row_id":1,"line_no":1,"articul":"OWN","unit_code":"BOX","row_status":"OPEN","order_quantity":"3","base_uom":"EA","numerator":12,"denominator":1,"base_scale":0,"case_fact":"2","pallet_fact":"0","hard_quantity":"0","refused_lines":0,"refusal_reason":None}
unknown=line_progress({**base,"denominator":None})
assert unknown["requested_quantity"]=="3"and unknown["requested_uom"]=="BOX"and unknown["picked_quantity"]=="2"and unknown["base_uom"]=="EA"
assert order_progress_status([unknown])=="REQUIRES_UOM"
def sample(**values):return line_progress({**base,"unit_code":"EA","order_quantity":"5","numerator":1,**values})
excess=sample(case_fact="6");assert order_progress_status([excess])=="OVER_PICKED"
cancelled=sample(row_status="CANCELLED");assert order_progress_status([cancelled])=="CANCELLED"and line_is_cancelled(cancelled)
picked=sample(case_fact="5");assert order_progress_status([picked,cancelled])=="PICKED"
short=sample(refused_lines=1,refusal_reason="Own shortage");assert order_progress_status([short])=="SHORT_CLOSED"
reserved=sample(case_fact="0",hard_quantity="5");assert order_progress_status([reserved])=="RESERVED"
assert order_progress_status([short,reserved])=="PARTIAL_REFUSED"
cancelled_excess=sample(row_status="CANCELLED",case_fact="6");assert line_is_cancelled(cancelled_excess)and order_progress_status([cancelled_excess])=="OVER_PICKED"
assert order_progress_status([])=="PENDING"
Path("tmp/execution1017.json").write_text(json.dumps({"unknown_uom":unknown,"excess":excess,"cancelled":cancelled,"closed_short":short,"reserved":reserved,"meaningful_anomaly_status_checks":True},indent=2),encoding="utf-8")
print("PASS1017 excess/closedshort/mixedshort/reserved/cancelled-active/exactrequestedUOM separation")
