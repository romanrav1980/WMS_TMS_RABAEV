"""Expose carrier binding in the existing CASE API and terminal."""
import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+='''

def bind_existing_case_shipment(gateway, task_id: int, pallet_identifier: str,
                               scan_container: str, expected_version: int, actor: str):
    from .infrastructure.case_shipment_binding import bind_case_shipment
    return bind_case_shipment(gateway, task_id, pallet_identifier, scan_container, expected_version, actor)
'''
out[str(p)]=s
p=Path("api/wms_api_server/app/routers/case_pick.py");s=p.read_text(encoding="utf-8")
s+='''

class CaseShipmentBindRequest(BaseModel):
    pallet_identifier: str = Field(min_length=1, max_length=150)
    scan_container: str = Field(min_length=1, max_length=150)
    expected_content_version: int = Field(ge=0, strict=True)


@router.post("/tasks/{case_pick_task_id}/bind-shipment")
def bind_case_shipment(case_pick_task_id: int, request: CaseShipmentBindRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict:
    from ..modules.inventory.public import bind_existing_case_shipment
    from ..oracle_gateway import OracleGateway
    try:
        return bind_existing_case_shipment(OracleGateway(), case_pick_task_id,
            request.pallet_identifier, request.scan_container, request.expected_content_version, user.username)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
'''
out[str(p)]=s
p=Path("api/wms_api_server/app/services/case_pick_service.py");s=p.read_text(encoding="utf-8")
needle="                   t.CURRENT_CELL,t.CONTENT_VERSION,"
assert s.count(needle)==1
s=s.replace(needle,needle+"t.LEGACY_SBORKA_PALLET_ID,t.SHIPPED_OPERATION,",1)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/case-pick-tsd.html");s=p.read_text(encoding="utf-8")
needle='        <section class="tsd-actions" data-permission="case_pick_execute">'
assert s.count(needle)==1
s=s.replace(needle,'''        <section data-permission="case_pick_execute"><label>Идентификатор подготовленной паллеты СТ<input id="cpTsdShipmentIdentifier" autocomplete="off" /></label><button id="cpTsdBindShipment" type="button">Связать с отгрузкой СТ</button></section>
'''+needle,1)
s=s.replace('    <script src="case-carrier-move.js"></script>','    <script src="case-carrier-move.js"></script>\n    <script src="case-shipment-binding.js"></script>',1)
out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/068_shipping.sql");s=p.read_text(encoding="utf-8")
s=s.replace("v.put('case_carrier',v_carrier);","v.put('case_carrier',v_carrier_rows);",1)
s=s.replace("v_current clob;begin","v_current clob;v_previous clob;begin",1)
s=s.replace("    if dbms_lob.compare(v_current,v.get_clob('case_carrier'))!=0","    v_previous:=v.get_array('case_carrier').to_clob;\n    if dbms_lob.compare(v_current,v_previous)!=0",1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
