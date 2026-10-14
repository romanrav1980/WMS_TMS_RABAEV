exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};folder=Path("db/migrations/2026-10-12_ni061_flexible_unit_mode")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_INTERWARE_MARK_SCAN'and TYPE='PACKAGE BODY'order by LINE")
 before="create or replace "+"".join(r[0]for r in q).replace(chr(13)," ").strip()+"\n/\n"
 assert before.count("SCAN_MODE!='UNIT'")==1
 after=before.replace("SCAN_MODE!='UNIT'","SCAN_MODE not in('UNIT','UNIT_OR_AGGREGATION')").replace("INTERWARE_UNIT_SCAN_MODE_REQUIRED","INTERWARE_UNIT_CAPTURE_FORBIDDEN_BY_PROFILE")
out[(folder/"000_before.sql").as_posix()]=before
out[(folder/"001_scan.sql").as_posix()]=after
ledger="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-309-flexible-unit-mode' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing interwarehouse unique-unit capture accepts UNIT_OR_AGGREGATION; BOX and PALLET still require composition evidence',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
"""
out[(folder/"002_ledger.sql").as_posix()]=ledger
out[(folder/"apply.sql").as_posix()]="@@001_scan.sql\n@@002_ledger.sql\n"
out[(folder/"rollback.sql").as_posix()]="@@000_before.sql\n"
out[(folder/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_INTERWARE_MARK_SCAN';\nselect STATUS from USER_OBJECTS where OBJECT_NAME='RRL_INTERWARE_MARK_SCAN';\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");manifest=json.loads(p.read_text(encoding="utf-8"))
out[(folder/"000_before_manifest.json").as_posix()]=p.read_text(encoding="utf-8")
old="../2026-10-11_ni061_marked_partial/004_mark_scan.sql"
assert old in manifest["additional_scripts"]
manifest["additional_scripts"][manifest["additional_scripts"].index(old)]="../2026-10-12_ni061_flexible_unit_mode/001_scan.sql"
out[p.as_posix()]=json.dumps(manifest,indent=2)+"\n"
print(json.dumps(out))

