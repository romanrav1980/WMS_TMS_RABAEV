declare n number;begin select count(*)into n from RRL_STORE_RECEIPT_FACT f join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID
 where exists(select 1 from json_table(l.COMPOSITION_JSON,'$.nodes[*]'columns(NODE_KIND varchar2(20)path '$.kind'))where NODE_KIND='CASE')
 and exists(select 1 from RRL_STORE_RECEIPT_UNIT u where u.OPERATION_ID=f.OPERATION_ID);
 if n>0 then raise_application_error(-20899,'MARKED_CASE_RECEIPT_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_units.sql
@@000_before_store.sql
