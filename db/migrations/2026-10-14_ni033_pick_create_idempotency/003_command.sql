create or replace package RRL_PICK_PLAN_CREATE_API authid definer as
 function create_command(p_operation varchar2,p_order number,p_strategy varchar2,p_actor varchar2)return number;
 procedure assert_write(p_operation varchar2);
 function current_operation return varchar2;
 function cached_plan return number;
end;
/
create or replace package body RRL_PICK_PLAN_CREATE_API as
 g_operation varchar2(100);g_tx varchar2(100);g_hash varchar2(64);g_actor varchar2(100);g_ware number;
 function current_operation return varchar2 is begin return g_operation;end;
 function cached_plan return number is v RRL_PICK_PLAN_CREATE_OP%rowtype;begin
 if g_operation is null then return null;end if;
 begin select *into v from RRL_PICK_PLAN_CREATE_OP where OPERATION_ID=g_operation;exception when no_data_found then return null;end;
 if v.REQUEST_HASH!=g_hash or v.ACTOR!=g_actor or v.WARE_ID!=g_ware then raise_application_error(-20886,'PICK_CREATE_OPERATION_CONTENT_CONFLICT');end if;
 if v.PICK_PLAN_ID is null then raise_application_error(-20886,'PICK_CREATE_SAVED_RESULT_REQUIRED');end if;return v.PICK_PLAN_ID;end;
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
  select count(*)into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='ACTIVE';
  if n!=1 then raise_application_error(-20860,'PICK_CREATE_ACTIVE_REQUIRED');end if;
  inserted:=false;
  g_operation:=p_operation;g_hash:=request_hash;g_actor:=p_actor;g_ware:=ware_no;
  plan_no:=RRL_PICKING_API.create_plan(p_order,strategy_value,p_actor);inserted:=true;
  select count(*)into n from RRL_PICK_PLAN_CREATE_OP where OPERATION_ID=p_operation;
  if n=0 then
   g_tx:=dbms_transaction.local_transaction_id(false);
   insert into RRL_PICK_PLAN_CREATE_OP(OPERATION_ID,REQUEST_HASH,ACTOR,CUSTOMER_ORDER_ID,WARE_ID,PLAN_STRATEGY,PICK_PLAN_ID)
    values(p_operation,request_hash,p_actor,p_order,ware_no,strategy_value,plan_no);
  end if;
  g_operation:=null;g_tx:=null;
  return plan_no;
 exception when others then
  g_operation:=null;g_tx:=null;
  if inserted then rollback to rrl_pick_plan_begin;end if;
  raise;
 end;
end;
/
