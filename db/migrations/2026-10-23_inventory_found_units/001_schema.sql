-- C-0166: which marked units an inventory count wrote off, and which of exactly those were found again (append-only).
create table RRL_INVENTORY_LOSS_UNIT(
 PHYSICAL_UNIT_KEY varchar2(64)not null,LOSS_OPERATION_ID varchar2(100)not null,REVISION_ID number not null,UID_PALLET varchar2(200)not null,
 CELL varchar2(60)not null,UNIT_VERSION number not null,ACTOR varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_INV_LOSS_UNIT_PK primary key(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID),
 constraint RRL_INV_LOSS_UNIT_KEY_FK foreign key(PHYSICAL_UNIT_KEY)references RRL_WMS_RECEIPT_UNIT(PHYSICAL_UNIT_KEY),
 constraint RRL_INV_LOSS_UNIT_OP_FK foreign key(LOSS_OPERATION_ID)references RRL_STOCK_OPERATION(OPERATION_ID)
);
create index RRL_INV_LOSS_UNIT_LOT_IX on RRL_INVENTORY_LOSS_UNIT(UID_PALLET,CELL);
create table RRL_INVENTORY_FOUND_UNIT(
 PHYSICAL_UNIT_KEY varchar2(64)not null,LOSS_OPERATION_ID varchar2(100)not null,FOUND_OPERATION_ID varchar2(100)not null,REVISION_ID number not null,
 UID_PALLET varchar2(200)not null,CELL varchar2(60)not null,ACTOR varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_INV_FOUND_UNIT_PK primary key(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID),
 constraint RRL_INV_FOUND_UNIT_LOSS_FK foreign key(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID)references RRL_INVENTORY_LOSS_UNIT(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID),
 constraint RRL_INV_FOUND_UNIT_OP_FK foreign key(FOUND_OPERATION_ID)references RRL_STOCK_OPERATION(OPERATION_ID)
);
create or replace trigger RRL_INV_LOSS_UNIT_APPEND before update or delete on RRL_INVENTORY_LOSS_UNIT
begin raise_application_error(-20863,'INVENTORY_LOSS_HISTORY_APPEND_ONLY');end;
/
create or replace trigger RRL_INV_FOUND_UNIT_APPEND before update or delete on RRL_INVENTORY_FOUND_UNIT
begin raise_application_error(-20863,'INVENTORY_FOUND_HISTORY_APPEND_ONLY');end;
/
