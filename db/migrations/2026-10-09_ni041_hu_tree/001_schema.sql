-- Existing pallet identity; no parent quantitative stock or regulatory rewrite.
declare procedure col(p_name varchar2,p_sql varchar2) is n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_PALLETS' and COLUMN_NAME=p_name;
 if n=0 then execute immediate p_sql;end if;end;
begin
 col('HU_KIND','alter table RRL_PALLETS add HU_KIND varchar2(20) default ''STOCK'' not null');
 col('HU_TYPE','alter table RRL_PALLETS add HU_TYPE varchar2(20)');
 col('HU_CONTENT_VERSION','alter table RRL_PALLETS add HU_CONTENT_VERSION number default 0 not null');
 col('HU_CURRENT_CELL','alter table RRL_PALLETS add HU_CURRENT_CELL varchar2(60)');
 col('HU_TARE_WEIGHT_KG','alter table RRL_PALLETS add HU_TARE_WEIGHT_KG number default 0 not null');
end;
/
declare n number;begin
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_PALLET_HU_KIND_CK';
 if n=0 then execute immediate 'alter table RRL_PALLETS add constraint RRL_PALLET_HU_KIND_CK check(HU_KIND in(''STOCK'',''CONTAINER'') and HU_CONTENT_VERSION>=0 and HU_CONTENT_VERSION=trunc(HU_CONTENT_VERSION) and HU_TARE_WEIGHT_KG>=0 and (HU_KIND=''STOCK'' or (ARTICUL is null and UNIT_COUNT=0 and HU_CURRENT_CELL is not null and HU_TYPE in(''PALLET'',''BOX'',''ROLL_CAGE'',''BAG''))))';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_WMS_HU_LINK';
 if n=0 then execute immediate 'create table RRL_WMS_HU_LINK(
  HU_LINK_ID number primary key,PARENT_UID varchar2(200) not null,
  CHILD_PALLET_UID varchar2(200),CHILD_CASE_TASK_ID number,
  ACTIVE_FLAG number default 1 not null,LINK_VERSION number default 0 not null,
  LINKED_OPERATION_ID varchar2(100) not null,LINKED_AT timestamp with time zone default systimestamp not null,LINKED_BY varchar2(50) not null,
  UNLINKED_OPERATION_ID varchar2(100),UNLINKED_AT timestamp with time zone,UNLINKED_BY varchar2(50),
  constraint RRL_HU_PARENT_FK foreign key(PARENT_UID) references RRL_PALLETS(UID_PALLET),
  constraint RRL_HU_CHILD_PALLET_FK foreign key(CHILD_PALLET_UID) references RRL_PALLETS(UID_PALLET),
  constraint RRL_HU_CHILD_CASE_FK foreign key(CHILD_CASE_TASK_ID) references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
  constraint RRL_HU_LINK_CK check(ACTIVE_FLAG in(0,1) and LINK_VERSION>=0 and LINK_VERSION=trunc(LINK_VERSION)
   and ((CHILD_PALLET_UID is not null and CHILD_CASE_TASK_ID is null and CHILD_PALLET_UID!=PARENT_UID)
    or (CHILD_PALLET_UID is null and CHILD_CASE_TASK_ID is not null))))';
 execute immediate 'create unique index RRL_HU_ONE_PALLET_PARENT on RRL_WMS_HU_LINK(case when ACTIVE_FLAG=1 then CHILD_PALLET_UID end)';
 execute immediate 'create unique index RRL_HU_ONE_CASE_PARENT on RRL_WMS_HU_LINK(case when ACTIVE_FLAG=1 then CHILD_CASE_TASK_ID end)';
 execute immediate 'create index RRL_HU_PARENT_CHILD on RRL_WMS_HU_LINK(PARENT_UID,ACTIVE_FLAG,HU_LINK_ID)';
 end if;
 select count(*) into n from USER_SEQUENCES where SEQUENCE_NAME='RRL_WMS_HU_LINK_SQ';
 if n=0 then execute immediate 'create sequence RRL_WMS_HU_LINK_SQ';end if;
end;
/
create or replace trigger RRL_HU_LINK_WRITE_GUARD before insert or update or delete on RRL_WMS_HU_LINK for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 if deleting then raise_application_error(-20863,'HU_LINK_HISTORY_IMMUTABLE');end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
  sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_LINK_ROOT_COMMAND_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind not in('HU_ATTACH','HU_DETACH','HU_REPACK') then raise_application_error(-20863,'HU_LINK_COMMAND_INVALID');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.PARENT_UID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(:new.HU_LINK_ID)));
 if :new.CHILD_PALLET_UID is not null then RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.CHILD_PALLET_UID));end if;
 if inserting and (:new.ACTIVE_FLAG!=1 or :new.LINK_VERSION!=0 or :new.LINKED_OPERATION_ID!=v_op) then raise_application_error(-20863,'HU_LINK_INITIAL_VERSION_INVALID');end if;
 if updating and (:new.HU_LINK_ID!=:old.HU_LINK_ID or :new.PARENT_UID!=:old.PARENT_UID
  or nvl(:new.CHILD_PALLET_UID,chr(0))!=nvl(:old.CHILD_PALLET_UID,chr(0))
  or nvl(:new.CHILD_CASE_TASK_ID,-1)!=nvl(:old.CHILD_CASE_TASK_ID,-1)
  or :old.ACTIVE_FLAG!=1 or :new.ACTIVE_FLAG!=0 or :new.LINK_VERSION!=:old.LINK_VERSION+1
  or :new.UNLINKED_OPERATION_ID!=v_op or :new.LINKED_OPERATION_ID!=:old.LINKED_OPERATION_ID) then
  raise_application_error(-20863,'HU_LINK_HISTORY_OR_VERSION_INVALID');end if;
end;
/
create or replace trigger RRL_HU_CONTAINER_GUARD before insert or update of HU_KIND,HU_TYPE,HU_CONTENT_VERSION,HU_CURRENT_CELL,HU_TARE_WEIGHT_KG on RRL_PALLETS for each row
declare v_op varchar2(100);v_kind varchar2(80);
begin
 if inserting and :new.HU_KIND='STOCK' then return;end if;
 v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 if v_op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or
  sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'HU_METADATA_ROOT_COMMAND_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 if v_kind not in('HU_CREATE','HU_ATTACH','HU_DETACH','HU_REPACK','HU_MOVE','HU_TASK_COMPLETE') then raise_application_error(-20863,'HU_METADATA_COMMAND_INVALID');end if;
 RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));
 if updating and (:new.HU_KIND!=:old.HU_KIND or :new.HU_CONTENT_VERSION!=:old.HU_CONTENT_VERSION+1) then raise_application_error(-20863,'HU_IDENTITY_OR_VERSION_INVALID');end if;
end;
/
