create table RRL_TRADE_STOCK_ATTR (
 PHYSICAL_UNIT_KEY varchar2(64) not null, RECEIPT_UID varchar2(200) not null, UNIT_ID varchar2(100) not null,
 CAPTURE_WARE_ID number not null references RRL_TRADE_SITE(WARE_ID), SUPPLY_ID varchar2(100) not null,
 SUPPLY_VERSION number not null, SKU_ID varchar2(100) not null, OWNER_ID varchar2(100) not null,
 MRC number(12,2) not null, EXPIRY_DATE date not null, SUPPLIER_BATCH varchar2(100) not null,
 MARK_STATE varchar2(12) default 'PENDING' not null, VERSION_NO number default 1 not null,
 CREATED_BY varchar2(50) not null, CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_ATTR_PK primary key(PHYSICAL_UNIT_KEY),
 constraint RRL_TRADE_ATTR_UNIT_FK foreign key(RECEIPT_UID,UNIT_ID) references RRL_WMS_RECEIPT_UNIT(UID_PALLET,UNIT_ID),
 constraint RRL_TRADE_ATTR_MARK check(MARK_STATE in('PENDING','VALID','REJECTED')),
 constraint RRL_TRADE_ATTR_PRICE check(MRC>=0)
);
create index RRL_TRADE_ATTR_SOURCE_IX on RRL_TRADE_STOCK_ATTR(CAPTURE_WARE_ID,SUPPLY_ID);
create table RRL_TRADE_CELL_POLICY (
 CELL varchar2(60) not null, WARE_ID number not null references RRL_TRADE_SITE(WARE_ID),
 ZONE_KIND varchar2(12) not null, OWNER_ID varchar2(100), VERSION_NO number not null, REASON varchar2(2000) not null,
 CHANGED_BY varchar2(50) not null, CHANGED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_CELL_PK primary key(CELL),
 constraint RRL_TRADE_CELL_ZONE check(ZONE_KIND in('RECEIVE','STORAGE','PICK','WAIT','EXPEDITION','SORT','DEFECT')),
 constraint RRL_TRADE_PICK_OWNER check(ZONE_KIND<>'PICK' or OWNER_ID is not null)
);
create table RRL_TRADE_OWNER_GRANT (
 USERNAME nvarchar2(50) not null, WARE_ID number not null references RRL_TRADE_SITE(WARE_ID), OWNER_ID varchar2(100) not null,
 CAN_VIEW number(1) not null, CAN_OPERATE number(1) not null, VERSION_NO number not null,
 REASON varchar2(2000) not null, CHANGED_BY varchar2(50) not null,
 constraint RRL_TRADE_OWNER_GRANT_PK primary key(USERNAME,WARE_ID,OWNER_ID),
 constraint RRL_TRADE_OWNER_FLAGS check(CAN_VIEW in(0,1) and CAN_OPERATE in(0,1) and CAN_OPERATE<=CAN_VIEW)
);
create table RRL_TRADE_STOCK_COMMAND (
 OPERATION_ID varchar2(100) not null, WARE_ID number not null, ACTOR varchar2(50) not null,
 PAYLOAD_HASH varchar2(64) not null, RESULT_JSON clob not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_STOCK_CMD_PK primary key(OPERATION_ID),
 constraint RRL_TRADE_STOCK_CMD_JSON check(RESULT_JSON is json)
);
alter table RRL_TRADE_DOCUMENT drop constraint RRL_TRADE_DOC_KIND;
alter table RRL_TRADE_DOCUMENT add constraint RRL_TRADE_DOC_KIND check(ENTITY_TYPE in('OWNER','SKU','RECIPIENT','ORDER','TRIP','SUPPLY'));