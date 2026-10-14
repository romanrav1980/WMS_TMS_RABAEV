from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
s+='''
@router.post("/recovery-cancellations")
def cancel_recovery(body: ShortageConfirmation,user: AdminUser=Depends(require_permission("store_return_approve")),
                    service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_RECOVERY_CANCEL",body,body.request_operation_id,user,service)
''';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_records.py");s=p.read_text(encoding="utf-8")
s=s.replace("req.SOURCE_JSON,","req.SOURCE_JSON,cancelled.OPERATION_ID CANCEL_OPERATION_ID,cancelled.REASON_TEXT CANCEL_REASON,",1)
s=s.replace("        left join RRL_INTERWARE_RECOVERY_APPROVAL","        left join RRL_IW_RECOVERY_CANCEL cancelled on cancelled.REQUEST_OPERATION_ID=req.OPERATION_ID\n        left join RRL_INTERWARE_RECOVERY_APPROVAL",1)
s=s.replace("order by case when received.OPERATION_ID is null then 0 else 1 end","order by case when cancelled.OPERATION_ID is not null then 2 when received.OPERATION_ID is null then 0 else 1 end",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_read.py");s=p.read_text(encoding="utf-8")
s=s.replace("else:selected=records[0]if records else None","else:selected=next((r for r in records if not r['cancel_operation_id']),records[0]if records else None)",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py");s=p.read_text(encoding="utf-8")
s=s.replace('for case in recovery_cases for key in case["unit_keys"]','for case in recovery_cases if not case["cancel_operation_id"]for key in case["unit_keys"]',1)
s=s.replace('Decimal(case["request_quantity"])for case in recovery_cases)','Decimal(case["request_quantity"])for case in recovery_cases if not case["cancel_operation_id"])',1)
s=s.replace('status="RECOVERY_FINAL_RECEIPT_RECORDED"','recovery_cancel_operation_id=next((case["cancel_operation_id"]for case in recovery_cases if recovery and case["request_operation_id"]==recovery[0]),None),\n                    status="RECOVERY_REQUEST_CANCELLED"if recovery and any(case["request_operation_id"]==recovery[0]and case["cancel_operation_id"]for case in recovery_cases)else"RECOVERY_FINAL_RECEIPT_RECORDED"',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
needle='<button id="iwRecoveryPrepare" type="button">Подготовить СТ найденного товара</button>'
s=s.replace(needle,needle+'<button id="iwRecoveryCancel" type="button">Отменить выбранное сообщение до приёмки</button>',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('c.final_receipt_operation_id?"конечная приёмка"','c.cancel_operation_id?"отменено":c.final_receipt_operation_id?"конечная приёмка"',1)
s=s.replace('el("iwRecoveryStatus").textContent=r.recovery_final_receipt_operation_id?','el("iwRecoveryStatus").textContent=r.recovery_cancel_operation_id?"Сообщение отменено · "+r.recovery_cancel_operation_id:r.recovery_final_receipt_operation_id?',1)
s=s.replace('if(approve&&(r.recovery_receipt_operation_id||r.recovery_approval_operation_id))','if(approve&&(r.recovery_cancel_operation_id||r.recovery_receipt_operation_id||r.recovery_approval_operation_id))',1)
s=s.replace('||!r.recovery_approval_operation_id||r.recovery_receipt_operation_id)','||!r.recovery_approval_operation_id||r.recovery_cancel_operation_id||r.recovery_receipt_operation_id)',1)
needle=' el("iwRecoveryPrepare").addEventListener'
s=s.replace(needle,''' el("iwRecoveryCancel").addEventListener("click",async()=>{if(busy||pending)return;try{
 const r=currentShortage;if(!r||r.receipt_operation_id!==el("iwShortReceipt").value||!r.recovery_request_operation_id||r.recovery_cancel_operation_id||r.recovery_receipt_operation_id)throw Error("Выберите ещё не принятую и не отменённую найденную часть.");
 const body={operation_id:"INTERWARE.RECOVERY.CANCEL:"+crypto.randomUUID(),request_operation_id:r.recovery_request_operation_id,quantity:r.recovery_selection_quantity,reason:el("iwRecoveryReason").value.trim(),evidence_reference:el("iwRecoveryEvidence").value.trim()};
 if(body.reason.length<8||!body.evidence_reference)throw Error("Укажите причину и основание отмены.");
 const intent={path:"/recovery-cancellations",body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());currentShortage=null;
 }catch(e){say(e.message);controls();}});
'''+needle,1);out[p.as_posix()]=s
print(json.dumps(out))
