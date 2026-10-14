from pathlib import Path
import json
out={};d=Path("db/migrations/2026-10-11_ni061_partial_custody");base=Path("db/migrations/2026-10-11_ni061_shortage_disposition")
s=(base/"000_before_rrl_stock_interware_custody_package_body.sql").read_text(encoding="utf-8")
s=s.replace("cargo RRL_TT_HU_LOAD_FACT%rowtype;n number;","cargo RRL_TT_HU_LOAD_FACT%rowtype;n number;source_uid varchar2(200);loss_id varchar2(100);loss_at timestamp with time zone;")
s=s.replace(" if receipt.ORIGINAL_ROOT_UID is not null then raise_application_error(-20886,'INTERWARE_UNRESOLVED_PARTIAL_CARRIER_CUSTODY');end if;",""" source_uid:=nvl(receipt.ORIGINAL_ROOT_UID,receipt.ROOT_UID);
 if receipt.ORIGINAL_ROOT_UID is not null then
  select fact.OPERATION_ID,fact.CREATED_AT into loss_id,loss_at from RRL_INTERWARE_SHORTAGE_FACT fact
   join RRL_INTERWARE_SHORTAGE_REQUEST req on req.OPERATION_ID=fact.REQUEST_OPERATION_ID
   join RRL_STOCK_OPERATION o on o.OPERATION_ID=fact.OPERATION_ID and o.STATE='APPLIED'and o.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'
   where fact.RECEIPT_OPERATION_ID=receipt.OPERATION_ID and req.RECEIPT_OPERATION_ID=receipt.OPERATION_ID
   and req.SOURCE_LOAD_OPERATION_ID=receipt.SOURCE_LOAD_OPERATION_ID and req.ORIGINAL_UID=source_uid
   and req.ACCEPTED_UID=receipt.ROOT_UID and req.WARE_ID=receipt.WARE_ID
   and req.EXPECTED_QTY=receipt.EXPECTED_BASE_QTY and req.ACCEPTED_QTY=receipt.BASE_QTY
   and fact.SHORT_QTY=req.SHORT_QTY and receipt.BASE_QTY+fact.SHORT_QTY=receipt.EXPECTED_BASE_QTY;
 end if;""",1)
s=s.replace("cargo.ROOT_UID!=receipt.ROOT_UID or unloaded.ROOT_UID!=receipt.ROOT_UID","cargo.ROOT_UID!=source_uid or unloaded.ROOT_UID!=source_uid")
s=s.replace("p_domain.put('uid',receipt.ROOT_UID)","p_domain.put('uid',source_uid)")
s=s.replace("p_domain.put('custody_released_at',to_char(unloaded.CREATED_AT,","p_domain.put('custody_released_at',to_char(nvl(loss_at,unloaded.CREATED_AT),")
s=s.replace(" exception when no_data_found then raise_application_error(-20886,'INTERWARE_CUSTODY_ACTUAL_RECEIPT_REQUIRED');",""" if loss_id is not null then p_domain.put('shortage_confirmation_operation_id',loss_id);
 p_domain.put('accepted_pallet_identifier',receipt.ROOT_UID);p_domain.put('accepted_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(receipt.BASE_QTY));
 p_domain.put('confirmed_short_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(receipt.EXPECTED_BASE_QTY-receipt.BASE_QTY));p_domain.put('full_physical_receipt',false);end if;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_CUSTODY_ACTUAL_RECEIPT_OR_CONFIRMED_SHORTAGE_REQUIRED');""",1)
needle=" RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_CUSTODY_PROOF',p_operation);"
s=s.replace(needle,needle+"\n if v.has('shortage_confirmation_operation_id')then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_SHORTAGE_FACT',v.get_string('shortage_confirmation_operation_id'));end if;",1)
s=s.replace(" select CREATED_AT into released_at from RRL_INTERWARE_UNLOAD where OPERATION_ID=v_unload;",""" if v.has('shortage_confirmation_operation_id')then
 select CREATED_AT into released_at from RRL_INTERWARE_SHORTAGE_FACT where OPERATION_ID=v.get_string('shortage_confirmation_operation_id');
 else select CREATED_AT into released_at from RRL_INTERWARE_UNLOAD where OPERATION_ID=v_unload;end if;""",1)
