from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_recovery_read.py");s=p.read_text(encoding="utf-8")
s=s.replace("    return recovery,placement_plan,placement",'''    onward=None
    if recovery and recovery[4]:
        cur.execute("""select b.OPERATION_ID,b.ST_ID,b.ST_IDENTIFIER,b.ST_NUMBER_TEXT,b.TARGET_TT_ID,
            d.OPERATION_ID,receipt.OPERATION_ID,receipt.RECEIPT_STATE
            from(select OPERATION_ID,ST_ID,ST_IDENTIFIER,TARGET_TT_ID,RECOVERY_OPERATION_ID,
            (select ST_NUMBER from RRL_SBORKA_PALLETS st where st.ID=binding.ST_ID)ST_NUMBER_TEXT
            from RRL_IW_RECOVERY_ST_BIND binding) b
            left join RRL_IW_RECOVERY_DISPATCH d on d.BIND_OPERATION_ID=b.OPERATION_ID
            left join RRL_STORE_RECEIPT_FACT receipt on receipt.LOAD_OPERATION_ID=d.OPERATION_ID
            where b.RECOVERY_OPERATION_ID=:recovery_id""",recovery_id=recovery[4])
        onward=cur.fetchone()
    return recovery,placement_plan,placement,onward''',1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_shortage.py");s=p.read_text(encoding="utf-8")
s=s.replace("recovery,placement_plan,placement=read_recovery","recovery,placement_plan,placement,onward=read_recovery",1)
s=s.replace('status="RECOVERED_PLACED_PENDING_REDELIVERY"','recovery_st_binding_operation_id=onward[0]if onward else None,recovery_st_id=onward[1]if onward else None,\n                    recovery_st_identifier=onward[2]if onward else None,recovery_st_number=onward[3]if onward else None,\n                    recovery_target_trip_id=onward[4]if onward else None,recovery_dispatch_operation_id=onward[5]if onward else None,\n                    recovery_final_receipt_operation_id=onward[6]if onward else None,recovery_final_receipt_state=onward[7]if onward else None,\n                    status="RECOVERY_FINAL_RECEIPT_RECORDED"if onward and onward[6]else"RECOVERY_DISPATCHED"if onward and onward[5]else"RECOVERY_ST_PREPARED"if onward else"RECOVERED_PLACED_PENDING_REDELIVERY"',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
needle='<button id="iwRecoveryPlace" type="button">Создать задание размещения найденного товара</button>'
s=s.replace(needle,needle+'''<label>Рейс повторной доставки <input id="iwRecoveryTrip" inputmode="numeric"></label><button id="iwRecoveryPrepare" type="button">Подготовить СТ найденного товара</button>''',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('el("iwRecoveryStatus").textContent=r.recovery_placement_operation_id?','el("iwRecoveryStatus").textContent=r.recovery_final_receipt_operation_id?"Повторная конечная приёмка "+r.recovery_final_receipt_operation_id+" · "+r.recovery_final_receipt_state:r.recovery_dispatch_operation_id?"Найденный товар отгружен повторно · "+r.recovery_st_number:r.recovery_st_id?"Повторная СТ "+r.recovery_st_number+" · рейс "+r.recovery_target_trip_id:r.recovery_placement_operation_id?',1)
needle=' el("iwRecoveryPlace").addEventListener'
s=s.replace(needle,''' el("iwRecoveryPrepare").addEventListener("click",async()=>{if(busy||pending)return;try{
 const r=currentShortage,trip=Number(el("iwRecoveryTrip").value);
 if(!r||r.receipt_operation_id!==el("iwShortReceipt").value||!r.recovery_placement_operation_id||r.recovery_st_id||!Number.isSafeInteger(trip)||trip<1)throw Error("Загрузите размещённый найденный товар и укажите плановый рейс повторной доставки.");
 const body={operation_id:"INTERWARE.RECOVERY.ST:"+crypto.randomUUID(),recovery_operation_id:r.recovery_receipt_operation_id,target_trip_id:trip,reason:el("iwRecoveryReason").value.trim(),decision_reference:el("iwRecoveryEvidence").value.trim()};
 if(!body.reason||!body.decision_reference)throw Error("Укажите причину и основание повторной доставки.");
 const intent={path:"/prepare-recovery-onward",body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());currentShortage=null;
 }catch(e){say(e.message);controls();}});
'''+needle,1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
s=s.replace('<th>Подтверждённая транспортная недостача</th>','<th>Остаётся потерянным в транспорте</th><th>История транспортной недостачи</th><th>Найдено на складе</th>',1)
s=s.replace('Транспортная недостача входит в неполученное количество. Она не означает приёмку товара и не списывает складской запас повторно.','Неполученное количество уменьшается только фактической приёмкой покупателя. История недостачи и найденный на складе товар показаны отдельно; находка не означает приёмку покупателем.',1);out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/order-delivery.js");s=p.read_text(encoding="utf-8")
s=s.replace('line.confirmed_transport_shortage||"0"]','line.confirmed_transport_shortage||"0",line.historical_transport_shortage||"0",line.recovered_transport_quantity||"0"]',1)
s=s.replace('row.confirmed_transport_shortage&&row.confirmed_transport_shortage!=="0"','row.historical_transport_shortage&&row.historical_transport_shortage!=="0"').replace('row.confirmed_transport_shortage+" / "','row.historical_transport_shortage+" / "')
s=s.replace('return p;}));','p.textContent+=(row.is_corrective_receipt?" · повторная доставка найденного груза":"")+(row.recovered_transport_quantity&&row.recovered_transport_quantity!=="0"?" · найдено "+row.recovered_transport_quantity:"");return p;}));',1);out[p.as_posix()]=s
print(json.dumps(out))
