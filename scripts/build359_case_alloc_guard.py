exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};d=Path("db/migrations/2026-10-12_ni071_case_allocation")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_LOG_EXP_ALLOC_LINE_GUARD'and TYPE='TRIGGER'order by LINE");old="create or replace "+"".join(x[0]for x in q).replace("\r","").strip()+"\n/\n"
out[(d/"000_before_guard.sql").as_posix()]=old
new=old.replace(" where a.OPERATION_ID=:new.OPERATION_ID and a.CURRENCY=:new.CURRENCY;",""" join RRL_STOCK_OPERATION stock_op on stock_op.OPERATION_ID=l.LOAD_OPERATION_ID and stock_op.STATE='APPLIED'
 join json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(K varchar2(20)path '$.kind',U varchar2(200)path '$.uid',A varchar2(160)path '$.article',Q number path '$.quantity',B varchar2(20)path '$.base_uom'))leaf on leaf.K='STOCK'and leaf.U=:new.UID_PALLET and leaf.A=:new.ARTICLE and leaf.Q=:new.BASE_QTY and leaf.B=:new.BASE_UOM
 where a.OPERATION_ID=:new.OPERATION_ID and a.CURRENCY=:new.CURRENCY;""",1)
assert new!=old
marker=" if n!=1 then raise_application_error(-20886,'LOGISTICS_ALLOCATION_EXACT_LOAD_SOURCE_REQUIRED');end if;"
assert marker in new
new=new.replace(marker,marker+"""
 if :new.WEIGHT_SOURCE='MEASURED_CASE_NET'then
  select count(*)into n from RRL_TT_HU_LOAD_FACT l join RRL_TT_LOAD_BOX_WEIGHT b on b.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID and b.BOX_UID=:new.WEIGHT_BOX_UID
  join json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(K varchar2(20)path '$.kind',U varchar2(200)path '$.uid',CID number path '$.case_task_id',V number path '$.version',CAP varchar2(100)path '$.scale_qc.capture_key',QC varchar2(100)path '$.scale_qc.qc_operation_id',MV number path '$.scale_qc.measured_content_version',SIG number path '$.scale_qc.signature_version',NET number path '$.scale_qc.net_weight_kg',GROSS number path '$.scale_qc.gross_weight_kg',TARE number path '$.scale_qc.tare_weight_kg'))box on box.K='CASE'and box.U=b.BOX_UID and box.CID=b.CASE_BOX_TASK_ID and box.V=b.BOX_CONTENT_VERSION
  where l.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and b.MEASUREMENT_ORIGIN='WAREHOUSE_SCALE_QC'and b.COVERAGE_COMPLETE=1
   and b.FINAL_SCALE_CAPTURE=box.CAP and b.WAREHOUSE_QC_OPERATION=box.QC and b.SIGNATURE_VERSION=box.SIG and b.MEASURED_CONTENT_VERSION=box.MV
   and b.NET_WEIGHT_KG=box.NET and b.GROSS_WEIGHT_KG=box.GROSS and b.TARE_WEIGHT_KG=box.TARE and box.NET=:new.WEIGHT_KG and :new.BASIS_VALUE=:new.WEIGHT_KG
   and(select count(*)from json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(K varchar2(20)path '$.kind',CID number path '$.case_task_id'))child where child.K='STOCK'and child.CID=b.CASE_BOX_TASK_ID)=1
   and exists(select 1 from json_table(l.COMPOSITION_JSON,'$.links[*]'columns(P varchar2(200)path '$.parent',C varchar2(200)path '$.child',M varchar2(40)path '$.membership'))membership where membership.P=b.BOX_UID and membership.C=:new.UID_PALLET and membership.M='CASE_CARRIER_LOT');
  if n!=1 then raise_application_error(-20886,'LOGISTICS_ALLOCATION_EXACT_CASE_NET_REQUIRED');end if;
 end if;
""",1)
out[(d/"001_guard.sql").as_posix()]=new
out[(d/"002_ledger.sql").as_posix()]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-359-case-finance-source' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing expense allocation binds exact archived stock source and measured smallCASE single-leaf net proof',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"
out[(d/"apply.sql").as_posix()]="@@001_guard.sql\n@@002_ledger.sql\n"
out[(d/"rollback.sql").as_posix()]="@@000_before_guard.sql\n"
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_LOG_EXP_ALLOC_LINE_GUARD';\n"
print(json.dumps(out))
