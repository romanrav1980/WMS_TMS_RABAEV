from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py");s=p.read_text(encoding="utf-8")
s=s.replace('def read_shortage(gateway: Any,receipt_id: str,actor: str)','def read_shortage(gateway: Any,receipt_id: str,actor: str,selected_request: str|None=None)',1)
s=s.replace("recovery,placement_plan,placement,onward=read_recovery(cur,claim)","recovery,placement_plan,placement,onward,recovery_cases=read_recovery(cur,claim,selected_request)",1)
s=s.replace("if recovery and recovery[4]:\n            cur.execute","if claim and claim[4]:\n            cur.execute",1)
s=s.replace("where r.RECOVERY_OPERATION_ID=:recovery_id and r.LOSS_OPERATION_ID=:loss_id","where r.LOSS_OPERATION_ID=:loss_id",1)
s=s.replace('recovery_id=recovery[4],loss_id=claim[4]','loss_id=claim[4]',1)
s=s.replace('for unit in units:unit["recovered"]=unit["key"]in recovered_keys','''claims={key:case["request_operation_id"]for case in recovery_cases for key in case["unit_keys"]}
        for unit in units:
            unit["recovered"]=unit["key"]in recovered_keys
            unit["recovery_report_operation_id"]=claims.get(unit["key"])''',1)
s=s.replace('recovered_qty=Decimal(str(recovery[6]))if recovery and recovery[6]is not None else Decimal(0)','''recovered_qty=sum((Decimal(case["recovered_quantity"])for case in recovery_cases if case["receipt_operation_id"]),Decimal(0))
        reported_qty=sum((Decimal(case["request_quantity"])for case in recovery_cases),Decimal(0))
        if recovered_qty>shortage or reported_qty>shortage:raise StoreReturnReceiveError("RECOVERY_HISTORY_QUANTITY_CONFLICT","Восстановление превышает исходную недостачу",409)''',1)
s=s.replace('article=domain.get("article"),profiles=profiles,','article=domain.get("article"),profiles=profiles,recovery_cases=recovery_cases,\n                    unreported_recovery_quantity=str(shortage-reported_qty),recovery_selection_quantity=next((case["request_quantity"]for case in recovery_cases if recovery and case["request_operation_id"]==recovery[0]),None),',1)
s=s.replace('recovered_quantity=str(recovery[6])if recovery and recovery[6]is not None else"0"','recovered_quantity=str(recovered_qty)',1)
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
s=s.replace("def shortage(self,receipt_id: str,actor: str)","def shortage(self,receipt_id: str,actor: str,selected_request: str|None=None)",1).replace("return read_shortage(self.gateway,receipt_id,actor)","return read_shortage(self.gateway,receipt_id,actor,selected_request)",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py");s=p.read_text(encoding="utf-8").replace("def shortage(self,receipt_id: str,actor: str)","def shortage(self,receipt_id: str,actor: str,selected_request: str|None=None)",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8").replace("from typing import Any, Literal","from typing import Any, Literal, Annotated",1)
s=s.replace('def shortage(receipt_id: str,user:','def shortage(receipt_id: str,selected_request: str|None=Query(default=None,min_length=1,max_length=100),user:',1)
s=s.replace('try:return service.shortage(receipt_id,user.username)','try:return service.shortage(receipt_id,user.username,selected_request)',1)
s=s.replace('body.model_dump(include={"quantity","reason","evidence_reference"})','body.model_dump(include={"quantity","reason","evidence_reference","unit_keys"},exclude_defaults=True)',1)
s=s.replace('class RecoveryReport(ShortageEvidence):','class RecoveryReport(ShortageEvidence):\n    unit_keys: list[Annotated[str,Field(strict=True,min_length=1,max_length=64)]]=Field(default_factory=list,max_length=10000)',1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/order_delivery_receipts.sql");s=p.read_text(encoding="utf-8")
s=s.replace('loss.SHORT_QTY,loss.OPERATION_ID LOSS_ID,found.BASE_QTY FOUND_QTY,','''loss.SHORT_QTY,loss.OPERATION_ID LOSS_ID,
 (select nvl(sum(found.BASE_QTY),0)from RRL_INTERWARE_RECOVERY_RECEIPT found
 join RRL_STOCK_OPERATION fo on fo.OPERATION_ID=found.OPERATION_ID and fo.STATE='APPLIED'and fo.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'
 where found.LOSS_OPERATION_ID=loss.OPERATION_ID)FOUND_QTY,''',1)
a=s.index(' left join RRL_INTERWARE_RECOVERY_RECEIPT found on');b=s.index(' left join RRL_STORE_DISCREPANCY_CASE',a);s=s[:a]+s[b:]
s=s.replace(' recovery_op found issue)',' recovery_op issue)');out[p.as_posix()]=s
print(json.dumps(out))
