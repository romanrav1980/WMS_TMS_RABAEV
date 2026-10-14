declare n number;begin select count(*)into n from RRL_INTERWARE_PLACEMENT p join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=p.RECEIPT_OPERATION_ID join RRL_INTERWARE_UNIT_MANIFEST m on m.PLAN_OPERATION_ID=r.PLAN_OPERATION_ID;if n>0 then raise_application_error(-20863,'MARKED_PLACEMENT_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_interware_put.sql
@@000_before_rrl_stock_posting_api.sql
@@003_recompile.sql
