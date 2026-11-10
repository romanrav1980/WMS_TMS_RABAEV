whenever sqlerror exit failure rollback
declare n number;begin
 select count(*) into n from user_tables where table_name='RRL_TRADE_TOPUP_PALLETIZATION';
 if n<>1 then raise_application_error(-20993,'TRADE_TOPUP_PALLETIZATION_MISSING');end if;
 select count(*) into n from user_constraints where table_name='RRL_TRADE_TOPUP_PALLETIZATION' and constraint_type='P';
 if n<>1 then raise_application_error(-20994,'TRADE_TOPUP_PALLETIZATION_PRIMARY_KEY_MISSING');end if;
end;
/