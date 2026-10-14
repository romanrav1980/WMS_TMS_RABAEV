create or replace trigger RRL_TRACE_SENDER_MANIFEST_GUARD before insert or update or delete on RRL_TRACE_SENDER_MANIFEST for each row
declare n number;matched number;total number;
begin
 if not inserting then raise_application_error(-20863,'TRACE_SENDER_MANIFEST_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 if :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TRACE_MANIFEST_METADATA_ACTOR_REQUIRED');end if;
 select count(*)into n from RUSERS u where ID=:new.ACTOR and nvl(DELETED,0)=0 and(WARE_ID=:new.WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'trace_manifest_import')=1;
 if n!=1 then raise_application_error(-20882,'TRACE_MANIFEST_WARE_ACTOR_REQUIRED');end if;
 if :new.SOURCE_KIND='INVENTORY' then
  select count(*)into n from RRL_REVIZION where ID=:new.SOURCE_DOC_ID and WARE_ID=:new.WARE_ID and CONDITION in(0,1);
 else
  select count(*)into n from RRL_MES_MOVEMENT m join RRL_PRODUCTION_ORDER p on p.PRODUCTION_ORDER_ID=m.PRODUCTION_ORDER_ID join RRL_CELLS c on c.CELL=m.TARGET_LOCATION where m.MOVEMENT_ID=:new.SOURCE_DOC_ID and m.MOVEMENT_TYPE='FG_PALLET_RELEASE'and m.UID_PALLET=:new.UID_PALLET and p.TARGET_ARTICUL=:new.ARTICLE and c.WARE_ID=:new.WARE_ID;
 end if;
 if n!=1 then raise_application_error(-20886,'TRACE_MANIFEST_CURRENT_ORIGINAL_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_SKU_RECEIPT_POLICY where ARTICUL=:new.ARTICLE and POLICY_VERSION=:new.POLICY_VERSION and MARKING_REQUIRED=1;
 if n!=1 then raise_application_error(-20886,'TRACE_MANIFEST_CURRENT_MARKED_POLICY_REQUIRED');end if;
 select count(*)into total from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:new.ARTICLE;
 select count(*)into matched from json_table(:new.PROFILES_JSON,'$[*]' columns(SYSTEM_CODE varchar2(40)path '$.system_code',PROFILE_CODE varchar2(80)path '$.profile_code',VERSION_NO varchar2(40)path '$.version',SCAN_MODE varchar2(30)path '$.mode')) j join RRL_SKU_RECEIPT_PROFILE p on p.ARTICUL=:new.ARTICLE and p.SYSTEM_CODE=j.SYSTEM_CODE and p.PROFILE_CODE=j.PROFILE_CODE and p.PROFILE_VERSION=j.VERSION_NO and p.SCAN_MODE=j.SCAN_MODE;
 if total<1 or total>50 or total!=matched then raise_application_error(-20886,'TRACE_MANIFEST_PROFILE_VERSION_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_UOM_CONVERSION where ARTICUL=:new.ARTICLE and INPUT_UOM=:new.BASE_UOM and BASE_UOM=:new.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
 if n=0 then raise_application_error(-20886,'TRACE_MANIFEST_BASE_UOM_REQUIRED');end if;
 if lower(rawtohex(sys.dbms_crypto.hash(:new.RAW_JSON,sys.dbms_crypto.hash_sh256)))!=:new.RAW_SHA256 then raise_application_error(-20886,'TRACE_MANIFEST_ORIGINAL_UTF8_HASH_REQUIRED');end if;
end;
/
create or replace trigger RRL_TRACE_SENDER_AGG_GUARD before insert or update or delete on RRL_TRACE_SENDER_AGG for each row
declare n number;total number;v_article varchar2(160);v_actor nvarchar2(50);
begin
 if not inserting then raise_application_error(-20863,'TRACE_SENDER_AGG_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select ARTICLE,ACTOR into v_article,v_actor from RRL_TRACE_SENDER_MANIFEST where OPERATION_ID=:new.MANIFEST_OPERATION_ID;
 if v_actor!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TRACE_AGG_ORIGINAL_MANIFEST_ACTOR_REQUIRED');end if;
 select count(*)into n from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article and SYSTEM_CODE=:new.SYSTEM_CODE and PROFILE_CODE=:new.PROFILE_CODE and PROFILE_VERSION=:new.PROFILE_VERSION;
 if n!=1 then raise_application_error(-20886,'TRACE_AGG_CURRENT_PROFILE_REQUIRED');end if;
 if lower(rawtohex(sys.dbms_crypto.hash(:new.RAW_CODE,sys.dbms_crypto.hash_sh256)))!=:new.CODE_HASH then raise_application_error(-20886,'TRACE_AGG_CODE_HASH_REQUIRED');end if;
 select count(*),count(distinct UNIT_ID)into total,n from json_table(:new.UNITS_JSON,'$[*]'columns(UNIT_ID varchar2(100)path '$.unit_id'));
 if total=0 or total>10000 or total!=n then raise_application_error(-20886,'TRACE_AGG_EXACT_UNIQUE_MEMBERS_REQUIRED');end if;
end;
/
create or replace trigger RRL_TRACE_MANIFEST_USE_GUARD before insert or update or delete on RRL_TRACE_MANIFEST_USE for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);raw_request clob;d json_object_t;m json_object_t;c json_object_t;manifest RRL_TRACE_SENDER_MANIFEST%rowtype;n number;
begin
 if not inserting then raise_application_error(-20863,'TRACE_MANIFEST_USE_IMMUTABLE');end if;
 if op is null or op!=:new.STOCK_OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TRACE_MANIFEST_USE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,CANONICAL_REQUEST into v_kind,v_state,raw_request from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind not in('INVENTORY_REGISTER_LOT','MES_MOVEMENTS')or v_state!='IN_FLIGHT' then raise_application_error(-20863,'TRACE_MANIFEST_USE_BIRTH_REQUIRED');end if;
 select *into manifest from RRL_TRACE_SENDER_MANIFEST where OPERATION_ID=:new.MANIFEST_OPERATION_ID;
 if manifest.UID_PALLET!=:new.UID_PALLET then raise_application_error(-20863,'TRACE_MANIFEST_USE_ORIGINAL_PALLET_REQUIRED');end if;
 d:=json_object_t.parse(raw_request);m:=d.get_object('metadata').get_object('birth_captures');c:=m.get_object(:new.UID_PALLET);
 if c.get_string('manifest_operation_id')!=:new.MANIFEST_OPERATION_ID then raise_application_error(-20863,'TRACE_MANIFEST_USE_CANONICAL_SOURCE_REQUIRED');end if;
 if v_kind='INVENTORY_REGISTER_LOT' then
  if manifest.SOURCE_KIND!='INVENTORY'or d.get_object('source').get_number('revision_id')!=manifest.SOURCE_DOC_ID then raise_application_error(-20863,'TRACE_MANIFEST_USE_REVISION_REQUIRED');end if;
 else
  select count(*)into n from json_table(raw_request,'$.source.movement_ids[*]'columns(MOVEMENT_ID number path '$')) j where j.MOVEMENT_ID=manifest.SOURCE_DOC_ID;
  if manifest.SOURCE_KIND!='MES'or n!=1 then raise_application_error(-20863,'TRACE_MANIFEST_USE_MES_REQUIRED');end if;
 end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
end;
/
