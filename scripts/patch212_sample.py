from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_unload");s=(f/"000_before_sample_guard.sql").read_text(encoding="utf-8")
anchor=" if v_kind!='OUTGOING_PALLET_CHECK'";assert anchor in s
s=s.replace(anchor,""" if v_kind='UNLOAD_SHIPMENT'then
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(:new.ID)));
  declare wire clob;state_name varchar2(20);sid number;begin
   select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
   sid:=json_object_t.parse(wire).get_object('domain').get_number('shipment_id');
   if state_name!='IN_FLIGHT'or sid!=:new.ID or nvl(:new.QC_SAMPLE_BUCKET,-1)!=nvl(:old.QC_SAMPLE_BUCKET,-1)or nvl(:new.QC_SAMPLE_REQUIRED,0)!=nvl(:old.QC_SAMPLE_REQUIRED,0)or :new.QC_RESCAN_REQUIRED!=1 then raise_application_error(-20863,'UNLOAD_RESCAN_ONLY_REQUIRED');end if;
  end;return;
 end if;
"""+anchor)
print(json.dumps({str(f/"010_sample_guard.sql"):s},ensure_ascii=True))
