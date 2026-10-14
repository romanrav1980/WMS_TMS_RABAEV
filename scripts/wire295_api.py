from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8");s+='''\n    def shortage_action(self,kind: str,operation: str,source_id: str,metadata: dict,actor: str) -> dict:
        key="receipt_operation_id"if kind=="INTERWARE_SHORTAGE_REPORT"else "request_operation_id"
        return self.posting.post(StockCommand(operation_id=operation,command_type=kind,actor=actor,source={key:source_id},lines=(),metadata=metadata))
''';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8");s=s.replace("class InterwarehousePort(Protocol):","class InterwarehousePort(Protocol):\n    def shortage_action(self,kind: str,operation: str,source_id: str,metadata: dict,actor: str) -> dict[str,Any]: ...",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8");s+='''
class ShortageEvidence(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    quantity: str=Field(strict=True,min_length=1,max_length=60)
    reason: str=Field(strict=True,min_length=8,max_length=500)
    evidence_reference: str=Field(strict=True,min_length=1,max_length=255)

class ShortageReport(ShortageEvidence):
    receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)

class ShortageConfirmation(ShortageEvidence):
    request_operation_id: str=Field(strict=True,min_length=1,max_length=100)

def post_shortage(kind: str,body: ShortageEvidence,source_id: str,user: AdminUser,service: InterwarehousePort) -> dict:
    from ..contracts_stock import StockPostingError
    try:return service.shortage_action(kind,body.operation_id,source_id,body.model_dump(include={"quantity","reason","evidence_reference"}),user.username)
    except StockPostingError as exc:
        confirmed=exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed})from exc

@router.post("/shortage-reports")
def report_shortage(body: ShortageReport,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                    service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_SHORTAGE_REPORT",body,body.receipt_operation_id,user,service)

@router.post("/shortage-confirmations")
def confirm_shortage(body: ShortageConfirmation,user: AdminUser=Depends(require_permission("store_return_approve")),
                    service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_SHORTAGE_CONFIRM",body,body.request_operation_id,user,service)
''';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py");s=p.read_text(encoding="utf-8")
needle='        return dict(receipt_operation_id=receipt_id'
s=s.replace(needle,'''        cur.execute("""select req.OPERATION_ID,req.ACTOR,req.REASON_TEXT,req.EVIDENCE_REFERENCE,
            fact.OPERATION_ID,fact.ACTOR,fact.REASON_TEXT,fact.EVIDENCE_REFERENCE
            from RRL_INTERWARE_SHORTAGE_REQUEST req left join RRL_INTERWARE_SHORTAGE_FACT fact on fact.REQUEST_OPERATION_ID=req.OPERATION_ID
            where req.RECEIPT_OPERATION_ID=:receipt_id""",receipt_id=receipt_id)
        claim=cur.fetchone()
'''+needle,1)
s=s.replace('status="OPEN_SHORTAGE"if shortage>0 else"FULL_RECEIPT",','status="CONFIRMED_CARRIER_SHORTAGE"if claim and claim[4]else"PENDING_INDEPENDENT_CONFIRMATION"if claim else"OPEN_SHORTAGE"if shortage>0 else"FULL_RECEIPT",\n                    shortage_request_operation_id=claim[0]if claim else None,shortage_reporter=claim[1]if claim else None,\n                    shortage_confirmation_operation_id=claim[4]if claim else None,shortage_approver=claim[5]if claim else None,\n                    shortage_confirmation_reason=claim[6]if claim else None,shortage_confirmation_evidence=claim[7]if claim else None,')
s=s.replace('loss_confirmed=False,','loss_confirmed=bool(claim and claim[4]),')
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
