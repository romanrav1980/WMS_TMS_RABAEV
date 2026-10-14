declare n number;begin select count(*)into n from RRL_LOGISTICS_EXPENSE where CORRECTION_OF_OP is not null;if n>0 then raise_application_error(-20808,'LOGISTICS_CORRECTION_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@../2026-10-10_ni071_expenses/002_guards.sql
