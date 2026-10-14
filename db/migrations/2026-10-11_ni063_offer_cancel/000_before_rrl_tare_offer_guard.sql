create or replace trigger RRL_TARE_OFFER_GUARD before insert or update or delete on RRL_TARE_OFFER for each row
begin
 if not inserting then raise_application_error(-20863,'TARE_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_ROOT_OPERATION_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_OFFER',:new.OPERATION_ID,'TARE_OFFER');
end;
/
