declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_RECEIPT_POLICY';
 if n=0 then execute immediate q'[create table RRL_STORE_RECEIPT_POLICY(
  STORE_ADDR varchar2(255) primary key,RECEIPT_MODE varchar2(20) not null check(RECEIPT_MODE in('BARCODE','WEIGHT_PHOTO')),
  POLICY_VERSION number(19) default 1 not null check(POLICY_VERSION>0),
  CHANGED_BY varchar2(50) not null,CHANGED_AT timestamp with time zone default systimestamp not null)]';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_RECEIPT_USER';
 if n=0 then execute immediate q'[create table RRL_STORE_RECEIPT_USER(
  USER_ID varchar2(50) not null,STORE_ADDR varchar2(255) not null references RRL_STORE_RECEIPT_POLICY(STORE_ADDR),
  ASSIGNED_BY varchar2(50) not null,ASSIGNED_AT timestamp with time zone default systimestamp not null,
  constraint RRL_STORE_RECEIPT_USER_PK primary key(USER_ID,STORE_ADDR))]';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_RECEIPT_FACT';
 if n=0 then execute immediate q'[create table RRL_STORE_RECEIPT_FACT(
  OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
  LOAD_OPERATION_ID varchar2(100) not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
  STORE_ADDR varchar2(255) not null references RRL_STORE_RECEIPT_POLICY(STORE_ADDR),
  ROOT_KEY varchar2(200) not null,POLICY_VERSION number(19) not null,
  RECEIPT_STATE varchar2(30) not null check(RECEIPT_STATE in('ACCEPTED','DISCREPANCY')),
  CAMERA_CONFIRMED number(1) not null check(CAMERA_CONFIRMED=1),
  COMPOSITION_SIGNATURE varchar2(64) not null,COMPOSITION_JSON clob not null check(COMPOSITION_JSON is json),
  RECEIVED_BY varchar2(50) not null,RECEIVED_AT timestamp with time zone default systimestamp not null)]';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_RECEIPT_LINE';
 if n=0 then execute immediate q'[create table RRL_STORE_RECEIPT_LINE(
  OPERATION_ID varchar2(100) not null references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
  LINE_NO number not null,LOT_UID varchar2(200) not null,ARTICLE varchar2(160) not null,BASE_UOM varchar2(20) not null,
  SHIPPED_BASE_QTY number(27,9) not null check(SHIPPED_BASE_QTY>0),
  ACCEPTED_BASE_QTY number(27,9) not null check(ACCEPTED_BASE_QTY>=0),
  MISSING_BASE_QTY number(27,9) default 0 not null check(MISSING_BASE_QTY>=0),
  REFUSED_BASE_QTY number(27,9) default 0 not null check(REFUSED_BASE_QTY>=0),
  DAMAGED_BASE_QTY number(27,9) default 0 not null check(DAMAGED_BASE_QTY>=0),
  constraint RRL_STORE_RECEIPT_LINE_PK primary key(OPERATION_ID,LINE_NO),
  constraint RRL_STORE_RECEIPT_QTY_CK check(SHIPPED_BASE_QTY=ACCEPTED_BASE_QTY+MISSING_BASE_QTY+REFUSED_BASE_QTY+DAMAGED_BASE_QTY))]';end if;
end;
/
