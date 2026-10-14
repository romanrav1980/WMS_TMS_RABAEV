create or replace trigger RRL_DISPOSAL_REQUEST_GUARD before insert or update or delete on RRL_RETURN_DISPOSAL_REQUEST for each row
declare n number;
begin
 if not inserting then raise_application_error(-20863,'RETURN_DISPOSAL_REQUEST_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 select count(*)into n from RRL_STORE_RETURN_RECEIPT r join RUSERS u on u.ID=:new.ACTOR and nvl(u.DELETED,0)=0
 where r.OPERATION_ID=:new.RECEIPT_OPERATION_ID and r.DISPOSITION='DISPOSAL'
 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'warehouse_return_dispatch')=1;
 if n!=1 then raise_application_error(-20882,'RETURN_DISPOSAL_BOUND_REPORTER_REQUIRED');end if;
end;
/
create or replace trigger RRL_DISPOSAL_FACT_GUARD before insert or update or delete on RRL_RETURN_DISPOSAL_FACT for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;
begin
 if not inserting then raise_application_error(-20863,'RETURN_DISPOSAL_FACT_IMMUTABLE');end if;
 if op is null or :new.OPERATION_ID!=op or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'RETURN_DISPOSAL_ROOT_REQUIRED');end if;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=op and COMMAND_TYPE='STORE_RETURN_DISPOSE' and STATE='IN_FLIGHT';if n!=1 then raise_application_error(-20863,'RETURN_DISPOSAL_EXPLICIT_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RETURN_DISPOSAL_FACT',op));
end;
/
