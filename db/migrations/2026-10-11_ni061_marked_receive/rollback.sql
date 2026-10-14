declare n number;begin select count(*)into n from RRL_INTERWARE_RECEIPT r join RRL_INTERWARE_UNIT_MANIFEST u on u.PLAN_OPERATION_ID=r.PLAN_OPERATION_ID;if n>0 then raise_application_error(-20863,'FORWARD_REPAIR_AFTER_MARKED_RECEIPT_REQUIRED');end if;end;
/
@@000_before_rrl_stock_unit_core.sql
@@000_before_rrl_stock_interware_rec.sql
@@000_before_rrl_stock_posting_api.sql
@@005_recompile.sql
