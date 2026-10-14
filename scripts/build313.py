exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
folder=Path("db/migrations/2026-10-12_ni061_nested_binding_scope");out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_SHIP_CMD'and TYPE='PACKAGE BODY'order by LINE")
 before="create or replace "+"".join(r[0]for r in q).replace(chr(13)," ").strip()+"\n/\n"
s=before.replace("loading_domain json_object_t;","loading_domain json_object_t;v_warehouse number;v_source_cell varchar2(60);",1)
s=s.replace("snap:=json_object_t.parse(s);","snap:=json_object_t.parse(s);v_warehouse:=snap.get_number('warehouse');v_source_cell:=snap.get_string('cell');",1)
s=s.replace("select ST_ID from RRL_INTERWARE_ONWARD_BIND where ROOT_UID in(","select b.ST_ID from RRL_INTERWARE_ONWARD_BIND b where b.WARE_ID=v_warehouse and b.SOURCE_CELL=v_source_cell and not exists(select 1 from RRL_INTERWARE_ONWARD_DISPATCH dispatched where dispatched.BIND_OPERATION_ID=b.OPERATION_ID)and b.ROOT_UID in(",1)
s=s.replace("select ST_ID from RRL_IW_RECOVERY_ST_BIND where ROOT_UID in(","select b.ST_ID from RRL_IW_RECOVERY_ST_BIND b where b.WARE_ID=v_warehouse and b.SOURCE_CELL=v_source_cell and not exists(select 1 from RRL_IW_RECOVERY_DISPATCH dispatched where dispatched.BIND_OPERATION_ID=b.OPERATION_ID)and b.ROOT_UID in(",1)
put=lambda n,s:out.__setitem__((folder/n).as_posix(),s)
put("000_before.sql",before);put("001_scoped_binding.sql",s)
put("002_indexes.sql","""declare n number;begin
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_ONWARD_HU_SOURCE_IX';
 if n=0 then execute immediate 'create index RRL_IW_ONWARD_HU_SOURCE_IX on RRL_INTERWARE_ONWARD_BIND(WARE_ID,ROOT_UID,SOURCE_CELL,ST_ID)';end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_REC_HU_SOURCE_IX';
 if n=0 then execute immediate 'create index RRL_IW_REC_HU_SOURCE_IX on RRL_IW_RECOVERY_ST_BIND(WARE_ID,ROOT_UID,SOURCE_CELL,ST_ID)';end if;
 dbms_stats.gather_table_stats(user,'RRL_INTERWARE_ONWARD_BIND',cascade=>true);
 dbms_stats.gather_table_stats(user,'RRL_IW_RECOVERY_ST_BIND',cascade=>true);
end;
/
""")
put("003_ledger.sql","""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-313-nested-binding-scope' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Nested HU onward lookup uses current warehouse and cell, excludes applied historical bindings, and uses bounded source indexes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
""")
put("apply.sql","@@001_scoped_binding.sql\n@@002_indexes.sql\n@@003_ledger.sql\n");put("rollback.sql","@@000_before.sql\ndrop index RRL_IW_ONWARD_HU_SOURCE_IX;\ndrop index RRL_IW_REC_HU_SOURCE_IX;\n")
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_STOCK_HU_SHIP_CMD';\nselect INDEX_NAME,STATUS from USER_INDEXES where INDEX_NAME in('RRL_IW_ONWARD_HU_SOURCE_IX','RRL_IW_REC_HU_SOURCE_IX');\n")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));put("000_before_manifest.json",p.read_text(encoding="utf-8"))
m["additional_scripts"].append("../2026-10-12_ni061_nested_binding_scope/001_scoped_binding.sql");m["startup_scripts"].append("../2026-10-12_ni061_nested_binding_scope/002_indexes.sql");out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out))
