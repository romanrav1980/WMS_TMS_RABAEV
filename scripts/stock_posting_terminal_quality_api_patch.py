import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/schemas.py");s=p.read_text(encoding="utf-8")
s=s.replace("class LotCheckRequest(BaseModel):\n    user_id: str\n    error_count: int = 0\n    errors: list[TerminalErrorLine] = Field(default_factory=list)\n    vp_lines: list[TerminalVpLine] = Field(default_factory=list)","class LotCheckRequest(BaseModel):\n    operation_id: str | None = Field(default=None, min_length=1, max_length=100)\n    user_id: str\n    error_count: int = Field(default=0, ge=0)\n    errors: list[TerminalErrorLine] = Field(default_factory=list, max_length=200)\n    vp_lines: list[TerminalVpLine] = Field(default_factory=list, max_length=200)")
s=s.replace("class TerminalErrorLine(BaseModel):\n    uid: str\n    qty: float","class TerminalErrorLine(BaseModel):\n    uid: str\n    qty: Decimal = Field(ge=0, max_digits=27, decimal_places=9)",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8")
s+='\n\nfrom .api.error_handlers import install_stock_error_handlers\n\ndef post_existing_terminal_quality(gateway, pallet: str, request):\n    from .infrastructure.terminal_quality_commands import post_terminal_quality\n    return post_terminal_quality(gateway, pallet, request)\n'
out[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8")
s=s.replace('app = FastAPI(title=settings.api_title, version=settings.api_version)','app = FastAPI(title=settings.api_title, version=settings.api_version)\ninventory_receiving.install_stock_error_handlers(app)',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/services/tserver_service.py");s=p.read_text(encoding="utf-8")
s=s.replace('def execute_legacy_payload(self, payload: str)','def execute_legacy_payload(self, payload: str, actor: str | None = None)')
s=s.replace("response = self._dispatch(blocks)","response = self._dispatch(blocks, actor)",1)
s=s.replace("def _dispatch(self, blocks: list[LegacyBlock])","def _dispatch(self, blocks: list[LegacyBlock], actor: str | None = None)")
s=s.replace('request = self._lot_check_from_legacy(blocks)\n            self.confirm_lot_check','request = self._lot_check_from_legacy(blocks)\n            if actor is not None: request.user_id = actor\n            self.confirm_lot_check',1)
needle='''            result = self.call_spf(CallSpfRequest(spf_name=head.get("SPF_NAME"), params=head.values))'''
replacement='''            params = dict(head.values)
            if actor is not None:
                for key in params:
                    if key.lower() in {"user_id", "user_id1", "user_id2", "iser_id1", "iser_id21", "user_id3", "kladovshik1", "p_actor", "p_created_by"}:
                        params[key] = actor
            result = self.call_spf(CallSpfRequest(spf_name=head.get("SPF_NAME"), params=params))'''
assert needle in s;s=s.replace(needle,replacement,1)
s=s.replace('usscc = normalize_pallet_identifier(usscc)\n        statements:', '''usscc = normalize_pallet_identifier(usscc)
        from ..modules.inventory.public import post_existing_terminal_quality
        if post_existing_terminal_quality(self.gateway, usscc, request) is not None:
            return
        statements:''',1)
s=s.replace('return LotCheckRequest(\n            user_id=head.get("USER_ID"),','return LotCheckRequest(\n            operation_id=head.get("OPERATION_ID") or None,\n            user_id=head.get("USER_ID"),',1)
s=s.replace('"qty": float(block.get(QTY_KEY, "0") or 0),','"qty": block.get(QTY_KEY, "0") or "0",',1)
out[str(p)]=s
p=Path("api/wms_api_server/app/routers/tserver.py");s=p.read_text(encoding="utf-8")
s=s.replace("from fastapi import APIRouter","from fastapi import APIRouter, Depends, HTTPException\nfrom ..auth import AdminUser, get_current_admin, serialize_admin_user",1)
s=s.replace("def execute_legacy_tserver(request: LegacyExecuteRequest)","def execute_legacy_tserver(request: LegacyExecuteRequest, user: AdminUser = Depends(get_current_admin))",1)
s=s.replace("TserverService().execute_legacy_payload(request.payload)","TserverService().execute_legacy_payload(request.payload, user.username)",1)
needle='''def confirm_lot_check(usscc: str, request: LotCheckRequest) -> dict[str, str]:
    TserverService().confirm_lot_check(usscc, request)'''
replacement='''def confirm_lot_check(usscc: str, request: LotCheckRequest, user: AdminUser = Depends(get_current_admin)) -> dict[str, str]:
    request.user_id = user.username
    try:
        TserverService().confirm_lot_check(usscc, request)
    except ValueError as error:
        raise HTTPException(422, detail={"code": "QUALITY_REQUEST_INVALID", "message": str(error),
            "operation_id": request.operation_id, "outcome_confirmed": False}) from error'''
assert needle in s;s=s.replace(needle,replacement,1)
s+='\n\n@router.get("/terminal/auth/me")\ndef terminal_identity(user: AdminUser = Depends(get_current_admin)) -> dict:\n    return serialize_admin_user(user)\n'
out[str(p)]=s
for name in ("case-pick-posting.js","case-carrier-move.js"):
 p=Path("wiki-raw/wms_admin_ui_reference")/name;s=p.read_text(encoding="utf-8")
 s=s.replace(' || [400,401,403,422].includes(error.status)','').replace('||[400,401,403,422].includes(error.status)','')
 out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
