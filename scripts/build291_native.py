from pathlib import Path
import json
out={};base=Path("db/migrations/2026-10-11_ni061_partial_receiving")
p=base/"001_schema.sql";s=p.read_text(encoding="utf-8").replace("EXPECTED_BASE_QTY>BASE_QTY","EXPECTED_BASE_QTY is not null and EXPECTED_BASE_QTY>BASE_QTY");out[p.as_posix()]=s
s=(base/"000_before_rrl_stock_interware_rec_body.sql").read_text(encoding="utf-8")
needle=" if v_kind='INTERWARE_UNLOAD' then"
assert s.count(needle)==2
s=s.replace(needle,""" if m.get_boolean('partial_receipt')then
  if v_kind!='INTERWARE_RECEIVE'then raise_application_error(-20886,'INTERWARE_PARTIAL_RECEIPT_ONLY');end if;
  RRL_STOCK_INTERWARE_PART.describe_partial(m,plan.ROOT_UID,v_qty,v_uom,lot.ARTICUL,p_domain);
  v_qty:=RRL_STOCK_MATH.quantity(p_domain.get_string('quantity'));
 end if;
"""+needle,1)
needle=" if v.has('source_units')then"
first=s.index(needle)
extra="""
 if v.has('partial_receipt')then
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',v.get_string('uid'));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('original_root_uid'),v.get_string('article'),null,null);
  RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',v.get_string('source_origin_uid'));
 end if;
"""
s=s[:first]+extra+s[first:]
needle="  RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,v_qty,0,v_uom,v_ver,0);"
assert needle in s;s=s.replace(needle,"  if v.has('partial_receipt')then RRL_STOCK_INTERWARE_PART.create_pallet(v,op);end if;\n"+needle,1)
s=s.replace("SOURCE_LOAD_OPERATION_ID,STOCK_EVENT_ID,ACTOR)","SOURCE_LOAD_OPERATION_ID,STOCK_EVENT_ID,ACTOR,ORIGINAL_ROOT_UID,EXPECTED_BASE_QTY,DISCREPANCY_REASON,DISCREPANCY_REFERENCE)")
s=s.replace("v_source,v_event,p_actor);","v_source,v_event,p_actor,v.get_string('original_root_uid'),v.get_number('expected_quantity'),v.get_string('discrepancy_reason'),v.get_string('discrepancy_reference'));")
needle="  v_payload:=j.to_clob;"
assert needle in s;s=s.replace(needle,"""  if v.has('partial_receipt')then
   j.put('status','RECEIVED_PARTIAL_PENDING_PLACEMENT');j.put('original_pallet_identifier',v.get_string('original_root_uid'));
   j.put('expected_quantity',v.get_string('expected_quantity'));j.put('short_quantity',v.get_string('short_quantity'));
   j.put('carrier_shortage_resolved',false);j.put('discrepancy_reason',v.get_string('discrepancy_reason'));j.put('discrepancy_reference',v.get_string('discrepancy_reference'));
  end if;
"""+needle,1)
out[(base/"003_receiving_body.sql").as_posix()]=s
s=(base/"000_before_rrl_stock_interware_put_body.sql").read_text(encoding="utf-8")
needle=" select GROSS_WEIGHT_KG into v_gross from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=receipt.SOURCE_LOAD_OPERATION_ID;"
assert needle in s;s=s.replace(needle,""" if receipt.ORIGINAL_ROOT_UID is not null then
  select WEIGHT_BRUTTO into v_gross from RRL_PALLETS where UID_PALLET=receipt.ROOT_UID;
 else
"""+needle+"\n end if;",1)
out[(base/"004_put_body.sql").as_posix()]=s
s=(base/"000_before_rrl_stock_interware_custody_body.sql").read_text(encoding="utf-8")
needle=" select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=p_receipt;"
assert needle in s;s=s.replace(needle,needle+"\n if receipt.ORIGINAL_ROOT_UID is not null then raise_application_error(-20886,'INTERWARE_UNRESOLVED_PARTIAL_CARRIER_CUSTODY');end if;\n",1)
out[(base/"005_custody_body.sql").as_posix()]=s
s=(base/"000_before_rrl_interware_depart_gate_body.sql").read_text(encoding="utf-8")
needle="where r.PLAN_OPERATION_ID=p.OPERATION_ID and l.TT_ID=p_trip"
assert needle in s;s=s.replace(needle,"where (r.EXPECTED_BASE_QTY is null or r.BASE_QTY=r.EXPECTED_BASE_QTY)and r.PLAN_OPERATION_ID=p.OPERATION_ID and l.TT_ID=p_trip",1)
out[(base/"006_depart_gate.sql").as_posix()]=s
# Captured DBMS trigger includes ALTER ENABLE; normalize the separator.
s=(base/"000_before_rrl_sap_pallet_write_guard.sql").read_text(encoding="utf-8")
pos=s.index('ALTER TRIGGER');s=s[:pos].strip()+"\n/\n"
needle="   if allowed_clone=1 then"
assert needle in s
s=s.replace(needle,"""   if allowed_clone=0 then
    select count(*)into allowed_clone from RRL_STOCK_OPERATION operation
     join json_table(operation.RESOLVED_PLAN_JSON,'$.domain'columns(
       PARTIAL_FLAG varchar2(5)path '$.partial_receipt',SOURCE_UID varchar2(150)path '$.original_root_uid',TARGET_UID varchar2(150)path '$.uid',
       QUANTITY_TEXT varchar2(60)path '$.quantity',ORIGIN_UID varchar2(150)path '$.source_origin_uid',NAKLAD_ID number path '$.source_naklad_id'))d
      on d.TARGET_UID=:new.UID_PALLET
     join RRL_PALLETS source_lot on source_lot.UID_PALLET=d.SOURCE_UID
     where operation.OPERATION_ID=op and operation.STATE='IN_FLIGHT'and operation.COMMAND_TYPE='INTERWARE_RECEIVE'
      and d.PARTIAL_FLAG='true'and d.ORIGIN_UID=:new.STOCK_ORIGIN_UID
      and nvl(source_lot.STOCK_ORIGIN_UID,source_lot.UID_PALLET)=d.ORIGIN_UID
      and source_lot.PRIHOD_NAKLAD_ID=:new.PRIHOD_NAKLAD_ID and d.NAKLAD_ID=:new.PRIHOD_NAKLAD_ID
      and d.QUANTITY_TEXT=RRL_STOCK_PLAN_HELPER.decimal_text(:new.UNIT_COUNT);
   end if;
"""+needle,1)
out[(base/"007_sap_clone_guard.sql").as_posix()]=s
out[(base/"008_recompile.sql").as_posix()]="alter package RRL_STOCK_INTERWARE_REC compile body;\nalter package RRL_STOCK_INTERWARE_PUT compile body;\nalter package RRL_STOCK_INTERWARE_CUSTODY compile body;\nalter package RRL_INTERWARE_DEPART_GATE compile body;\nalter trigger RRL_INTERWARE_RECEIPT_GUARD compile;\nalter trigger RRL_INTERWARE_PUT_GUARD compile;\nalter trigger RRL_INTERWARE_PLACEMENT_GUARD compile;\nalter trigger RRL_INTERWARE_ONWARD_BIND_GUARD compile;\nalter package RRL_STOCK_INTERWARE_NEXT compile body;\nalter package RRL_INTERWARE_ROUTING compile body;\nalter package RRL_INTERWARE_UNIT_SOURCE compile body;\nalter trigger RRL_TT_HU_LOAD_FACT_GUARD compile;\n"
print(json.dumps(out,ensure_ascii=True))
