import json
from pathlib import Path
p=Path("db/migrations/2026-10-12_ni043_aggregation_lifecycle/001_lifecycle.sql");s=p.read_text(encoding="utf-8")
s=s.replace("blocked_wire clob;blocked json_array_t;","blocked_wire clob;members_wire clob;expected_members number;blocked json_array_t;")
old="""select count(*)into n from RRL_WMS_RECEIPT_UNIT u where u.UID_PALLET=v_origin and u.STOCK_STATUS in('AVAILABLE','RESERVED')
 and exists(select 1 from RRL_CELLS c where c.CELL=u.CURRENT_CELL and c.WARE_ID=v_ware);
 if n=0 then raise_application_error(-20886,'TRACE_AGG_LOCAL_CUSTODY_REQUIRED');end if;"""
new="""begin
 select a.UNITS_JSON into members_wire from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE u on u.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 where u.UID_PALLET=v_origin and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile and a.CODE_HASH=v_hash;
 exception when no_data_found then
 select a.UNITS_JSON into members_wire from RRL_SAP_TRACE_AGG a join RRL_SAP_PALLET_RECEIPT r on r.ORDER_ID=a.ORDER_ID and r.LINE_NUMBER=a.LINE_NUMBER
 where r.UID_PALLET=v_origin and r.POSTED_BASE_QTY>0 and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile and a.CODE_HASH=v_hash;
 end;
 expected_members:=json_array_t.parse(members_wire).get_size;
 if expected_members<1 or expected_members>10000 then raise_application_error(-20881,'TRACE_AGG_MEMBER_BOUND');end if;
 select count(*)into n from json_table(members_wire,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id'))j
 join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=v_origin and u.UNIT_ID=j.UNIT_ID
 join RRL_CELLS c on c.CELL=u.CURRENT_CELL and c.WARE_ID=v_ware
 where u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null;
 if n!=expected_members then raise_application_error(-20886,'TRACE_AGG_ALL_FREE_MEMBERS_LOCAL_CUSTODY_REQUIRED');end if;"""
assert s.count(old)==1;s=s.replace(old,new)
p2=Path("db/migrations/2026-10-12_ni043_aggregation_lifecycle/002_scan_guard.sql")
scan=p2.read_text(encoding="utf-8")
old2="where u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null"
assert scan.count(old2)==1
scan=scan.replace(old2,"where u.STOCK_STATUS='ISSUED'and u.CURRENT_UID=v_origin_uid and u.HARD_RESERVATION_ID is null")
print(json.dumps({str(p):s,str(p2):scan}))
