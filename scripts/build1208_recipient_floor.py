import json
from pathlib import Path
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
folder="db/migrations/2026-10-14_ni022_recipient_floor/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=5000;q=c.cursor()
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_PLAN_RULES' and TYPE='PACKAGE BODY' order by LINE")
 original="create or replace "+"".join(r[0] for r in q)+"\n/\n"
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_CUSTOMER_PALLET_TYPE_RULE'")
 columns={r[0] for r in q}
 assert {"CUSTOMER_ID","CUSTOMER_STORE_MAP_ID","PALLET_TYPE_ID","IS_DEFAULT","ACTIVE","VALID_FROM","VALID_TO","CUSTOMER_PALLET_TYPE_RULE_ID"}<=columns,columns
body=original.replace("case_count number;type_count number;type_id number;active_value number;","case_count number;type_count number;type_id number;active_value number;planned_count number;planned_type number;planned_active number;")
old="p.PALLET_UID,count(distinct c.CASE_PICK_TASK_ID),count(distinct c.PALLET_TYPE_ID),min(c.PALLET_TYPE_ID),min(t.ACTIVE) from RRL_SBORKA_PALLETS p"
new="p.PALLET_UID,count(distinct c.CASE_PICK_TASK_ID),count(distinct c.PALLET_TYPE_ID),min(c.PALLET_TYPE_ID),min(t.ACTIVE),count(distinct rt.PALLET_TYPE_ID),min(rt.PALLET_TYPE_ID),min(pt.ACTIVE) from RRL_SBORKA_PALLETS p"
assert old in body;body=body.replace(old,new,1)
old="left join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=c.PALLET_TYPE_ID where p.ST_NUMBER in ("
new="""left join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=c.PALLET_TYPE_ID left join RRL_CUSTOMER_ORDER_FULFILLMENT ff on ff.LEGACY_SBORKA_PALLET_ID=p.ID left join RRL_CUSTOMER_ORDER co on co.CUSTOMER_ORDER_ID=ff.CUSTOMER_ORDER_ID left join RRL_CUSTOMER_PALLET_TYPE_RULE rt on rt.CUSTOMER_PALLET_TYPE_RULE_ID=(select rr.CUSTOMER_PALLET_TYPE_RULE_ID from RRL_CUSTOMER_PALLET_TYPE_RULE rr where rr.CUSTOMER_ID=co.CUSTOMER_ID and (rr.CUSTOMER_STORE_MAP_ID=co.CUSTOMER_STORE_MAP_ID or (rr.CUSTOMER_STORE_MAP_ID is null and rr.CUSTOMER_ADDRESS_ID is null)) and rr.ACTIVE=1 and trunc(sysdate) between rr.VALID_FROM and nvl(rr.VALID_TO,date ''2999-12-31'') order by case when rr.CUSTOMER_STORE_MAP_ID=co.CUSTOMER_STORE_MAP_ID then 0 else 1 end,rr.IS_DEFAULT desc,rr.CUSTOMER_PALLET_TYPE_RULE_ID fetch first 1 row only) left join RRL_PALLET_TYPE pt on pt.PALLET_TYPE_ID=rt.PALLET_TYPE_ID where p.ST_NUMBER in ("""
assert old in body;body=body.replace(old,new,1)
old="fetch rows_cursor into uid_value,case_count,type_count,type_id,active_value;"
assert old in body;body=body.replace(old,"fetch rows_cursor into uid_value,case_count,type_count,type_id,active_value,planned_count,planned_type,planned_active;",1)
old="if case_count=1 and type_count=1 and active_value=1 then"
assert old in body;body=body.replace(old,"if case_count=0 and planned_count=1 and planned_active=1 then type_id:=planned_type;type_count:=1;active_value:=1;case_count:=1;end if;\n   "+old,1)
body=body.replace("PLAN_TARE_BOUND1186","PLAN_TARE_RECIPIENT1208",1)
print(json.dumps({folder+"000_before_body.sql":original,folder+"001_plan_rule.sql":body,folder+"apply.sql":"@@001_plan_rule.sql\n",folder+"rollback.sql":"@@000_before_body.sql\n"},ensure_ascii=True))
