declare n number;begin select count(*)into n from RRL_IW_RECOVERY_PUT_PLAN;if n>0 then raise_application_error(-20878,'RETAINED_RECOVERY_TASKS_REQUIRE_FORWARD_FIX');end if;end;
/
@@000_before_rrl_stock_task_plan.sql
@@000_before_rrl_stock_task_core.sql
@@000_before_rrl_stock_task_domain.sql
@@../2026-10-11_ni061_marked_partial/005_put_body.sql
@@../2026-10-11_ni061_loss_recovery/019_receiving_root_body.sql
drop trigger RRL_IW_RECOVERY_PLACE_GUARD;
drop trigger RRL_IW_RECOVERY_PUT_GUARD;
drop package RRL_STOCK_IW_RECOVERY_PUT;
drop package RRL_STOCK_IW_PUT_CELL;
drop table RRL_IW_RECOVERY_PLACEMENT;
drop table RRL_IW_RECOVERY_PUT_PLAN;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
