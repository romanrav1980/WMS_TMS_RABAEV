declare n number;begin select(select count(*)from RRL_INTERWARE_PUT_PLAN)+(select count(*)from RRL_INTERWARE_PLACEMENT)into n from dual;if n!=0 then raise_application_error(-20899,'INTERWARE120_FACTS_FORWARD_CORRECTION_REQUIRED');end if;end;
/
@@../2026-10-08_stock_posting_core/436_before120_root.sql
@@../2026-10-08_stock_posting_core/433_before120_task_plan.sql
@@../2026-10-08_stock_posting_core/434_before120_task_core.sql
@@../2026-10-08_stock_posting_core/435_before120_task_domain.sql
drop table RRL_INTERWARE_PLACEMENT;
drop table RRL_INTERWARE_PUT_PLAN;
drop package RRL_STOCK_INTERWARE_PUT;
