-- C-0164: composition of an assembled trade order reported to SAP and SKM, and their business acknowledgments.
-- A snapshot is immutable except for the per-system outcome; a newer snapshot supersedes it. No stock data is stored or changed here.
create table RRL_TRADE_ORDER_COMPOSITION(
 WARE_ID number not null,ORDER_ID varchar2(100)not null,COMPOSITION_NO number not null,ORDER_VERSION number not null,CUSTOMER_ORDER_ID number not null,
 SIGNATURE varchar2(64)not null,UNIT_COUNT number not null,CARRIER_COUNT number not null,CODE_COUNT number not null,
 SOURCE_ID varchar2(100)not null,SKM_ID varchar2(100),SITE_VERSION number not null,
 SAP_STATUS varchar2(12)not null,SAP_REASON varchar2(2000),SAP_EVENT_ID varchar2(100),
 SKM_STATUS varchar2(12)not null,SKM_REASON varchar2(2000),SKM_EVENT_ID varchar2(100),
 STATE varchar2(12)not null,OUTBOX_ID number,PAYLOAD_JSON clob not null,CREATED_BY varchar2(50)not null,
 CREATED_AT timestamp with time zone default systimestamp not null,UPDATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_ORDER_COMP_PK primary key(WARE_ID,ORDER_ID,COMPOSITION_NO),
 constraint RRL_TRADE_ORDER_COMP_SITE_FK foreign key(WARE_ID)references RRL_TRADE_SITE(WARE_ID),
 constraint RRL_TRADE_ORDER_COMP_SAP check(SAP_STATUS in('WAITING','ACCEPTED','REJECTED')),
 constraint RRL_TRADE_ORDER_COMP_SKM check(SKM_STATUS in('WAITING','ACCEPTED','REJECTED','NOT_REQUIRED')),
 constraint RRL_TRADE_ORDER_COMP_SKM_ID check(SKM_STATUS='NOT_REQUIRED'or SKM_ID is not null),
 constraint RRL_TRADE_ORDER_COMP_STATE check(STATE in('CURRENT','SUPERSEDED')),
 constraint RRL_TRADE_ORDER_COMP_JSON check(PAYLOAD_JSON is json)
);
create unique index RRL_TRADE_ORDER_COMP_CUR_UK on RRL_TRADE_ORDER_COMPOSITION(case when STATE='CURRENT'then WARE_ID end,case when STATE='CURRENT'then ORDER_ID end);
create table RRL_TRADE_COMPOSITION_ACK(
 WARE_ID number not null,SYSTEM_CODE varchar2(3)not null,SENDER_ID varchar2(100)not null,EVENT_ID varchar2(100)not null,
 ORDER_ID varchar2(100)not null,COMPOSITION_NO number not null,OUTCOME varchar2(12)not null,PAYLOAD_HASH varchar2(64)not null,
 BODY_JSON clob not null,RESULT_JSON clob not null,ACTOR varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_COMP_ACK_PK primary key(WARE_ID,SYSTEM_CODE,SENDER_ID,EVENT_ID),
 constraint RRL_TRADE_COMP_ACK_FK foreign key(WARE_ID,ORDER_ID,COMPOSITION_NO)references RRL_TRADE_ORDER_COMPOSITION(WARE_ID,ORDER_ID,COMPOSITION_NO),
 constraint RRL_TRADE_COMP_ACK_SYSTEM check(SYSTEM_CODE in('SAP','SKM')),
 constraint RRL_TRADE_COMP_ACK_OUTCOME check(OUTCOME in('ACCEPTED','REJECTED')),
 constraint RRL_TRADE_COMP_ACK_JSON check(BODY_JSON is json and RESULT_JSON is json)
);
create or replace trigger RRL_TRADE_COMP_ACK_APPEND before update or delete on RRL_TRADE_COMPOSITION_ACK
begin raise_application_error(-20902,'COMPOSITION_ACK_APPEND_ONLY');end;
/
-- Only STATE, the per-system outcome and UPDATED_AT/OUTBOX_ID change; the reported composition itself never does (LOBs cannot be listed in UPDATE OF).
create or replace trigger RRL_TRADE_ORDER_COMP_FROZEN before delete or update on RRL_TRADE_ORDER_COMPOSITION for each row
begin
 if deleting or :new.WARE_ID<>:old.WARE_ID or :new.ORDER_ID<>:old.ORDER_ID or :new.COMPOSITION_NO<>:old.COMPOSITION_NO
  or :new.ORDER_VERSION<>:old.ORDER_VERSION or :new.CUSTOMER_ORDER_ID<>:old.CUSTOMER_ORDER_ID or :new.SIGNATURE<>:old.SIGNATURE
  or :new.UNIT_COUNT<>:old.UNIT_COUNT or :new.CARRIER_COUNT<>:old.CARRIER_COUNT or :new.CODE_COUNT<>:old.CODE_COUNT or :new.SOURCE_ID<>:old.SOURCE_ID
  or (case when :new.SKM_ID=:old.SKM_ID or(:new.SKM_ID is null and :old.SKM_ID is null)then 0 else 1 end)=1 or :new.SITE_VERSION<>:old.SITE_VERSION or :new.CREATED_BY<>:old.CREATED_BY
  or dbms_lob.compare(:new.PAYLOAD_JSON,:old.PAYLOAD_JSON)<>0 then raise_application_error(-20902,'COMPOSITION_SNAPSHOT_FROZEN');end if;
end;
/
