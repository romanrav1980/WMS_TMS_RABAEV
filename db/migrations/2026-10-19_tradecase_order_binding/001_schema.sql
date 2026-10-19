create table RRL_TRADE_ORDER_LINK(
 CUSTOMER_ORDER_ID number not null,WARE_ID number not null,EXTERNAL_ID varchar2(100)not null,
 DOCUMENT_VERSION number not null,RECIPIENT_ID varchar2(100)not null,RECIPIENT_VERSION number not null,
 CREATED_BY varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_ORDER_LINK_PK primary key(CUSTOMER_ORDER_ID),
 constraint RRL_TRADE_ORDER_LINK_UK unique(WARE_ID,EXTERNAL_ID),
 constraint RRL_TRADE_ORDER_NATIVE_FK foreign key(CUSTOMER_ORDER_ID)references RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID),
 constraint RRL_TRADE_ORDER_SITE_FK foreign key(WARE_ID)references RRL_TRADE_SITE(WARE_ID)
);
create table RRL_TRADE_ORDER_LINE(
 CUSTOMER_ORDER_ROW_ID number not null,CUSTOMER_ORDER_ID number not null,EXTERNAL_LINE_ID varchar2(100)not null,
 SKU_ID varchar2(100)not null,SKU_VERSION number not null,SOURCE_OWNER_ID varchar2(100)not null,TARGET_OWNER_ID varchar2(100)not null,
 MRC number(12,2)not null,MIN_EXPIRY_DATE date not null,BUYOUT_MODE varchar2(20)not null,
 constraint RRL_TRADE_ORDER_LINE_PK primary key(CUSTOMER_ORDER_ROW_ID),
 constraint RRL_TRADE_ORDER_LINE_UK unique(CUSTOMER_ORDER_ID,EXTERNAL_LINE_ID),
 constraint RRL_TRADE_LINE_NATIVE_FK foreign key(CUSTOMER_ORDER_ROW_ID)references RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID),
 constraint RRL_TRADE_LINE_LINK_FK foreign key(CUSTOMER_ORDER_ID)references RRL_TRADE_ORDER_LINK(CUSTOMER_ORDER_ID),
 constraint RRL_TRADE_LINE_MODE check(BUYOUT_MODE in('BEFORE_PICK','AFTER_PICK','IN_TRANSIT'))
);
create table RRL_TRADE_ORDER_COMMAND(
 OPERATION_ID varchar2(100)not null,WARE_ID number not null,ACTOR varchar2(50)not null,
 PAYLOAD_HASH varchar2(64)not null,RESULT_JSON clob not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_TRADE_ORDER_COMMAND_PK primary key(OPERATION_ID),
 constraint RRL_TRADE_ORDER_COMMAND_JSON check(RESULT_JSON is json)
);
