create or replace package RRL_TARE_DAMAGE_TRACE authid definer accessible by(
 package RRL_STOCK_TARE_CMD,package RRL_STOCK_TARE_RESOLVE,package RRL_STOCK_TARE_LOSS,
 trigger RRL_TARE_DORIGIN_GUARD,trigger RRL_TARE_DPOSITION_GUARD,trigger RRL_TARE_DOFFER_GUARD,trigger RRL_TARE_DMOVE_GUARD)as
 function tracked_quantity(p_key raw)return number;
 function origin_exists(p_damage varchar2)return boolean;
 function offer_origin(p_offer varchar2)return varchar2;
 procedure check_transfer(p_damage varchar2,p_key raw,p_quantity number,p_physical number);
 procedure register_damage(p_operation varchar2,p_key raw,p_quantity number);
 procedure record_offer(p_operation varchar2,p_damage varchar2);
 procedure record_transfer(p_operation varchar2,p_damage varchar2,p_from raw,p_to raw,p_quantity number);
 procedure record_writeoff(p_operation varchar2,p_damage varchar2,p_key raw,p_quantity number);
 procedure assert_internal;
end;
/
create or replace package body RRL_TARE_DAMAGE_TRACE as
 g_writing boolean:=false;
 function tracked_quantity(p_key raw)return number is n number;
 begin select nvl(sum(QUANTITY),0)into n from RRL_TARE_DAMAGE_POSITION where BALANCE_KEY=p_key;return n;end;
 function origin_exists(p_damage varchar2)return boolean is n number;
 begin select count(*)into n from RRL_TARE_DAMAGE_ORIGIN where DAMAGE_OPERATION_ID=p_damage;return n=1;end;
 function offer_origin(p_offer varchar2)return varchar2 is result varchar2(100);
 begin select DAMAGE_OPERATION_ID into result from RRL_TARE_DAMAGE_OFFER where OFFER_OPERATION_ID=p_offer;return result;
 exception when no_data_found then return null;end;
 procedure check_transfer(p_damage varchar2,p_key raw,p_quantity number,p_physical number)is n number;
 begin
  if p_damage is null then
   if p_quantity>p_physical-tracked_quantity(p_key)-RRL_TARE_PLANNING.held_quantity(p_key)then raise_application_error(-20886,'TARE_DAMAGE_ORIGIN_REQUIRED');end if;
  else
   begin select QUANTITY into n from RRL_TARE_DAMAGE_POSITION where DAMAGE_OPERATION_ID=p_damage and BALANCE_KEY=p_key;
   exception when no_data_found then raise_application_error(-20886,'TARE_DAMAGE_CURRENT_CUSTODY_REQUIRED');end;
   if p_quantity>n then raise_application_error(-20886,'TARE_DAMAGE_CURRENT_QUANTITY_EXCEEDED');end if;
  end if;
 end;
 procedure assert_internal is op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');k varchar2(80);state varchar2(20);
 begin
  if not g_writing or op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null
   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
   then raise_application_error(-20863,'TARE_DAMAGE_TRACE_ROOT_REQUIRED');end if;
  select COMMAND_TYPE,STATE into k,state from RRL_STOCK_OPERATION where OPERATION_ID=op;
  if state!='IN_FLIGHT'or k not in('TARE_DAMAGE','TARE_WRITE_OFF','TARE_OFFER','TARE_ACCEPT')
   then raise_application_error(-20863,'TARE_DAMAGE_TRACE_COMMAND_REQUIRED');end if;
 end;
 procedure register_damage(p_operation varchar2,p_key raw,p_quantity number)is
 begin
  RRL_TARE_ASSERT_WRITE('RRL_TARE_RESOLUTION',p_operation,'TARE_DAMAGE');
  g_writing:=true;
  insert into RRL_TARE_DAMAGE_ORIGIN(DAMAGE_OPERATION_ID,ORIGIN_BALANCE_KEY,QUANTITY)values(p_operation,p_key,p_quantity);
  insert into RRL_TARE_DAMAGE_POSITION(DAMAGE_OPERATION_ID,BALANCE_KEY,QUANTITY,VERSION_NO,LAST_OPERATION_ID)
   values(p_operation,p_key,p_quantity,1,p_operation);
  g_writing:=false;
 exception when others then g_writing:=false;raise;end;
 procedure record_offer(p_operation varchar2,p_damage varchar2)is
 begin
  if p_damage is null then return;end if;
  RRL_TARE_ASSERT_WRITE('RRL_TARE_OFFER',p_operation,'TARE_OFFER');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_RESOLUTION',p_damage));
  g_writing:=true;
  insert into RRL_TARE_DAMAGE_OFFER(OFFER_OPERATION_ID,DAMAGE_OPERATION_ID)values(p_operation,p_damage);
  g_writing:=false;
 exception when others then g_writing:=false;raise;end;
 procedure record_transfer(p_operation varchar2,p_damage varchar2,p_from raw,p_to raw,p_quantity number)is
 begin
  if p_damage is null then return;end if;
  RRL_TARE_ASSERT_WRITE('RRL_TARE_ACCEPT',p_operation,'TARE_ACCEPT');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_RESOLUTION',p_damage));
  g_writing:=true;
  update RRL_TARE_DAMAGE_POSITION set QUANTITY=QUANTITY-p_quantity,VERSION_NO=VERSION_NO+1,LAST_OPERATION_ID=p_operation
   where DAMAGE_OPERATION_ID=p_damage and BALANCE_KEY=p_from and QUANTITY>=p_quantity;
  if sql%rowcount!=1 then raise_application_error(-20886,'TARE_DAMAGE_CURRENT_QUANTITY_EXCEEDED');end if;
  merge into RRL_TARE_DAMAGE_POSITION p using(select p_damage D,p_to K from dual)s
   on(p.DAMAGE_OPERATION_ID=s.D and p.BALANCE_KEY=s.K)
   when matched then update set QUANTITY=QUANTITY+p_quantity,VERSION_NO=VERSION_NO+1,LAST_OPERATION_ID=p_operation
   when not matched then insert(DAMAGE_OPERATION_ID,BALANCE_KEY,QUANTITY,VERSION_NO,LAST_OPERATION_ID)values(p_damage,p_to,p_quantity,1,p_operation);
  insert into RRL_TARE_DAMAGE_MOVE(ACCEPT_OPERATION_ID,DAMAGE_OPERATION_ID,FROM_BALANCE_KEY,TO_BALANCE_KEY,QUANTITY)
   values(p_operation,p_damage,p_from,p_to,p_quantity);
  g_writing:=false;
 exception when others then g_writing:=false;raise;end;
 procedure record_writeoff(p_operation varchar2,p_damage varchar2,p_key raw,p_quantity number)is
 begin
  if not origin_exists(p_damage)then return;end if;
  RRL_TARE_ASSERT_WRITE('RRL_TARE_RESOLUTION',p_operation,'TARE_WRITE_OFF');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_RESOLUTION',p_damage));
  g_writing:=true;
  update RRL_TARE_DAMAGE_POSITION set QUANTITY=QUANTITY-p_quantity,VERSION_NO=VERSION_NO+1,LAST_OPERATION_ID=p_operation
   where DAMAGE_OPERATION_ID=p_damage and BALANCE_KEY=p_key and QUANTITY>=p_quantity;
  if sql%rowcount!=1 then raise_application_error(-20886,'TARE_DAMAGE_CURRENT_QUANTITY_EXCEEDED');end if;
  g_writing:=false;
 exception when others then g_writing:=false;raise;end;
end;
/
