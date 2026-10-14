begin
 execute immediate q'[create table RRL_PICK_PLAN_CREATE_OP(
  OPERATION_ID varchar2(100) not null,
  REQUEST_HASH varchar2(64) not null,
  ACTOR varchar2(100) not null,
  CUSTOMER_ORDER_ID number not null,
  WARE_ID number not null,
  PLAN_STRATEGY varchar2(30) not null,
  PICK_PLAN_ID number,
  CREATED_AT timestamp with time zone default systimestamp not null,
  constraint RRL_PICK_CREATE_OP_PK primary key(OPERATION_ID),
  constraint RRL_PICK_CREATE_ORDER_FK foreign key(CUSTOMER_ORDER_ID) references RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID),
  constraint RRL_PICK_CREATE_PLAN_FK foreign key(PICK_PLAN_ID) references RRL_PICK_PLAN(PICK_PLAN_ID)
 )]';
end;
/
