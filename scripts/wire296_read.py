from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-11_ni061_partial_custody")
s=(d/"000_before_load_fact_guard.sql").read_text(encoding="utf-8")
needle="join RRL_INTERWARE_UNLOAD u on u.OPERATION_ID=r.UNLOAD_OPERATION_ID where f.OPERATION_ID=op and r.SOURCE_LOAD_OPERATION_ID=:old.LOAD_OPERATION_ID and r.ROOT_UID=:old.ROOT_UID and :new.CUSTODY_RELEASED_AT=u.CREATED_AT;"
assert needle in s
s=s.replace(needle,"""join RRL_INTERWARE_UNLOAD u on u.OPERATION_ID=r.UNLOAD_OPERATION_ID
 left join RRL_INTERWARE_SHORTAGE_FACT loss on loss.RECEIPT_OPERATION_ID=r.OPERATION_ID
 left join RRL_STOCK_OPERATION confirmed on confirmed.OPERATION_ID=loss.OPERATION_ID
 where f.OPERATION_ID=op and r.SOURCE_LOAD_OPERATION_ID=:old.LOAD_OPERATION_ID
 and((r.ORIGINAL_ROOT_UID is null and r.ROOT_UID=:old.ROOT_UID and :new.CUSTODY_RELEASED_AT=u.CREATED_AT)
 or(r.ORIGINAL_ROOT_UID=:old.ROOT_UID and confirmed.STATE='APPLIED'and confirmed.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'
 and r.BASE_QTY+loss.SHORT_QTY=r.EXPECTED_BASE_QTY and :new.CUSTODY_RELEASED_AT=loss.CREATED_AT));""",1)
out[(d/"004_load_guard.sql").as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.sql");s=p.read_text(encoding="utf-8")
s=s.replace(" r.ROOT_UID RECEIVED_PALLET_IDENTIFIER,",""" r.ROOT_UID RECEIVED_PALLET_IDENTIFIER,
 loss.OPERATION_ID SHORTAGE_CONFIRMATION_OPERATION_ID,
 RRL_STOCK_PLAN_HELPER.decimal_text(nvl(loss.SHORT_QTY,0))CONFIRMED_SHORT_QUANTITY,
 case when confirmed.STATE='APPLIED'and confirmed.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'and r.BASE_QTY+loss.SHORT_QTY=r.EXPECTED_BASE_QTY then 1 else 0 end SHORTAGE_RESOLVED,
 json_value(l.COMPOSITION_JSON,'$.nodes[0].quantity')LOADED_QUANTITY,l.ROOT_UID LOADED_PALLET_IDENTIFIER,""",1)
s=s.replace("left join RRL_INTERWARE_PLACEMENT placement", """left join RRL_INTERWARE_SHORTAGE_FACT loss on loss.RECEIPT_OPERATION_ID=r.OPERATION_ID
left join RRL_STOCK_OPERATION confirmed on confirmed.OPERATION_ID=loss.OPERATION_ID
left join RRL_INTERWARE_PLACEMENT placement""",1);out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/domain/interwarehouse_readiness.py");s=p.read_text(encoding="utf-8")
s=s.replace('        row["ready"] = row["physically_loaded"] and row["temperature_decision"]!="HOLD" and row.get("receipt_complete",1)==1','''        accounted=row.get("receipt_complete",1)==1 or row.get("shortage_resolved",0)==1
        if "loaded_quantity"in row:
            row["physically_loaded"]=row["physically_loaded"] and row.get("loaded_pallet_identifier")==row.get("received_pallet_identifier") and row.get("loaded_quantity") is not None and row.get("received_quantity") is not None and Decimal(row["loaded_quantity"])==Decimal(row["received_quantity"])
        row["quantity_to_load"]=row.get("received_quantity")if accounted else None
        row["incoming_accounted"]=accounted
        row["ready"] = row["physically_loaded"] and row["temperature_decision"]!="HOLD" and accounted''',1)
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py");s=p.read_text(encoding="utf-8")
s=s.replace('if plan.get("receipt_complete",1)!=1:','if plan.get("receipt_complete",1)!=1 and plan.get("shortage_resolved",0)!=1:',1)
# Preserve distinction: warehouse physical full vs accepted fragment accounted; aggregate only readiness of actual accepted quantity.
s=s.replace('plan["warehouse_placement_completed"]=ready','plan["warehouse_placement_completed"]=ready and plan.get("receipt_complete",1)==1\n        plan["incoming_accounted_placement_completed"]=ready',1)
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
