create or replace trigger RRL_TARE_DORIGIN_GUARD before insert or update or delete on RRL_TARE_DAMAGE_ORIGIN for each row
begin
 if updating or deleting then raise_application_error(-20863,'TARE_DAMAGE_TRACE_HISTORY_IMMUTABLE');end if;
 RRL_TARE_DAMAGE_TRACE.assert_internal;
 if :new.DAMAGE_OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_DAMAGE_TRACE_OPERATION_REQUIRED');end if;
end;
/
create or replace trigger RRL_TARE_DOFFER_GUARD before insert or update or delete on RRL_TARE_DAMAGE_OFFER for each row
begin
 if updating or deleting then raise_application_error(-20863,'TARE_DAMAGE_TRACE_HISTORY_IMMUTABLE');end if;
 RRL_TARE_DAMAGE_TRACE.assert_internal;
 if :new.OFFER_OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_DAMAGE_TRACE_OPERATION_REQUIRED');end if;
end;
/
create or replace trigger RRL_TARE_DMOVE_GUARD before insert or update or delete on RRL_TARE_DAMAGE_MOVE for each row
begin
 if updating or deleting then raise_application_error(-20863,'TARE_DAMAGE_TRACE_HISTORY_IMMUTABLE');end if;
 RRL_TARE_DAMAGE_TRACE.assert_internal;
 if :new.ACCEPT_OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_DAMAGE_TRACE_OPERATION_REQUIRED');end if;
end;
/
create or replace trigger RRL_TARE_DPOSITION_GUARD before insert or update or delete on RRL_TARE_DAMAGE_POSITION for each row
begin
 if deleting then raise_application_error(-20863,'TARE_DAMAGE_POSITION_DELETE_FORBIDDEN');end if;
 RRL_TARE_DAMAGE_TRACE.assert_internal;
 if :new.LAST_OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_DAMAGE_TRACE_OPERATION_REQUIRED');end if;
 if inserting and :new.VERSION_NO!=1 or updating and(:new.DAMAGE_OPERATION_ID!=:old.DAMAGE_OPERATION_ID or :new.BALANCE_KEY!=:old.BALANCE_KEY or :new.VERSION_NO!=:old.VERSION_NO+1)
 then raise_application_error(-20863,'TARE_DAMAGE_POSITION_IDENTITY_VERSION');end if;
end;
/
