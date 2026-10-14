from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8")
needle='    base_uom: str = Field(strict=True,min_length=1,max_length=20)'
assert needle in s
s=s.replace(needle,needle+'''
    partial_receipt: bool | None = Field(strict=True,default=None)
    receipt_pallet_identifier: str | None = Field(strict=True,default=None,min_length=1,max_length=50)
    gross_weight_kg: str | None = Field(strict=True,default=None,pattern=r"^[0-9]{1,18}(\\.[0-9]{1,9})?$")
    discrepancy_reason: str | None = Field(strict=True,default=None,min_length=8,max_length=1000)
    discrepancy_reference: str | None = Field(strict=True,default=None,min_length=1,max_length=255)

    @model_validator(mode="after")
    def partial_fields(self) -> "Receive":
        fields=(self.receipt_pallet_identifier,self.gross_weight_kg,self.discrepancy_reason,self.discrepancy_reference)
        if self.partial_receipt:
            if any(value is None for value in fields):
                raise ValueError("При частичной приёмке укажите новую паллету, вес, причину и документ расхождения")
        elif any(value is not None for value in fields):
            raise ValueError("Поля расхождения требуют явного режима частичной приёмки")
        return self
''',1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.sql");s=p.read_text(encoding="utf-8")
needle=" t.TRANSPORT VEHICLE_NUMBER,u.OPERATION_ID UNLOAD_OPERATION_ID,r.OPERATION_ID RECEIPT_OPERATION_ID,"
assert needle in s;s=s.replace(needle,""" r.ROOT_UID RECEIVED_PALLET_IDENTIFIER,RRL_STOCK_PLAN_HELPER.decimal_text(r.BASE_QTY)RECEIVED_QUANTITY,
 RRL_STOCK_PLAN_HELPER.decimal_text(case when r.EXPECTED_BASE_QTY is not null then r.EXPECTED_BASE_QTY-r.BASE_QTY else 0 end)SHORT_QUANTITY,
 r.DISCREPANCY_REASON,r.DISCREPANCY_REFERENCE,
"""+needle,1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.sql");s=p.read_text(encoding="utf-8")
needle=" u.OPERATION_ID UNLOAD_OPERATION_ID,r.OPERATION_ID RECEIPT_OPERATION_ID,"
assert needle in s;s=s.replace(needle,""" case when r.OPERATION_ID is not null and(r.EXPECTED_BASE_QTY is null or r.BASE_QTY=r.EXPECTED_BASE_QTY)then 1 else 0 end RECEIPT_COMPLETE,
 RRL_STOCK_PLAN_HELPER.decimal_text(r.BASE_QTY)RECEIVED_QUANTITY,
 RRL_STOCK_PLAN_HELPER.decimal_text(case when r.EXPECTED_BASE_QTY is not null then r.EXPECTED_BASE_QTY-r.BASE_QTY else 0 end)SHORT_QUANTITY,
 r.ROOT_UID RECEIVED_PALLET_IDENTIFIER,
"""+needle,1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/domain/interwarehouse_readiness.py");s=p.read_text(encoding="utf-8")
s=s.replace('row["ready"] = row["physically_loaded"] and row["temperature_decision"]!="HOLD"','row["ready"] = row["physically_loaded"] and row["temperature_decision"]!="HOLD" and row.get("receipt_complete",1)==1')
out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
needle=' el("iwReceive").parentElement.append(marks);'
assert needle in s
s=s.replace(needle,needle+'''
 const partialPanel=document.createElement("section");
 partialPanel.innerHTML='<h3>Приёмка с недостачей</h3><label><input type="checkbox" id="iwPartialReceipt"> Зафиксировать фактически принятое количество и недостачу</label><label>Идентификатор принятой паллеты <input id="iwPartialPallet" maxlength="50"></label><label>Фактически наблюдаемый вес брутто, кг <input id="iwPartialGross"></label><label>Причина расхождения <textarea id="iwPartialReason" maxlength="1000"></textarea></label><label>Документ / основание расхождения <input id="iwPartialReference" maxlength="255"></label><p>Принятый товар учитывается на отдельной паллете. Непринятая часть остаётся открытым обязательством перевозчика. Для маркированного товара требуется точное подтверждение состава единиц.</p>';
 el("iwReceive").parentElement.append(partialPanel);
''')
# Locate the actual receipt body construction rather than replace the whole flow.
needle='if(path==="/receive"&&unitScans.length)'
if needle not in s:
    matches=[line for line in s.splitlines()if 'body.scans' in line]
    assert len(matches)==1,matches
    line=matches[0];needle='if(path==="/receive"&&unitScans.length)'
    assert needle in line,line
insert='''if(path==="/receive"&&el("iwPartialReceipt").checked){body.partial_receipt=true;body.receipt_pallet_identifier=el("iwPartialPallet").value.trim();body.gross_weight_kg=el("iwPartialGross").value.trim();body.discrepancy_reason=el("iwPartialReason").value.trim();body.discrepancy_reference=el("iwPartialReference").value.trim();if(!body.receipt_pallet_identifier||!body.gross_weight_kg||body.discrepancy_reason.length<8||!body.discrepancy_reference)throw Error("Укажите принятую паллету, вес и основание расхождения.");}'''
assert needle in s;s=s.replace(needle,insert+needle,1)
# Queue status explains the existing received fragment separately from frozen source.
needle='row.receipt_operation_id?'
if needle in s:
 s=s.replace(needle,'row.receipt_operation_id?',1)
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
