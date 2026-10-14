declare n number;begin select count(*)into n from RRL_INTERWARE_ONWARD_DISPATCH d join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=d.RECEIPT_OPERATION_ID join RRL_INTERWARE_UNIT_MANIFEST m on m.PLAN_OPERATION_ID=r.PLAN_OPERATION_ID;if n>0 then raise_application_error(-20863,'MARKED_ONWARD_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_interware_next.sql
@@000_before_rrl_stock_interware_custody.sql
@@000_before_rrl_stock_posting_api.sql
@@004_recompile.sql
