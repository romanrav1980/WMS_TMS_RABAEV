exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};folder=Path("db/migrations/2026-10-12_ni061_aggregation_scan")
helper="""create or replace package RRL_IW_AGG_SCAN authid definer accessible by(package RRL_INTERWARE_MARK_SCAN)as
 procedure expand(p_metadata clob,p_scans out clob);
end;
/
create or replace package body RRL_IW_AGG_SCAN as
 procedure expand(p_metadata clob,p_scans out clob)is
 m json_object_t:=json_object_t.parse(p_metadata);direct_scans json_array_t:=json_array_t();aggregates json_array_t:=json_array_t();
 result_scans json_array_t:=json_array_t();item json_object_t;expanded json_array_t;members clob;expanded_wire clob;
 system_code varchar2(40);profile_code varchar2(80);digest varchar2(64);level_code varchar2(10);origin_uid varchar2(200);
 n number;expected_count number;current_count number;aggregate_version varchar2(40);current_version varchar2(40);scan_mode varchar2(40);
 begin
 if m.has('unit_scans')then direct_scans:=m.get_array('unit_scans');end if;
 if m.has('aggregation_scans')then aggregates:=m.get_array('aggregation_scans');end if;
 if direct_scans is null or aggregates is null or direct_scans.get_size>20000 or aggregates.get_size>1000 then raise_application_error(-20881,'INTERWARE_SCAN_BOUND');end if;
 for i in 0..direct_scans.get_size-1 loop result_scans.append(direct_scans.get(i));end loop;
 for i in 0..aggregates.get_size-1 loop
 item:=treat(aggregates.get(i)as json_object_t);
 if item is null or item.get_size!=4 then raise_application_error(-20871,'INTERWARE_AGGREGATION_SCAN_FIELDS');end if;
 system_code:=item.get_string('system_code');profile_code:=item.get_string('profile_code');digest:=item.get_string('code_hash');level_code:=item.get_string('level');
 if system_code is null or profile_code is null or digest is null or not regexp_like(digest,'^[a-f0-9]{64}$')or level_code not in('BOX','PALLET')or level_code is null then raise_application_error(-20871,'INTERWARE_AGGREGATION_SCAN_INVALID');end if;
 select count(*)into n from RRL_WMS_RECEIPT_AGG where SYSTEM_CODE=system_code and PROFILE_CODE=profile_code and CODE_HASH=digest and AGG_LEVEL=level_code;
 if n!=1 then raise_application_error(-20886,'INTERWARE_REGISTERED_AGGREGATION_REQUIRED');end if;
 select UID_PALLET into origin_uid from RRL_WMS_RECEIPT_AGG where SYSTEM_CODE=system_code and PROFILE_CODE=profile_code and CODE_HASH=digest and AGG_LEVEL=level_code;
 select count(*)into n from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE used on used.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=used.STOCK_OPERATION_ID and op.STATE='APPLIED'
 where used.UID_PALLET=origin_uid and a.SYSTEM_CODE=system_code and a.PROFILE_CODE=profile_code and a.CODE_HASH=digest and a.AGG_LEVEL=level_code;
 if n!=1 then raise_application_error(-20886,'INTERWARE_APPLIED_SENDER_AGGREGATION_REQUIRED');end if;
 select a.UNITS_JSON,a.PROFILE_VERSION into members,aggregate_version from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE used on used.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 where used.UID_PALLET=origin_uid and a.SYSTEM_CODE=system_code and a.PROFILE_CODE=profile_code and a.CODE_HASH=digest and a.AGG_LEVEL=level_code;
 select count(*)into n from RRL_SKU_RECEIPT_PROFILE profile join RRL_PALLETS p on p.ARTICUL=profile.ARTICUL
 where p.UID_PALLET=origin_uid and profile.SYSTEM_CODE=system_code and profile.PROFILE_CODE=profile_code;
 if n!=1 then raise_application_error(-20886,'INTERWARE_AGGREGATION_CURRENT_PROFILE_REQUIRED');end if;
 select profile.PROFILE_VERSION,profile.SCAN_MODE into current_version,scan_mode from RRL_SKU_RECEIPT_PROFILE profile join RRL_PALLETS p on p.ARTICUL=profile.ARTICUL
 where p.UID_PALLET=origin_uid and profile.SYSTEM_CODE=system_code and profile.PROFILE_CODE=profile_code;
 if current_version!=aggregate_version or scan_mode not in(level_code,'UNIT_OR_AGGREGATION')or scan_mode is null then raise_application_error(-20887,'INTERWARE_AGGREGATION_PROFILE_VERSION_OR_MODE');end if;
 if system_code='CRPT'then
 select count(*)into n from RRL_CRPT_AGGREGATION where UID_PALLET=origin_uid and upper(AGGREGATION_STATUS)in('DISAGGREGATED','CANCELLED','DESTROYED','REJECTED');
 if n!=0 then raise_application_error(-20886,'INTERWARE_REGULATORY_AGGREGATION_INVALIDATED');end if;
 end if;
 expected_count:=json_array_t.parse(members).get_size;
 if expected_count<1 or expected_count>10000 then raise_application_error(-20881,'INTERWARE_AGGREGATION_MEMBER_BOUND');end if;
 select count(*),json_arrayagg(json_object('system_code'value system_code,'profile_code'value profile_code,'code_hash'value code.CODE_HASH)order by u.PHYSICAL_UNIT_KEY returning clob)
 into current_count,expanded_wire
 from json_table(members,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id',Q varchar2(60)path '$.quantity',RAW_CODE varchar2(4000)path '$.code'))j
 join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=origin_uid and u.UNIT_ID=j.UNIT_ID
 join RRL_WMS_RECEIPT_CODE code on code.UID_PALLET=u.UID_PALLET and code.UNIT_ID=u.UNIT_ID and code.SYSTEM_CODE=system_code
 where u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=RRL_STOCK_MATH.quantity(j.Q)
 and exists(select 1 from json_table(code.PROFILES_JSON,'$[*]'columns(P varchar2(80)path '$.profile',C varchar2(4000)path '$.raw_code'))proof where proof.P=profile_code and proof.C=j.RAW_CODE);
 if current_count!=expected_count then raise_application_error(-20886,'INTERWARE_AGGREGATION_MEMBERS_CHANGED');end if;
 expanded:=json_array_t.parse(expanded_wire);
 for j in 0..expanded.get_size-1 loop result_scans.append(expanded.get(j));end loop;
 if result_scans.get_size>20000 then raise_application_error(-20881,'INTERWARE_EXPANDED_SCAN_BOUND');end if;
 end loop;
 p_scans:=result_scans.to_clob;
 end;
end;
/
"""
# Prefix PL variables so SQL never resolves them as self-comparison columns.
import re
for token in ["system_code","profile_code","digest","level_code","origin_uid"]:
 helper=re.sub(r"(?<![.'])\b"+token+r"\b(?!')","v_"+token,helper,flags=re.I)
