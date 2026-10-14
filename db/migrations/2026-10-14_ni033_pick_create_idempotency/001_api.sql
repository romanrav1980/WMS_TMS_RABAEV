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
create or replace package RRL_PICK_PLAN_CREATE_API authid definer as
 function create_command(p_operation varchar2,p_order number,p_strategy varchar2,p_actor varchar2)return number;
 procedure assert_write(p_operation varchar2);
end;
/
create or replace package body RRL_PICK_PLAN_CREATE_API as
 g_operation varchar2(100);g_tx varchar2(100);
 procedure assert_write(p_operation varchar2)is
 begin
  if g_operation is null or g_operation!=p_operation or g_tx is null or g_tx!=dbms_transaction.local_transaction_id(false)then
   raise_application_error(-20863,'PICK_CREATE_ONLY_COMMAND_WRITER');end if;
 end;
 function create_command(p_operation varchar2,p_order number,p_strategy varchar2,p_actor varchar2)return number is
  strategy_value varchar2(30):=upper(trim(nvl(p_strategy,'FEFO')));ware_no number;plan_no number;request_hash varchar2(64);
  cached RRL_PICK_PLAN_CREATE_OP%rowtype;n number;inserted boolean:=false;
  function saved_result return number is
  begin
   select *into cached from RRL_PICK_PLAN_CREATE_OP where OPERATION_ID=p_operation;
   if cached.REQUEST_HASH!=request_hash or cached.ACTOR!=p_actor then raise_application_error(-20886,'PICK_CREATE_OPERATION_CONTENT_CONFLICT');end if;
   if cached.WARE_ID!=ware_no then raise_application_error(-20886,'PICK_CREATE_ORDER_WARE_CHANGED');end if;
   if cached.PICK_PLAN_ID is null then raise_application_error(-20886,'PICK_CREATE_SAVED_RESULT_REQUIRED');end if;
   return cached.PICK_PLAN_ID;
  end;
 begin
  if p_operation is null or length(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_order is null or p_order<1 or p_order!=trunc(p_order)
   or strategy_value not in('FEFO','FIFO')or p_actor is null then raise_application_error(-20886,'PICK_CREATE_EXPLICIT_IDENTITY_REQUIRED');end if;
  begin select WARE_ID into ware_no from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=p_order;
  exception when no_data_found then raise_application_error(-20886,'PICK_ORDER_IDENTITY_MISSING');end;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'pick_plan_create')=1
   and(WARE_ID=ware_no or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 or ware_no is null then raise_application_error(-20882,'PICK_CREATE_CURRENT_WARE_ACTOR_REQUIRED');end if;
  request_hash:=rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(to_char(p_order,'TM9')||':'||strategy_value||':'||p_actor,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
  select count(*)into n from RRL_PICK_PLAN_CREATE_OP where OPERATION_ID=p_operation;
  if n=1 then return saved_result;end if;
  savepoint pick_create_command;
  g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(true);
  begin
   insert into RRL_PICK_PLAN_CREATE_OP(OPERATION_ID,REQUEST_HASH,ACTOR,CUSTOMER_ORDER_ID,WARE_ID,PLAN_STRATEGY)
    values(p_operation,request_hash,p_actor,p_order,ware_no,strategy_value);
   inserted:=true;
  exception when dup_val_on_index then g_operation:=null;g_tx:=null;return saved_result;end;
  plan_no:=RRL_PICKING_API.create_plan(p_order,strategy_value,p_actor);
  update RRL_PICK_PLAN_CREATE_OP set PICK_PLAN_ID=plan_no where OPERATION_ID=p_operation;
  g_operation:=null;g_tx:=null;
  return plan_no;
 exception when others then
  g_operation:=null;g_tx:=null;
  if inserted then rollback to pick_create_command;end if;
  raise;
 end;
end;
/
create or replace trigger RRL_PICK_CREATE_OP_GUARD before insert or update or delete on RRL_PICK_PLAN_CREATE_OP for each row
begin
 if deleting then raise_application_error(-20863,'PICK_CREATE_HISTORY_IMMUTABLE');end if;
 if updating and(:old.PICK_PLAN_ID is not null or :new.OPERATION_ID!=:old.OPERATION_ID or :new.REQUEST_HASH!=:old.REQUEST_HASH or :new.ACTOR!=:old.ACTOR
  or :new.CUSTOMER_ORDER_ID!=:old.CUSTOMER_ORDER_ID or :new.WARE_ID!=:old.WARE_ID or :new.PLAN_STRATEGY!=:old.PLAN_STRATEGY
  or :new.CREATED_AT!=:old.CREATED_AT or :new.PICK_PLAN_ID is null)then raise_application_error(-20863,'PICK_CREATE_HISTORY_IMMUTABLE');end if;
 RRL_PICK_PLAN_CREATE_API.assert_write(:new.OPERATION_ID);
end;
/
