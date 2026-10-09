declare n number;
begin
 select count(*) into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='PREPARED';
 if n!=1 then raise_application_error(-20808,'RECEIPT_SCHEMA_REQUIRES_PREPARED');end if;
 select count(*) into n from user_tab_columns where TABLE_NAME='RRL_SAP_PALLET_RECEIPT' and COLUMN_NAME='POSTED_BASE_QTY';
 if n=0 then execute immediate 'alter table RRL_SAP_PALLET_RECEIPT add(POSTED_BASE_QTY number,STOCK_BASE_UOM varchar2(20),STOCK_OPERATION_ID varchar2(100))';end if;
 select count(*) into n from user_indexes where INDEX_NAME='RRL_SAP_RECEIPT_LINE_IX';
 if n=0 then execute immediate 'create index RRL_SAP_RECEIPT_LINE_IX on RRL_SAP_PALLET_RECEIPT(ORDER_ID,LINE_NUMBER)';end if;
 select count(*) into n from RRL_STOCK_POLICY_GUARD where POLICY_KEY=RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE');
 if n=0 then
  insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)
   select RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD;
 end if;
end;
/
