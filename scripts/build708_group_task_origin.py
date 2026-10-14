exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
import hashlib
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_TASK'and TYPE='PACKAGE BODY'order by LINE");before="create or replace "+"".join(x[0]for x in q)+"/\n"
anchor="  src.put('uid',t.UID_PALLET);"
assert before.count(anchor)==1
addition="""  declare v_group_receipt varchar2(100);begin
   select max(RECEIPT_OPERATION_ID)into v_group_receipt from RRL_IW_GROUP_PUT_PLAN where TASK_ID=t.TASK_ID;
   if v_group_receipt is not null then m.put('group_receipt_operation_id',v_group_receipt);
   else m.remove('group_receipt_operation_id');end if;
  end;
"""
after=before.replace(anchor,addition+anchor)
d="db/migrations/2026-10-12_ni061_group_task_origin"
out={d+"/000_before.sql":before,d+"/001_task.sql":after,d+"/apply.sql":"@@001_task.sql\n@@002_ledger.sql\n",d+"/rollback.sql":"@@000_before.sql\n",d+"/002_ledger.sql":"""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-708-group-task-origin'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing HU task reconstructs grouped receipt origin from its immutable plan, not operator input',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",d+"/checkpoint.json":json.dumps({"schema":"RABAEV","before_sha256":hashlib.sha256(before.encode()).hexdigest(),"recovery":"captured package body restore; no quantity rewrite"},indent=2),d+"/verify.sql":"select *from USER_ERRORS where NAME='RRL_STOCK_HU_TASK';\n"}
print(json.dumps(out))