# Restore JSON literal keys accidentally protected above remain untouched; table columns explicitly qualified.
helper=helper.replace("where SYSTEM_CODE=v_system_code and PROFILE_CODE=v_profile_code and CODE_HASH=v_digest and AGG_LEVEL=v_level_code","where RRL_WMS_RECEIPT_AGG.SYSTEM_CODE=v_system_code and RRL_WMS_RECEIPT_AGG.PROFILE_CODE=v_profile_code and CODE_HASH=v_digest and AGG_LEVEL=v_level_code")
# regex also renamed unqualified table columns; qualify and restore those occurrences.
helper=helper.replace("where v_system_code=v_system_code and v_profile_code=v_profile_code","where RRL_WMS_RECEIPT_AGG.SYSTEM_CODE=v_system_code and RRL_WMS_RECEIPT_AGG.PROFILE_CODE=v_profile_code")
put=lambda n,s:out.__setitem__((folder/n).as_posix(),s)
put("001_aggregation.sql",helper)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_INTERWARE_MARK_SCAN'and TYPE='PACKAGE BODY'order by LINE")
 before="create or replace "+"".join(r[0]for r in q).replace(chr(13)," ").strip()+"\n/\n"
put("000_before_scan.sql",before)
after=before.replace("if m.has('unit_scans') then scans:=m.get_array('unit_scans');end if;","RRL_IW_AGG_SCAN.expand(p_metadata,scans_clob);scans:=json_array_t.parse(scans_clob);")
start="   select count(*) into v_count from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article and (SCAN_MODE is null or SCAN_MODE not in('UNIT','UNIT_OR_AGGREGATION'));"
assert start in after
replacement="""   select count(*)into v_count from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=v_article and(
    p.SCAN_MODE is null or(p.SCAN_MODE not in('UNIT','UNIT_OR_AGGREGATION')and not exists(
     select 1 from json_table(p_metadata,'$.aggregation_scans[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code',L varchar2(10)path '$.level'))agg
     where agg.S=p.SYSTEM_CODE and agg.P=p.PROFILE_CODE and agg.L=p.SCAN_MODE))
    or(p.SCAN_MODE not in('UNIT','UNIT_OR_AGGREGATION')and exists(
     select 1 from json_table(p_metadata,'$.unit_scans[*]'columns(S varchar2(40)path '$.system_code',P varchar2(80)path '$.profile_code'))direct_scan
     where direct_scan.S=p.SYSTEM_CODE and direct_scan.P=p.PROFILE_CODE)));"""
after=after.replace(start,replacement)
put("002_scan.sql",after)
ledger="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-310-interware-aggregation-scan' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing registered non-SAP sender aggregation expands into exact issued unit/profile validation; immutable applied origin and current policy required; no new code registry or legal ACK',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
"""
put("003_ledger.sql",ledger);put("apply.sql","@@001_aggregation.sql\n@@002_scan.sql\n@@003_ledger.sql\n")
put("rollback.sql","@@000_before_scan.sql\ndrop package RRL_IW_AGG_SCAN;\n")
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_IW_AGG_SCAN','RRL_INTERWARE_MARK_SCAN');\n")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));put("000_before_manifest.json",p.read_text(encoding="utf-8"))
m["packages"].append("RRL_IW_AGG_SCAN")
old="../2026-10-12_ni061_flexible_unit_mode/001_scan.sql";pos=m["additional_scripts"].index(old);m["additional_scripts"][pos:pos+1]=["../2026-10-12_ni061_aggregation_scan/001_aggregation.sql","../2026-10-12_ni061_aggregation_scan/002_scan.sql"]
# Spec must exist before scanner body compilation on a clean deployment.
m["components"].append("../2026-10-12_ni061_aggregation_scan/001_aggregation.sql")
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out))
