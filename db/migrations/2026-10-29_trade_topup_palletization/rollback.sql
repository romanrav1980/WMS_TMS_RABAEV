whenever sqlerror exit failure rollback
declare n number;begin
 select count(*) into n from RRL_TRADE_TOPUP_PALLETIZATION;
 if n<>0 then raise_application_error(-20995,'TRADE_TOPUP_PALLETIZATION_ROWS_EXIST');end if;
end;
/
drop table RRL_TRADE_TOPUP_PALLETIZATION cascade constraints
/