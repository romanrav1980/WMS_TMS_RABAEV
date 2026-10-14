begin execute immediate q'[
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
begin execute immediate q'[
create table RRL_TRACE_AGG_BLOCK(
 SYSTEM_CODE varchar2(40) not null,PROFILE_CODE varchar2(80) not null,CODE_HASH varchar2(64) not null,
 INVALIDATION_OPERATION_ID varchar2(100) not null references RRL_TRACE_AGG_INVALIDATION(OPERATION_ID),
 ORIGIN_UID varchar2(200) not null,
 constraint RRL_TRACE_AGG_BLOCK_PK primary key(SYSTEM_CODE,PROFILE_CODE,CODE_HASH)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
create or replace package RRL_TRACE_AGG_LIFECYCLE authid definer as
 function invalidate(p_operation varchar2,p_request clob,p_actor varchar2)return clob;
 procedure assert_write;
 procedure assert_scan(p_system varchar2,p_profile varchar2,p_hash varchar2);
end;
/
create or replace package body RRL_TRACE_AGG_LIFECYCLE as
 g_writing boolean:=false;
 procedure assert_write is begin
 if not g_writing then raise_application_error(-20863,'TRACE_AGG_LIFECYCLE_OWNER_REQUIRED');end if;
 end;
 procedure assert_scan(p_system varchar2,p_profile varchar2,p_hash varchar2)is n number;begin
 select count(*)into n from RRL_TRACE_AGG_BLOCK where SYSTEM_CODE=p_system and PROFILE_CODE=p_profile and CODE_HASH=p_hash;
 if n!=0 then raise_application_error(-20886,'INTERWARE_LOCAL_AGGREGATION_INVALIDATED');end if;
 end;
 function invalidate(p_operation varchar2,p_request clob,p_actor varchar2)return clob is
 m json_object_t:=json_object_t.parse(p_request);result json_object_t:=json_object_t();
 v_system varchar2(40);v_profile varchar2(80);v_hash varchar2(64);v_origin varchar2(200);
 v_reason varchar2(30);v_reference varchar2(200);v_ware number;v_journal number;
 digest raw(32);old_digest raw(32);old_result clob;n number;body clob;blocked_wire clob;members_wire clob;expected_members number;v_manifest varchar2(100);v_node varchar2(100);blocked json_array_t;blocked_item json_object_t;
 begin
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if p_operation is null or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]{1,100}$')or p_actor is null or RRL_HAS_WRIGHT(p_actor,'trace_manifest_import')!=1 then raise_application_error(-20882,'TRACE_AGG_INVALIDATION_FORBIDDEN');end if;
 if m.get_size!=7 then raise_application_error(-20871,'TRACE_AGG_INVALIDATION_FIELDS');end if;
 v_system:=m.get_string('system_code');v_profile:=m.get_string('profile_code');v_hash:=m.get_string('code_hash');
 v_origin:=m.get_string('origin_pallet_identifier');v_ware:=m.get_number('warehouse_id');
 v_reason:=m.get_string('reason_code');v_reference:=m.get_string('document_reference');
 if v_system is null or v_profile is null or v_origin is null or v_ware is null or v_reason is null or v_reason not in('OPENED','REPACKED','DAMAGED','COMPOSITION_CHANGED')or trim(v_reference) is null or not regexp_like(v_hash,'^[a-f0-9]{64}$')or v_hash is null then raise_application_error(-20871,'TRACE_AGG_INVALIDATION_INVALID');end if;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=v_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'TRACE_AGG_CURRENT_WARE_ACTOR_REQUIRED');end if;
 digest:=sys.dbms_crypto.hash(p_request||chr(10)||p_actor,sys.dbms_crypto.hash_sh256);
 begin select PAYLOAD_HASH,RESULT_JSON into old_digest,old_result from RRL_TRACE_AGG_INVALIDATION where OPERATION_ID=p_operation;
 if old_digest!=digest then raise_application_error(-20864,'TRACE_AGG_INVALIDATION_PAYLOAD_CONFLICT');end if;
 return old_result;exception when no_data_found then null;end;
 select count(*)into n from(
 select a.CODE_HASH from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE u on u.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=u.STOCK_OPERATION_ID and op.STATE='APPLIED'
 where u.UID_PALLET=v_origin and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile and a.CODE_HASH=v_hash
 union all
 select a.CODE_HASH from RRL_SAP_TRACE_AGG a join RRL_SAP_PALLET_RECEIPT r on r.ORDER_ID=a.ORDER_ID and r.LINE_NUMBER=a.LINE_NUMBER
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=r.STOCK_OPERATION_ID and op.STATE='APPLIED'and op.COMMAND_TYPE='SAP_RECEIPT'
 where r.UID_PALLET=v_origin and r.POSTED_BASE_QTY>0 and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile and a.CODE_HASH=v_hash
 );
 if n!=1 then raise_application_error(-20886,'TRACE_AGG_REGISTERED_ORIGIN_REQUIRED');end if;
 begin
 select a.UNITS_JSON,a.MANIFEST_OPERATION_ID,a.AGGREGATION_ID into members_wire,v_manifest,v_node from RRL_TRACE_SENDER_AGG a join RRL_TRACE_MANIFEST_USE u on u.MANIFEST_OPERATION_ID=a.MANIFEST_OPERATION_ID
 where u.UID_PALLET=v_origin and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile and a.CODE_HASH=v_hash;
 exception when no_data_found then
 select a.UNITS_JSON into members_wire from RRL_SAP_TRACE_AGG a join RRL_SAP_PALLET_RECEIPT r on r.ORDER_ID=a.ORDER_ID and r.LINE_NUMBER=a.LINE_NUMBER
 where r.UID_PALLET=v_origin and r.POSTED_BASE_QTY>0 and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile and a.CODE_HASH=v_hash;
 end;
 expected_members:=json_array_t.parse(members_wire).get_size;
 if expected_members<1 or expected_members>10000 then raise_application_error(-20881,'TRACE_AGG_MEMBER_BOUND');end if;
 select count(*)into n from json_table(members_wire,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id'))j
 join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=v_origin and u.UNIT_ID=j.UNIT_ID
 join RRL_CELLS c on c.CELL=u.CURRENT_CELL and c.WARE_ID=v_ware
 where u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null;
 if n!=expected_members then raise_application_error(-20886,'TRACE_AGG_ALL_FREE_MEMBERS_LOCAL_CUSTODY_REQUIRED');end if;
 select count(*)into n from RRL_TRACE_AGG_BLOCK where SYSTEM_CODE=v_system and PROFILE_CODE=v_profile and CODE_HASH=v_hash;
 if n!=0 then raise_application_error(-20886,'TRACE_AGG_ALREADY_INVALIDATED');end if;
 if v_manifest is not null then
 select json_arrayagg(json_object('code_hash'value x.CODE_HASH)returning clob)into blocked_wire from(
 select v_hash CODE_HASH from dual
 union
 select a.CODE_HASH from RRL_TRACE_SENDER_AGG a
 where a.MANIFEST_OPERATION_ID=v_manifest and a.SYSTEM_CODE=v_system and a.PROFILE_CODE=v_profile
 and a.AGGREGATION_ID in(
 select e.PARENT_ID from(
 select j.PARENT_ID,j.CHILD_ID from RRL_TRACE_SENDER_MANIFEST manifest
 cross join json_table(manifest.RAW_JSON,'$.aggregations[*]'columns(PARENT_ID varchar2(100)path '$.aggregation_id',
 nested path '$.children[*]'columns(CHILD_ID varchar2(100)path '$')))j
 where manifest.OPERATION_ID=v_manifest and j.CHILD_ID is not null)e
 start with e.CHILD_ID=v_node connect by nocycle prior e.PARENT_ID=e.CHILD_ID))x;
 else
 select json_arrayagg(json_object('code_hash'value x.CODE_HASH)returning clob)into blocked_wire from(
 select v_hash CODE_HASH from dual
 union
 select parent.CODE_HASH from RRL_SAP_TRACE_AGG parent join RRL_SAP_PALLET_RECEIPT rec on rec.ORDER_ID=parent.ORDER_ID and rec.LINE_NUMBER=parent.LINE_NUMBER
 join RRL_SAP_TRACE_AGG child on child.ORDER_ID=parent.ORDER_ID and child.LINE_NUMBER=parent.LINE_NUMBER and child.SYSTEM_CODE=parent.SYSTEM_CODE and child.PROFILE_CODE=parent.PROFILE_CODE
 where rec.UID_PALLET=v_origin and parent.SYSTEM_CODE=v_system and parent.PROFILE_CODE=v_profile and child.CODE_HASH=v_hash
 and child.AGG_LEVEL='BOX'and parent.AGG_LEVEL='PALLET'
 and not exists(select 1 from json_table(child.UNITS_JSON,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id'))cu
 where not exists(select 1 from json_table(parent.UNITS_JSON,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id'))pu where pu.UNIT_ID=cu.UNIT_ID)))x;
 end if;
 blocked:=json_array_t.parse(blocked_wire);
 if blocked.get_size<1 or blocked.get_size>1000 then raise_application_error(-20881,'TRACE_AGG_ANCESTOR_BOUND');end if;
 result.put('operation_id',p_operation);result.put('status','INVALIDATED_LOCAL');result.put('system_code',v_system);
 result.put('profile_code',v_profile);result.put('code_hash',v_hash);result.put('origin_pallet_identifier',v_origin);
 result.put('warehouse_id',v_ware);result.put('reason_code',v_reason);result.put('document_reference',v_reference);
 result.put('actor',p_actor);result.put('stock_changed',false);result.put('government_ack_created',false);
 result.put('blocked_aggregate_count',blocked.get_size);result.put('blocked_aggregates',blocked);body:=result.to_clob;
 v_journal:=RRL_REGULATORY_API.write_journal(p_system_code=>v_system,p_entity_type=>'LOCAL_AGGREGATION',p_entity_id=>v_hash,p_uid_pallet=>v_origin,
 p_operation_type=>'LOCAL_AGGREGATION_INVALIDATE',p_old_status=>'REGISTERED',p_new_status=>'INVALIDATED_LOCAL',
 p_document_id=>v_reference,p_external_operation_id=>p_operation,p_payload_json=>body,p_message=>v_reason,p_created_by=>p_actor);
 result.put('journal_id',v_journal);body:=result.to_clob;
 g_writing:=true;
 insert into RRL_TRACE_AGG_INVALIDATION(OPERATION_ID,PAYLOAD_HASH,SYSTEM_CODE,PROFILE_CODE,CODE_HASH,ORIGIN_UID,WARE_ID,REASON_CODE,DOCUMENT_REFERENCE,ACTOR,JOURNAL_ID,RESULT_JSON)
 values(p_operation,digest,v_system,v_profile,v_hash,v_origin,v_ware,v_reason,v_reference,p_actor,v_journal,body);
 for i in 0..blocked.get_size-1 loop
 blocked_item:=treat(blocked.get(i)as json_object_t);
 declare v_block_hash varchar2(64):=blocked_item.get_string('code_hash');begin
 insert into RRL_TRACE_AGG_BLOCK(SYSTEM_CODE,PROFILE_CODE,CODE_HASH,INVALIDATION_OPERATION_ID,ORIGIN_UID)
 select v_system,v_profile,v_block_hash,p_operation,v_origin from dual
 where not exists(select 1 from RRL_TRACE_AGG_BLOCK where SYSTEM_CODE=v_system and PROFILE_CODE=v_profile and CODE_HASH=v_block_hash);
 end;
 end loop;
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


create or replace trigger RRL_TRACE_AGG_BLOCK_GUARD before insert or update or delete on RRL_TRACE_AGG_BLOCK for each row
begin
 if not inserting then raise_application_error(-20863,'TRACE_AGG_BLOCK_IMMUTABLE');end if;
 RRL_TRACE_AGG_LIFECYCLE.assert_write;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
end;
/
