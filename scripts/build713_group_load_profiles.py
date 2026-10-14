exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import hashlib
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_SHIP_CMD'and TYPE='PACKAGE BODY'order by LINE");before="create or replace "+"".join(x[0]for x in q)+"/\n"
old="if leg_count>0 then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_UNIT_SCAN_MODE_REQUIRED');end if;"
new="if leg_count>0 and not subdomain.get_object('interwarehouse_onward_source').has('group_receipt_operation_id') then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_UNIT_SCAN_MODE_REQUIRED');end if;"
assert before.count(old)==1
d="db/migrations/2026-10-12_ni061_group_load_profiles"
out={d+"/000_before.sql":before,d+"/001_ship.sql":before.replace(old,new),d+"/apply.sql":"@@001_ship.sql\n@@002_ledger.sql\n",d+"/rollback.sql":"@@000_before.sql\n",d+"/002_ledger.sql":"""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-713-group-load-profiles'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Original whole grouped receipt continuation preserves mixed capture profiles; shared source/unit/QC/load guards retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",d+"/checkpoint.json":json.dumps({"schema":"RABAEV","before_sha256":hashlib.sha256(before.encode()).hexdigest(),"authoritative_rule":"RRL_IW_GROUP_NEXT exact original units/stock and QC/load; receipt capture mode is not unit control mode","recovery":"restore captured body; no stock rewrite"},indent=2),d+"/verify.sql":"select *from USER_ERRORS where NAME='RRL_STOCK_HU_SHIP_CMD';\n"}
print(json.dumps(out))
