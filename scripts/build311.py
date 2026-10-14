exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};folder=Path("db/migrations/2026-10-12_ni061_sap_aggregation_scan")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_IW_AGG_SCAN'and TYPE='PACKAGE BODY'order by LINE")
 before="create or replace "+"".join(r[0]for r in q).replace(chr(13)," ").strip()+"\n/\n"
a=before.index(" if n!=1 then raise_application_error(-20886,'INTERWARE_APPLIED_SENDER_AGGREGATION_REQUIRED');end if;")
b=before.index(" select count(*)into n from RRL_SKU_RECEIPT_PROFILE",a)
replacement=""" if n>1 then raise_application_error(-20886,'INTERWARE_AGGREGATION_ORIGIN_AMBIGUOUS');end if;
 if n=1 then
 select a.UNITS_JSON,a.PROFILE_VERSION into members,aggregate_version from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE used on used.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 where used.UID_PALLET=v_origin_uid and a.SYSTEM_CODE=v_system_code and a.PROFILE_CODE=v_profile_code and a.CODE_HASH=v_digest and a.AGG_LEVEL=v_level_code;
 else
 select count(*)into n from RRL_SAP_TRACE_AGG a join RRL_SAP_PALLET_RECEIPT rec on rec.ORDER_ID=a.ORDER_ID and rec.LINE_NUMBER=a.LINE_NUMBER
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=rec.STOCK_OPERATION_ID and op.STATE='APPLIED'and op.COMMAND_TYPE='SAP_RECEIPT'
 where rec.UID_PALLET=v_origin_uid and rec.POSTED_BASE_QTY>0 and a.SYSTEM_CODE=v_system_code and a.PROFILE_CODE=v_profile_code and a.CODE_HASH=v_digest and a.AGG_LEVEL=v_level_code;
 if n!=1 then raise_application_error(-20886,'INTERWARE_APPLIED_AGGREGATION_BIRTH_SOURCE_REQUIRED');end if;
 select a.UNITS_JSON into members from RRL_SAP_TRACE_AGG a join RRL_SAP_PALLET_RECEIPT rec on rec.ORDER_ID=a.ORDER_ID and rec.LINE_NUMBER=a.LINE_NUMBER
 where rec.UID_PALLET=v_origin_uid and a.SYSTEM_CODE=v_system_code and a.PROFILE_CODE=v_profile_code and a.CODE_HASH=v_digest and a.AGG_LEVEL=v_level_code;
 aggregate_version:=null;
 end if;
"""
after=before[:a]+replacement+before[b:]
after=after.replace("if current_version!=aggregate_version or scan_mode not in", "if current_version is null or(aggregate_version is not null and current_version!=aggregate_version)or scan_mode not in")
after=after.replace("C varchar2(4000)path '$.raw_code'","C varchar2(4000)path '$.raw_code',V varchar2(40)path '$.version'")
after=after.replace("proof.P=v_profile_code and proof.C=j.RAW_CODE","proof.P=v_profile_code and proof.C=j.RAW_CODE and proof.V=current_version")
put=lambda n,s:out.__setitem__((folder/n).as_posix(),s)
put("000_before.sql",before);put("001_aggregation.sql",after)
put("002_ledger.sql","""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-311-sap-interware-aggregation' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Interwarehouse aggregation proof resolves exact applied SAP receipt order and line; current code-profile versions and original physical registry retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
""")
put("apply.sql","@@001_aggregation.sql\n@@002_ledger.sql\n");put("rollback.sql","@@000_before.sql\n")
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_IW_AGG_SCAN';\n")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));put("000_before_manifest.json",p.read_text(encoding="utf-8"))
m["additional_scripts"].append("../2026-10-12_ni061_sap_aggregation_scan/001_aggregation.sql");out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out))
