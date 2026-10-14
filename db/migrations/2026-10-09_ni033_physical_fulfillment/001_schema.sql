declare
 procedure add_column(p_name varchar2,p_type varchar2) is n number;begin
  select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CUSTOMER_ORDER_FULFILLMENT' and COLUMN_NAME=p_name;
  if n=0 then execute immediate 'alter table RRL_CUSTOMER_ORDER_FULFILLMENT add '||p_name||' '||p_type;end if;
 end;
begin
 add_column('FACT_COMPOSITION_JSON','clob');
 add_column('FACT_UOM','varchar2(20)');
 add_column('PICKED_CASE_TASK_ID','number');
 add_column('PICKED_CONTENT_VERSION','number');
 add_column('PICKED_AT','timestamp');
 add_column('PICKED_BY','varchar2(100)');
end;
/
