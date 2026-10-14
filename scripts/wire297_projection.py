from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py");s=p.read_text(encoding="utf-8")
s=s.replace("requested.ORIGINAL_LOAD FINAL_LOAD from requested","requested.ORIGINAL_LOAD FINAL_LOAD,cast(null as varchar2(100)) INTERWARE_RECEIPT from requested",1)
s=s.replace("d.OPERATION_ID FINAL_LOAD from requested","d.OPERATION_ID FINAL_LOAD,d.RECEIPT_OPERATION_ID INTERWARE_RECEIPT from requested",1)
s=s.replace("line.LOT_UID,receipt.OPERATION_ID RECEIPT_OPERATION","""line.LOT_UID,
                   case when confirmed.STATE='APPLIED'and confirmed.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'
                    and transit.ORIGINAL_ROOT_UID is not null and transit.ROOT_UID=line.LOT_UID
                    and transit.SOURCE_LOAD_OPERATION_ID=lineage.ORIGINAL_LOAD and transit.BASE_QTY=line.SHIPPED_BASE_QTY
                    and transit.BASE_QTY+loss.SHORT_QTY=transit.EXPECTED_BASE_QTY
                    then transit.ORIGINAL_ROOT_UID else line.LOT_UID end ORIGINAL_LOT_UID,
                   RRL_STOCK_PLAN_HELPER.decimal_text(case when confirmed.STATE='APPLIED'and confirmed.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'
                    and transit.ORIGINAL_ROOT_UID is not null and transit.ROOT_UID=line.LOT_UID
                    and transit.SOURCE_LOAD_OPERATION_ID=lineage.ORIGINAL_LOAD and transit.BASE_QTY=line.SHIPPED_BASE_QTY
                    and transit.BASE_QTY+loss.SHORT_QTY=transit.EXPECTED_BASE_QTY then loss.SHORT_QTY else 0 end)CONFIRMED_TRANSPORT_SHORTAGE,
                   loss.OPERATION_ID TRANSPORT_SHORTAGE_OPERATION_ID,
                   receipt.OPERATION_ID RECEIPT_OPERATION""",1)
s=s.replace("              left join RRL_STORE_DISCREPANCY_CASE issue","""              left join RRL_INTERWARE_RECEIPT transit on transit.OPERATION_ID=lineage.INTERWARE_RECEIPT
              left join RRL_INTERWARE_SHORTAGE_FACT loss on loss.RECEIPT_OPERATION_ID=transit.OPERATION_ID
              left join RRL_STOCK_OPERATION confirmed on confirmed.OPERATION_ID=loss.OPERATION_ID
              left join RRL_STORE_DISCREPANCY_CASE issue""",1)
s=s.replace('"lot_uid":row["lot_uid"]}for row in receipt]','"lot_uid":row["lot_uid"],"original_lot_uid":row.get("original_lot_uid",row["lot_uid"]),"transport_shortage_operation_id":row.get("transport_shortage_operation_id"),"confirmed_transport_shortage":row.get("confirmed_transport_shortage","0")}for row in receipt]')
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/delivery/domain/order_delivery.py");s=p.read_text(encoding="utf-8")
s=s.replace('by_load_uid={(row["load_operation_id"],row["lot_uid"]):row for row in receipts}','''by_load_uid={(row["load_operation_id"],row.get("original_lot_uid",row["lot_uid"])):row for row in receipts}
    if len(by_load_uid)!=len(receipts):
        raise ValueError("DELIVERY_MULTIPLE_FINAL_RECEIPTS_REQUIRES_EXPLICIT_SUMMED_LINEAGE")''',1)
s=s.replace('("shipped",*FIELDS,"unreceived","unattributed")','("shipped",*FIELDS,"unreceived","unattributed","confirmed_transport_shortage")',1)
s=s.replace('if Decimal(receipt["shipped"])!=total:','''transport_short=Decimal(receipt.get("confirmed_transport_shortage","0"))
        if transport_short<0 or Decimal(receipt["shipped"])+transport_short!=total:''',1)
s=s.replace('        if len(owners)==1:\n            for field in FIELDS:','''        if len(owners)==1:
            counter["confirmed_transport_shortage"]+=transport_short
            counter["unreceived"]+=transport_short
            for field in FIELDS:''',1)
s=s.replace('elif any(value["unreceived"]>0 for value in totals.values()):','elif any(value["unreceived"]>value["confirmed_transport_shortage"] for value in totals.values()):',1)
s=s.replace('elif any(any(value[field]>0 for field in ("missing","refused","damaged"))','elif any(any(value[field]>0 for field in ("missing","refused","damaged","confirmed_transport_shortage"))',1)
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
