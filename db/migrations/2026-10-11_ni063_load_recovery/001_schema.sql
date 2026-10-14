create table RRL_TARE_LOAD_RECOVERY(
 OPERATION_ID varchar2(100)primary key references RRL_TARE_BOOK(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100)not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 ORIGINAL_BOOK_OPERATION_ID varchar2(100)not null unique references RRL_TARE_BOOK(OPERATION_ID),
 RETURN_OFFER_OPERATION_ID varchar2(100)not null unique references RRL_TARE_OFFER(OPERATION_ID),
 RETURN_ACCEPT_OPERATION_ID varchar2(100)not null unique references RRL_TARE_ACCEPT(OPERATION_ID),
 WARE_ID number not null,PALLET_TYPE_ID number not null references RRL_PALLET_TYPE(PALLET_TYPE_ID),
 CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 CREATED_BY varchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null);
