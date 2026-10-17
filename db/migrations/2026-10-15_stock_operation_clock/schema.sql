create table RRL_STOCK_OP_CLOCK(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 ACTOR varchar2(50)not null,COMMAND_TYPE varchar2(80)not null,
 RECORDED_AT_UTC timestamp with time zone not null,TIME_SOURCE varchar2(40)not null,
 constraint RRL_STOCK_CLOCK_SOURCE_CK check(TIME_SOURCE='ORACLE_SYSTIMESTAMP')
);
create or replace trigger RRL_STOCK_CLOCK_GUARD before insert or update or delete on RRL_STOCK_OP_CLOCK for each row
begin
 if not inserting then raise_application_error(-20863,'STOCK_CLOCK_APPEND_ONLY');end if;
 if sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null
  or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=:new.OPERATION_ID then
  raise_application_error(-20863,'STOCK_CLOCK_NATIVE_TRANSACTION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',:new.OPERATION_ID));
 if extract(timezone_hour from :new.RECORDED_AT_UTC)!=0 or extract(timezone_minute from :new.RECORDED_AT_UTC)!=0 then
  raise_application_error(-20863,'STOCK_CLOCK_UTC_OFFSET_REQUIRED');end if;
end;
/
create or replace trigger RRL_STOCK_APPLIED_CLOCK after insert or update of STATE on RRL_STOCK_OPERATION for each row
begin
 if :new.STATE='APPLIED'and(inserting or :old.STATE is null or :old.STATE!='APPLIED')then
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=:new.OPERATION_ID then
   raise_application_error(-20863,'STOCK_CLOCK_NATIVE_APPLIED_REQUIRED');end if;
  insert into RRL_STOCK_OP_CLOCK(OPERATION_ID,ACTOR,COMMAND_TYPE,RECORDED_AT_UTC,TIME_SOURCE)
   values(:new.OPERATION_ID,:new.ACTOR,:new.COMMAND_TYPE,systimestamp at time zone 'UTC','ORACLE_SYSTIMESTAMP');
 end if;
end;
/
