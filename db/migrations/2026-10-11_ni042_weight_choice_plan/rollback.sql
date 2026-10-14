declare n number;begin select count(*)into n from RRL_PICK_WEIGHT_CHOICE where STATUS='USED';if n>0 then raise_application_error(-20863,'WEIGHT_PLAN_RETAIN_BOUND_HISTORY_FORWARD_REPAIR');end if;end;
/
@@000_before_picking.sql
@@000_before_guard.sql
@@000_before_choice.sql
drop context RRL_WEIGHT_PLAN_CTX;
drop package RRL_WEIGHT_PLAN_BIND;
drop index RRL_WEIGHT_CHOICE_ORDER_I;
