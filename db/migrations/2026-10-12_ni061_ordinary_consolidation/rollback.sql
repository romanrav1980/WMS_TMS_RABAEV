declare n number;begin select count(*)into n from(select OPERATION_ID from RRL_INTERWARE_ONWARD_DISPATCH group by OPERATION_ID having count(*)>1);if n>0 then raise_application_error(-20899,'CONSOLIDATED_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_rrl_stock_hu_ship_cmd.sql
@@000_before_rrl_stock_interware_next.sql
@@000_before_rrl_interware_depart_gate.sql
alter table RRL_INTERWARE_ONWARD_DISPATCH drop constraint RRL_IW_ONWARD_DISPATCH_PK;
alter table RRL_INTERWARE_ONWARD_DISPATCH add primary key(OPERATION_ID);
@@005_recompile.sql
