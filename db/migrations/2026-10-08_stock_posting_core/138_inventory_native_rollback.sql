declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/

@@137_inventory_2_rollback.sql
@@137_inventory_3_rollback.sql
@@137_inventory_4_rollback.sql
@@014b_recompile.sql
