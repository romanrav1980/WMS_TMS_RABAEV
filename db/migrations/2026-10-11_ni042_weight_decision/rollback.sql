declare n number;begin select count(*)into n from RRL_CASE_PICK_SHORT where WEIGHT_DECISION_OPERATION is not null;if n>0 then raise_application_error(-20863,'WEIGHT_DECISION_RETAIN_HISTORY_FORWARD_REPAIR');end if;end;
/
@@000_before_short.sql
@@000_before_read.sql
drop trigger RRL_CASE_WT_DECISION_GUARD;
drop package RRL_CASE_WEIGHT_DECISION;
alter table RRL_CASE_PICK_SHORT drop constraint RRL_CASE_WT_DECISION_CK;
alter table RRL_CASE_PICK_SHORT drop(WEIGHT_POLICY_VERSION,WEIGHT_TOLERANCE_PCT,WEIGHT_ORDER_REQUESTED_KG,WEIGHT_ORDER_PICKED_KG,WEIGHT_DECISION_OPERATION);
