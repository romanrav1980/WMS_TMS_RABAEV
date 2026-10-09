declare n number;begin select count(*) into n from RRL_STOCK_OPERATION;if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
@@147_rrl_accept_order2_rollback.sql
@@147_rrl_accept_order2_2_rollback.sql
@@147_rrl_accept_order2_3_rollback.sql
@@147_rrl_accept_order3_rollback.sql
@@147_rrl_otkat_order2_rollback.sql
@@014b_recompile.sql
