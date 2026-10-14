create or replace trigger RRL_RETURN_REUSE_ZONE_GUARD before insert or update of REUSE_RECEIVE_CELL,SUPPLIER_RECEIVE_CELL,DISPOSAL_RECEIVE_CELL on RRL_STORE_RETURN_WARE_POLICY for each row
declare n number;
begin
 if :new.REUSE_RECEIVE_CELL is null then return;end if;
 select count(*)into n from RRL_CELLS where CELL=:new.REUSE_RECEIVE_CELL and WARE_ID=:new.WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
 if n!=1 or :new.REUSE_RECEIVE_CELL in(:new.SUPPLIER_RECEIVE_CELL,:new.DISPOSAL_RECEIVE_CELL)then raise_application_error(-20886,'RETURN_REUSE_SEPARATE_BLOCKED_RECEIVE_ZONE_REQUIRED');end if;
end;
/
create or replace trigger RRL_RETURN_REUSE_PROOF_GUARD before insert or update or delete on RRL_RETURN_REUSE_PROOF for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if not inserting then raise_application_error(-20863,'RETURN_REUSE_PROOF_IMMUTABLE');end if;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or :new.OPERATION_ID!=op or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'RETURN_REUSE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_kind!='STORE_RETURN_RECEIVE'or v_state!='IN_FLIGHT'then raise_application_error(-20863,'RETURN_REUSE_RECEIVE_ROOT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RETURN_REUSE_PROOF',op));
end;
/
