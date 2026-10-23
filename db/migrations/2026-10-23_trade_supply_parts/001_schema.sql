-- C-0163: incoming SUPPLY composition sent in parts. A transfer collects its parts and the END summary durably; only a complete and
-- verified transfer is handed, once, to the existing document intake (RRL_TRADE_DOCUMENT_API.receive_document) as the same canonical
-- SUPPLY. No goods, no codes are written here: physical receipt stays with the existing owners.
create table RRL_TRADE_SUPPLY_TRANSFER(
 WARE_ID number not null,SOURCE_ID varchar2(100)not null,TRANSFER_ID varchar2(100)not null,
 DOCUMENT_ID varchar2(100)not null,VERSION_NO number not null,PART_COUNT number not null,
 HEADER_JSON clob not null,HEADER_HASH varchar2(64)not null,
 END_EVENT_ID varchar2(100),END_HASH varchar2(64),END_TOTAL number,END_CODES_SHA varchar2(64),END_OCCURRED_AT varchar2(40),
 STATUS varchar2(20)not null,STATUS_REASON varchar2(200),RECEIVED_CODES number default 0 not null,
 DELIVERED_EVENT_ID varchar2(100),DELIVERY_RESULT clob,CREATED_BY varchar2(50)not null,
 CREATED_AT timestamp with time zone default systimestamp not null,UPDATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_SUPPLY_TRANSFER_PK primary key(WARE_ID,SOURCE_ID,TRANSFER_ID),
 constraint RRL_TRADE_SUPPLY_TRANSFER_END_EV unique(WARE_ID,SOURCE_ID,END_EVENT_ID),
 constraint RRL_TRADE_SUPPLY_TRANSFER_ST check(STATUS in('OPEN','MISMATCH','COMPLETE','DELIVERED','DELIVERY_REJECTED','SUPERSEDED')),
 constraint RRL_TRADE_SUPPLY_TRANSFER_PC check(PART_COUNT between 1 and 1000 and PART_COUNT=trunc(PART_COUNT)),
 constraint RRL_TRADE_SUPPLY_TRANSFER_VER check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO)),
 constraint RRL_TRADE_SUPPLY_TRANSFER_HJ check(HEADER_JSON is json),
 constraint RRL_TRADE_SUPPLY_TRANSFER_RJ check(DELIVERY_RESULT is json)
);
create index RRL_TRADE_SUPPLY_TRANSFER_DOC on RRL_TRADE_SUPPLY_TRANSFER(WARE_ID,SOURCE_ID,DOCUMENT_ID,VERSION_NO);
create index RRL_TRADE_SUPPLY_TRANSFER_UPD on RRL_TRADE_SUPPLY_TRANSFER(WARE_ID,UPDATED_AT);
create table RRL_TRADE_SUPPLY_PART(
 WARE_ID number not null,SOURCE_ID varchar2(100)not null,TRANSFER_ID varchar2(100)not null,PART_NO number not null,
 EVENT_ID varchar2(100)not null,PART_HASH varchar2(64)not null,CODE_COUNT number not null,CODES_JSON clob not null,
 ACTOR varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_SUPPLY_PART_PK primary key(WARE_ID,SOURCE_ID,TRANSFER_ID,PART_NO),
 constraint RRL_TRADE_SUPPLY_PART_EV unique(WARE_ID,SOURCE_ID,EVENT_ID),
 constraint RRL_TRADE_SUPPLY_PART_FK foreign key(WARE_ID,SOURCE_ID,TRANSFER_ID)references RRL_TRADE_SUPPLY_TRANSFER(WARE_ID,SOURCE_ID,TRANSFER_ID),
 constraint RRL_TRADE_SUPPLY_PART_CJ check(CODES_JSON is json),
 constraint RRL_TRADE_SUPPLY_PART_CC check(CODE_COUNT between 1 and 10000)
);
-- A recorded part never changes: a correction is a new version/transfer, never an edit.
create or replace trigger RRL_TRADE_SUPPLY_PART_APPEND before update or delete on RRL_TRADE_SUPPLY_PART
begin raise_application_error(-20901,'SUPPLY_PART_APPEND_ONLY');end;
/
