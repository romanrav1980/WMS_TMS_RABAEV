import json
from pathlib import Path
d=Path("db/migrations/2026-10-12_ni043_aggregation_lifecycle")
sql="""begin execute immediate q'[
create table RRL_TRACE_AGG_INVALIDATION(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 SYSTEM_CODE varchar2(40) not null,PROFILE_CODE varchar2(80) not null,CODE_HASH varchar2(64) not null,
 ORIGIN_UID varchar2(200) not null,WARE_ID number not null,
 REASON_CODE varchar2(30) not null check(REASON_CODE in('OPENED','REPACKED','DAMAGED','COMPOSITION_CHANGED')),
 DOCUMENT_REFERENCE varchar2(200) not null,ACTOR nvarchar2(50) not null,
 JOURNAL_ID number not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRACE_AGG_INVALID_UK unique(SYSTEM_CODE,PROFILE_CODE,CODE_HASH)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
create or replace package RRL_TRACE_AGG_LIFECYCLE authid definer as
 function invalidate(p_operation varchar2,p_request clob,p_actor varchar2)return clob;
 procedure assert_write;
end;
/
create or replace package body RRL_TRACE_AGG_LIFECYCLE as
 g_writing boolean:=false;
 procedure assert_write is begin
 if not g_writing then raise_application_error(-20863,'TRACE_AGG_LIFECYCLE_OWNER_REQUIRED');end if;
 end;
 function invalidate(p_operation varchar2,p_request clob,p_actor varchar2)return clob is
 m json_object_t:=json_object_t.parse(p_request);result json_object_t:=json_object_t();
 v_system varchar2(40);v_profile varchar2(80);v_hash varchar2(64);v_origin varchar2(200);
 v_reason varchar2(30);v_reference varchar2(200);v_ware number;v_journal number;
 digest raw(32);old_digest raw(32);old_result clob;n number;body clob;
 begin
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if p_operation is null or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]{1,100}$')or p_actor is null or RRL_HAS_WRIGHT(p_actor,'trace_manifest_import')!=1 then raise_application_error(-20882,'TRACE_AGG_INVALIDATION_FORBIDDEN');end if;
 if m.get_size!=7 then raise_application_error(-20871,'TRACE_AGG_INVALIDATION_FIELDS');end if;
 v_system:=m.get_string('system_code');v_profile:=m.get_string('profile_code');v_hash:=m.get_string('code_hash');
 v_origin:=m.get_string('origin_pallet_identifier');v_ware:=m.get_number('warehouse_id');
 v_reason:=m.get_string('reason_code');v_reference:=m.get_string('document_reference');
 if v_system is null or v_profile is null or v_origin is null or v_ware is null or v_reason is null or v_reason not in('OPENED','REPACKED','DAMAGED','COMPOSITION_CHANGED')or v_reference is null or not regexp_like(v_hash,'^[a-f0-9]{64}$')or v_hash is null then raise_application_error(-20871,'TRACE_AGG_INVALIDATION_INVALID');end if;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=v_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'TRACE_AGG_CURRENT_WARE_ACTOR_REQUIRED');end if;
 digest:=sys.dbms_crypto.hash(p_request||chr(10)||p_actor,sys.dbms_crypto.hash_sh256);
 begin select PAYLOAD_HASH,RESULT_JSON into old_digest,old_result from RRL_TRACE_AGG_INVALIDATION where OPERATION_ID=p_operation;
 if old_digest!=digest then raise_application_error(-20864,'TRACE_AGG_INVALIDATION_PAYLOAD_CONFLICT');end if;
 return old_result;exception when no_data_found then null;end;
 select count(*)into n from RRL_WMS_RECEIPT_AGG where SYSTEM_CODE=v_system and PROFILE_CODE=v_profile and CODE_HASH=v_hash and UID_PALLET=v_origin;
 if n!=1 then raise_application_error(-20886,'TRACE_AGG_REGISTERED_ORIGIN_REQUIRED');end if;
 select count(*)into n from RRL_WMS_RECEIPT_UNIT u where u.UID_PALLET=v_origin and u.STOCK_STATUS in('AVAILABLE','RESERVED')
 and exists(select 1 from RRL_PALLETS p join RRL_CELLS c on c.CELL=p.CELL where p.UID_PALLET=u.CURRENT_UID and c.WARE_ID=v_ware);
 if n=0 then raise_application_error(-20886,'TRACE_AGG_LOCAL_CUSTODY_REQUIRED');end if;
 result.put('operation_id',p_operation);result.put('status','INVALIDATED_LOCAL');result.put('system_code',v_system);
 result.put('profile_code',v_profile);result.put('code_hash',v_hash);result.put('origin_pallet_identifier',v_origin);
 result.put('warehouse_id',v_ware);result.put('reason_code',v_reason);result.put('document_reference',v_reference);
 result.put('actor',p_actor);result.put('stock_changed',false);result.put('government_ack_created',false);
 body:=result.to_clob;
 v_journal:=RRL_REGULATORY_API.write_journal(p_system_code=>v_system,p_entity_type=>'LOCAL_AGGREGATION',p_entity_id=>v_hash,p_uid_pallet=>v_origin,
 p_operation_type=>'LOCAL_AGGREGATION_INVALIDATE',p_old_status=>'REGISTERED',p_new_status=>'INVALIDATED_LOCAL',
 p_document_id=>v_reference,p_external_operation_id=>p_operation,p_payload_json=>body,p_message=>v_reason,p_created_by=>p_actor);
 result.put('journal_id',v_journal);body:=result.to_clob;
 g_writing:=true;
 insert into RRL_TRACE_AGG_INVALIDATION(OPERATION_ID,PAYLOAD_HASH,SYSTEM_CODE,PROFILE_CODE,CODE_HASH,ORIGIN_UID,WARE_ID,REASON_CODE,DOCUMENT_REFERENCE,ACTOR,JOURNAL_ID,RESULT_JSON)
 values(p_operation,digest,v_system,v_profile,v_hash,v_origin,v_ware,v_reason,v_reference,p_actor,v_journal,body);
 g_writing:=false;return body;
 exception when others then g_writing:=false;raise;
 end;
end;
/
create or replace trigger RRL_TRACE_AGG_INVALID_GUARD before insert or update or delete on RRL_TRACE_AGG_INVALIDATION for each row
begin
 if not inserting then raise_application_error(-20863,'TRACE_AGG_INVALIDATION_IMMUTABLE');end if;
 RRL_TRACE_AGG_LIFECYCLE.assert_write;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
end;
/
"""
# Current native scan owner source is captured before changing it.
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select text from user_source where name='RRL_IW_AGG_SCAN'and type='PACKAGE BODY'order by line")
 before="create or replace "+"".join(r[0]for r in q).replace("\r","")+"\n/\n"
 marker="if v_system_code='CRPT'then"
 assert before.count(marker)==1
 check="""select count(*)into n from RRL_TRACE_AGG_INVALIDATION where SYSTEM_CODE=v_system_code and PROFILE_CODE=v_profile_code and CODE_HASH=v_digest;
 if n!=0 then raise_application_error(-20886,'INTERWARE_LOCAL_AGGREGATION_INVALIDATED');end if;
 """
 after=before.replace(marker,check+marker)
out={str(d/"001_lifecycle.sql"):sql,str(d/"002_scan_guard.sql"):after,str(d/"000_before_scan.sql"):before,
 str(d/"apply.sql"):"@@001_lifecycle.sql\n@@002_scan_guard.sql\n@@003_ledger.sql\n",
 str(d/"003_ledger.sql"):"merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-450-local-aggregation-invalidation' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Immutable per-profile local aggregation invalidation; existing regulatory journal; no quantity effect',sysdate,user,'apply.sql','rollback.sql','APPLIED');\n/\n",
 str(d/"rollback.sql"):"@@000_before_scan.sql\n-- Historical invalidation facts remain immutable. Do not drop committed facts.\n"}
print(json.dumps(out))
