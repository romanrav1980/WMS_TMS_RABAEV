declare n number;begin
 select count(*)into n from RRL_INTERWARE_SHORTAGE_UNIT;
 if n>0 then raise_application_error(-20886,'ROLLBACK_REJECTED_RETAINED_CONFIRMED_LOSS_KEYS');end if;
end;
/
@@000_before_rrl_stock_unit_guard.sql
-- Revert order projection and raw delivery panel in the same release; preserve final receipt history.
