whenever sqlerror exit failure rollback
declare n number;begin
 select count(*) into n from user_objects where object_name='RRL_TRADE_TOPUP_PALLETIZATION';
 if n<>0 then raise_application_error(-20991,'TRADE_TOPUP_PALLETIZATION_ALREADY_EXISTS');end if;
 select count(*) into n from user_objects where status='INVALID';
 if n<>0 then raise_application_error(-20992,'PREEXISTING_INVALID_OBJECTS');end if;
end;
/