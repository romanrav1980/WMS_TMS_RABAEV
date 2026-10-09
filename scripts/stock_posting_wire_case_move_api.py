"""Wire the carrier move into the existing CASE API and TSD."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=1:raise RuntimeError("Missing unique anchor "+path)
 files[path]=text.replace(old,new,1)
path="api/wms_api_server/app/modules/inventory/public.py"
files[path]=(ROOT/path).read_text(encoding="utf-8")+"""

def build_case_carrier_move_service():
    from .application.case_carrier_move import CaseCarrierMove
    return CaseCarrierMove(build_stock_posting_service())
"""
path="api/wms_api_server/app/routers/case_pick.py"
edit(path,'@router.get("/tasks/{case_pick_task_id}/lines/{line_id}/marking-policy")',
"""from pydantic import BaseModel, Field


class CaseCarrierMoveRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100)
    scan_container: str = Field(min_length=1, max_length=150)
    scanned_to_cell: str = Field(min_length=1, max_length=60)
    expected_content_version: int = Field(ge=0, strict=True)


@router.post("/tasks/{case_pick_task_id}/move-carrier")
def move_case_carrier(case_pick_task_id: int, request: CaseCarrierMoveRequest,
    user: AdminUser = Depends(require_permission(CASE_PICK_EXECUTE_PERMISSION))) -> dict:
    from ..modules.inventory.public import build_case_carrier_move_service
    from ..modules.inventory.contracts_stock import StockPostingError
    try:
        return build_case_carrier_move_service().execute(request.operation_id, user.username,
            case_pick_task_id, request.scan_container, request.scanned_to_cell, request.expected_content_version)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED", "STOCK_RELEASE_NOT_ACTIVE"}
        raise HTTPException(503 if uncertain else 409, detail={"code": exc.code,
            "operation_id": exc.operation_id, "oracle_code": exc.oracle_code,
            "outcome_confirmed": not uncertain, "retry_same_operation_id": uncertain}) from exc


@router.get("/tasks/{case_pick_task_id}/lines/{line_id}/marking-policy")""")
path="wiki-raw/wms_admin_ui_reference/case-pick-tsd.html"
edit(path,'<section class="tsd-actions" data-permission="case_pick_execute">',
 '<section><label>Скан места контроля или отгрузки<input id="cpTsdCarrierDestination" autocomplete="off" /></label><button id="cpTsdMoveCarrier" data-permission="case_pick_execute">Переместить паллету отбора</button><button id="cpTsdRetryCarrier" data-permission="case_pick_execute" hidden>Повторить перемещение</button></section>\n        <section class="tsd-actions" data-permission="case_pick_execute">')
edit(path,'<script src="case-pick-posting.js"></script>','<script src="case-pick-posting.js"></script>\n    <script src="case-carrier-move.js"></script>')
path="db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"
manifest=json.loads((ROOT/path).read_text(encoding="utf-8"))
at=manifest["components"].index("024_posting.sql")
for component,package in [("160_case_pick_command.sql","RRL_STOCK_CASE_PICK_CMD"),("167_case_carrier_move.sql","RRL_STOCK_CASE_MOVE_CMD")]:
 manifest["components"].insert(at,component);at+=1;manifest["packages"].append(package)
files[path]=json.dumps(manifest,indent=2)+"\n"
base="db/migrations/2026-10-08_stock_posting_core/"
files[base+manifest["contracts"]]="\n".join((ROOT/base/f).read_text(encoding="utf-8").split("\n/\n",1)[0]+"\n/\n" for f in manifest["components"])
files[base+manifest["bundle"]]="@@"+manifest["contracts"]+"\n"+"\n".join("@@"+f for f in manifest["components"]+manifest["additional_scripts"])+"\n@@014b_recompile.sql\n"
print(json.dumps(files,ensure_ascii=True))
