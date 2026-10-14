from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8");s+='''
    def recovery_action(self,kind: str,operation: str,source_id: str,metadata: dict,actor: str) -> dict:
        key="loss_operation_id"if kind=="INTERWARE_RECOVERY_REPORT"else "request_operation_id"
        return self.posting.post(StockCommand(operation_id=operation,command_type=kind,actor=actor,source={key:source_id},lines=(),metadata=metadata))
''';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8").replace("class InterwarehousePort(Protocol):","class InterwarehousePort(Protocol):\n    def recovery_action(self,kind: str,operation: str,source_id: str,metadata: dict,actor: str) -> dict[str,Any]: ...",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace('try:return service.shortage_action(kind,body.operation_id,source_id,body.model_dump(include={"quantity","reason","evidence_reference"}),user.username)','''try:
        action=service.recovery_action if kind.startswith("INTERWARE_RECOVERY_")else service.shortage_action
        return action(kind,body.operation_id,source_id,body.model_dump(include={"quantity","reason","evidence_reference"}),user.username)''',1)
s+='''
class RecoveryReport(ShortageEvidence):
    loss_operation_id: str=Field(strict=True,min_length=1,max_length=100)

@router.post("/recovery-reports")
def report_recovery(body: RecoveryReport,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                    service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_RECOVERY_REPORT",body,body.loss_operation_id,user,service)

@router.post("/recovery-approvals")
def approve_recovery(body: ShortageConfirmation,user: AdminUser=Depends(require_permission("store_return_approve")),
                     service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_RECOVERY_APPROVE",body,body.request_operation_id,user,service)
''';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py");s=p.read_text(encoding="utf-8")
needle='        return dict(receipt_operation_id=receipt_id'
s=s.replace(needle,'''        recovery=None
        if claim and claim[4]:
            cur.execute("""select req.OPERATION_ID,req.ACTOR,approval.OPERATION_ID,approval.ACTOR,received.OPERATION_ID,received.ROOT_UID,received.BASE_QTY
                from RRL_INTERWARE_RECOVERY_REQUEST req left join RRL_INTERWARE_RECOVERY_APPROVAL approval on approval.REQUEST_OPERATION_ID=req.OPERATION_ID
                left join RRL_INTERWARE_RECOVERY_RECEIPT received on received.APPROVAL_OPERATION_ID=approval.OPERATION_ID
                where req.LOSS_OPERATION_ID=:loss_id""",loss_id=claim[4])
            recovery=cur.fetchone()
'''+needle,1)
s=s.replace('carrier_custody_released=released is not None,','''recovery_request_operation_id=recovery[0]if recovery else None,recovery_reporter=recovery[1]if recovery else None,
                    recovery_approval_operation_id=recovery[2]if recovery else None,recovery_approver=recovery[3]if recovery else None,
                    recovery_receipt_operation_id=recovery[4]if recovery else None,recovered_pallet_identifier=recovery[5]if recovery else None,
                    recovered_quantity=str(recovery[6])if recovery and recovery[6]is not None else"0",
                    carrier_custody_released=released is not None,''',1)
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
