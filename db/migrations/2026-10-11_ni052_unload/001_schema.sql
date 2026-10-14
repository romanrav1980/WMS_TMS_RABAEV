create table RRL_TT_UNLOAD_FACT(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100)not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 TT_ID number not null references RRL_TRANSPORT_TASK(ID),
 CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 WARE_ID number not null,
 CELL_CODE varchar2(60)not null,
 COMPOSITION_JSON clob not null check(COMPOSITION_JSON is json),
 REASON varchar2(1000)not null,
 CREATED_BY varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null);
