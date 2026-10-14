exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-12_ni061_nested_custody");out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,kind in[("RRL_STOCK_INTERWARE_CUSTODY","PACKAGE BODY"),("RRL_TT_HU_LOAD_FACT_GUARD","TRIGGER")]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=name,kind=kind)
  body="\n".join(line.rstrip()for line in "".join(r[0]for r in q).replace(chr(13)," ").splitlines()).strip()
  out[(d/("000_before_"+name.lower()+".sql")).as_posix()]="create or replace "+body+"\n/\n"
before=out[(d/"000_before_rrl_stock_interware_custody.sql").as_posix()]
after=before.replace("loss_at timestamp with time zone;","loss_at timestamp with time zone;physical_uid varchar2(200);source_plan RRL_INTERWARE_PLAN%rowtype;",1)
after=after.replace("source_uid:=nvl(receipt.ORIGINAL_ROOT_UID,receipt.ROOT_UID);","source_uid:=nvl(receipt.ORIGINAL_ROOT_UID,receipt.ROOT_UID);\n select *into source_plan from RRL_INTERWARE_PLAN where OPERATION_ID=receipt.PLAN_OPERATION_ID;physical_uid:=nvl(source_plan.SOURCE_PLACE_UID,source_uid);",1)
after=after.replace("cargo.ROOT_UID!=source_uid","cargo.ROOT_UID!=physical_uid",1)
after=after.replace("p_domain.put('uid',source_uid)","p_domain.put('uid',physical_uid);p_domain.put('stock_pallet_identifier',source_uid)",1)
out[(d/"001_custody.sql").as_posix()]=after
before=out[(d/"000_before_rrl_tt_hu_load_fact_guard.sql").as_posix()]
assert "r.ROOT_UID=:old.ROOT_UID"in before
after=before.replace("r.ROOT_UID=:old.ROOT_UID","nvl((select p.SOURCE_PLACE_UID from RRL_INTERWARE_PLAN p where p.OPERATION_ID=r.PLAN_OPERATION_ID),r.ROOT_UID)=:old.ROOT_UID",1)
out[(d/"002_load_guard.sql").as_posix()]=after
out[(d/"003_ledger.sql").as_posix()]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-318-nested-custody-place' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Custody release uses actual frozen physical top HU independently of stock leaf while preserving original quantity and departure proofs',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
"""
out[(d/"apply.sql").as_posix()]="@@001_custody.sql\n@@002_load_guard.sql\n@@003_ledger.sql\n"
out[(d/"rollback.sql").as_posix()]="@@000_before_rrl_stock_interware_custody.sql\n@@000_before_rrl_tt_hu_load_fact_guard.sql\n"
print(json.dumps(out))