# Avoid JSON object getter inside SQL.
s=s.replace("released_at timestamp with time zone;","released_at timestamp with time zone;v_loss varchar2(100);",1)
s=s.replace(" select CREATED_AT into released_at from RRL_INTERWARE_SHORTAGE_FACT where OPERATION_ID=v.get_string('shortage_confirmation_operation_id');"," v_loss:=v.get_string('shortage_confirmation_operation_id');select CREATED_AT into released_at from RRL_INTERWARE_SHORTAGE_FACT where OPERATION_ID=v_loss;")
s=s.replace(" j.put('status','FIRST_LEG_CUSTODY_RELEASED');",""" if v.has('shortage_confirmation_operation_id')then
 j.put('shortage_confirmation_operation_id',v.get_string('shortage_confirmation_operation_id'));j.put('full_physical_receipt',false);
 j.put('accepted_pallet_identifier',v.get_string('accepted_pallet_identifier'));j.put('accepted_quantity',v.get_string('accepted_quantity'));j.put('confirmed_short_quantity',v.get_string('confirmed_short_quantity'));end if;
 j.put('status','FIRST_LEG_CUSTODY_RELEASED');""",1)
out[(d/"001_custody_body.sql").as_posix()]=s
s=(base/"000_before_rrl_stock_interware_next_package_body.sql").read_text(encoding="utf-8")
s=s.replace("unit_snapshot clob;j json_object_t","unit_snapshot clob;receipt_wire clob;receipt_domain json_object_t;subset_wire json_object_t;j json_object_t",1)
needle="  select MANIFEST_JSON into unit_wire from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=receipt.PLAN_OPERATION_ID;"
assert needle in s
s=s.replace(needle,"""  if receipt.ORIGINAL_ROOT_UID is not null then
   select RESOLVED_PLAN_JSON into receipt_wire from RRL_STOCK_OPERATION where OPERATION_ID=receipt.OPERATION_ID and STATE='APPLIED'and COMMAND_TYPE='INTERWARE_RECEIVE';
   receipt_domain:=json_object_t.parse(receipt_wire).get_object('domain');subset_wire:=json_object_t();
   subset_wire.put('units',receipt_domain.get_array('source_units'));subset_wire.put('physical_unit_count',receipt_domain.get_array('source_units').get_size);unit_wire:=subset_wire.to_clob;
  else
"""+needle+"\n  end if;",1)
out[(d/"002_onward_body.sql").as_posix()]=s
s=(base/"000_before_rrl_interware_depart_gate_package_body.sql").read_text(encoding="utf-8")
needle="(r.EXPECTED_BASE_QTY is null or r.BASE_QTY=r.EXPECTED_BASE_QTY)"
assert needle in s
s=s.replace(needle,"""(r.EXPECTED_BASE_QTY is null or r.BASE_QTY=r.EXPECTED_BASE_QTY or exists(
 select 1 from RRL_INTERWARE_SHORTAGE_FACT fact join RRL_STOCK_OPERATION confirmed on confirmed.OPERATION_ID=fact.OPERATION_ID
 where fact.RECEIPT_OPERATION_ID=r.OPERATION_ID and confirmed.STATE='APPLIED'and confirmed.COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM'
 and fact.SHORT_QTY+r.BASE_QTY=r.EXPECTED_BASE_QTY))""",1)
# Explicit actual accepted cargo composition, not merely existence of any active load.
s=s.replace("and l.TT_ID=p_trip and l.STATUS='LOADED'","""and l.TT_ID=p_trip and l.STATUS='LOADED'and l.ROOT_UID=r.ROOT_UID
 and RRL_STOCK_MATH.quantity(json_value(l.COMPOSITION_JSON,'$.nodes[0].quantity'))=r.BASE_QTY""",1)
out[(d/"003_depart_gate.sql").as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
