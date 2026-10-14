declare n number;begin select count(*)into n from RRL_SKU_RECEIPT_POLICY where STACK_STAGE!='MAIN';if n>0 then raise_application_error(-20863,'STACK_CONFIG_HISTORY_RETAIN_FORWARD_REPAIR');end if;select count(*)into n from RRL_CASE_PICK_LINE where STACK_STAGE!='MAIN';if n>0 then raise_application_error(-20863,'STACK_ISSUED_HISTORY_RETAIN_FORWARD_REPAIR');end if;end;
/
@@000_before_route.sql
drop trigger RRL_CASE_STACK_STAGE_CAPTURE;
alter table RRL_CASE_PICK_LINE drop constraint RRL_CASE_STACK_STAGE_CK;
alter table RRL_CASE_PICK_LINE drop(STACK_STAGE,STACK_POLICY_VERSION);
alter table RRL_SKU_RECEIPT_POLICY drop constraint RRL_SKU_STACK_STAGE_CK;
alter table RRL_SKU_RECEIPT_POLICY drop column STACK_STAGE;
