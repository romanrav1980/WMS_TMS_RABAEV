prompt NI02 immutable SAP store demand on existing customer orders
declare
 procedure ensure_table(nm varchar2, ddl clob) is k number;
 begin select count(*) into k from user_tables where table_name=nm;
 if k=0 then execute immediate ddl; end if; end;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 ensure_table('RRL_SAP_STORE_CALENDAR',q'[
 create table RRL_SAP_STORE_CALENDAR(
 WARE_ID number not null,CUSTOMER_STORE_MAP_ID number not null,UTC_OFFSET_MINUTES number not null,
 DELIVERY_WEEKDAYS varchar2(20) not null,ALLOW_SAME_DAY number default 0 not null,
 UPDATED_AT timestamp default systimestamp not null,UPDATED_BY varchar2(100),
 constraint RRL_SAP_STORE_CAL_PK primary key(WARE_ID,CUSTOMER_STORE_MAP_ID),
 constraint RRL_SAP_STORE_CAL_FK foreign key(CUSTOMER_STORE_MAP_ID) references RRL_CUSTOMER_STORE_MAP(CUSTOMER_STORE_MAP_ID),
 constraint RRL_SAP_STORE_CAL_CK check(ALLOW_SAME_DAY in(0,1) and UTC_OFFSET_MINUTES between -720 and 840 and UTC_OFFSET_MINUTES=trunc(UTC_OFFSET_MINUTES)))]');
 ensure_table('RRL_SAP_STORE_ORDER',q'[
 create table RRL_SAP_STORE_ORDER(
 CUSTOMER_ORDER_ID number not null,SENDER varchar2(100) not null,ORDER_NUMBER varchar2(100) not null,CONTENT_HASH varchar2(64) not null,
 RAW_XML clob not null,DEMAND_JSON clob not null,RESULT_JSON clob not null,ADMISSION_STATUS varchar2(30) not null,
 OPERATIONAL_DATE date not null,DELIVERY_DATE date not null,PICKING_START_AT timestamp not null,PICKING_FINISH_AT timestamp not null,SHIPMENT_AT timestamp not null,
 UTC_OFFSET_MINUTES number not null,CREATED_AT timestamp default systimestamp not null,
 constraint RRL_SAP_STORE_ORDER_PK primary key(CUSTOMER_ORDER_ID),constraint RRL_SAP_STORE_ORDER_UK unique(SENDER,ORDER_NUMBER),
 constraint RRL_SAP_STORE_ORDER_FK foreign key(CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID),
 constraint RRL_SAP_STORE_ORDER_CK check(ADMISSION_STATUS in('ACCEPTED','PENDING_LATE','REJECTED')),
 constraint RRL_SAP_STORE_DEMAND_JSON check(DEMAND_JSON is json),constraint RRL_SAP_STORE_RESULT_JSON check(RESULT_JSON is json))]');
 ensure_table('RRL_SAP_STORE_MESSAGE',q'[
 create table RRL_SAP_STORE_MESSAGE(
 SENDER varchar2(100) not null,MESSAGE_ID varchar2(100) not null,CUSTOMER_ORDER_ID number not null,PAYLOAD_HASH varchar2(64) not null,
 RAW_XML clob not null,RESULT_JSON clob not null,CREATED_AT timestamp default systimestamp not null,CREATED_BY varchar2(100),
 constraint RRL_SAP_STORE_MSG_PK primary key(SENDER,MESSAGE_ID),constraint RRL_SAP_STORE_MSG_FK foreign key(CUSTOMER_ORDER_ID) references RRL_SAP_STORE_ORDER(CUSTOMER_ORDER_ID),
 constraint RRL_SAP_STORE_MSG_JSON check(RESULT_JSON is json))]');
end;
/
create or replace trigger RRL_SAP_STORE_ROW_GUARD
before insert or update or delete on RRL_CUSTOMER_ORDER_ROW for each row
declare n number; v_id number;
begin
 if inserting then v_id:=:new.CUSTOMER_ORDER_ID; else v_id:=:old.CUSTOMER_ORDER_ID; end if;
 select count(*) into n from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=v_id or CUSTOMER_ORDER_ID=:new.CUSTOMER_ORDER_ID;
 if n>0 then
  if inserting or deleting or updating('CUSTOMER_ORDER_ROW_ID') or updating('CUSTOMER_ORDER_ID') or updating('LINE_NO') or updating('ARTICUL') or updating('UNIT_CODE') or updating('ORDER_QTY') or updating('ORDER_WEIGHT') or updating('WARE_ID') then
   raise_application_error(-20862,'Original SAP customer demand is immutable');
  end if;
 end if;
end;
/
create or replace trigger RRL_SAP_STORE_HEAD_GUARD
before update or delete on RRL_CUSTOMER_ORDER for each row
declare n number;
begin
 select count(*) into n from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=:old.CUSTOMER_ORDER_ID;
 if n>0 and (deleting or updating('CUSTOMER_ORDER_ID') or updating('ORDER_NO') or updating('CUSTOMER_ID') or updating('CUSTOMER_STORE_MAP_ID') or updating('WARE_ID') or updating('ORDER_DATE') or updating('SHIPMENT_DATE') or updating('SOURCE_SYSTEM')) then
  raise_application_error(-20862,'Original SAP customer order is immutable');
 end if;
end;
/
create or replace trigger RRL_SAP_STORE_PICK_GUARD
before insert or update of CUSTOMER_ORDER_ID on RRL_PICK_PLAN for each row
declare n number;
begin
 select count(*) into n from RRL_SAP_STORE_ORDER where CUSTOMER_ORDER_ID=:new.CUSTOMER_ORDER_ID and ADMISSION_STATUS!='ACCEPTED';
 if n>0 then raise_application_error(-20863,'Late SAP order requires explicit logistics admission before planning'); end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-07-008-ni02-store-orders' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI02 immutable store demand, source book and late-order planning guard',sysdate,user,'008_apply.sql','008_rollback.sql','APPLIED');
commit;