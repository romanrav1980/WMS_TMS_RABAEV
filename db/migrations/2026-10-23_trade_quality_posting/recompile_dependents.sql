-- Replacing EFFECT_CORE spec or changing CASE columns invalidates these unchanged dependents.
begin
 for pass in 1..2 loop
  for x in(select OBJECT_NAME from USER_OBJECTS where STATUS='INVALID'and OBJECT_TYPE='PACKAGE BODY'
   and OBJECT_NAME in('RRL_STOCK_MES_MOVEMENT_CORE','RRL_STOCK_RETURN_DISPOSE','RRL_STOCK_SHIPPING_CORE',
    'RRL_TRADE_QUALITY_CASE_API','RRL_STOCK_EFFECT_CORE','RRL_STOCK_QUALITY_WRITEOFF','RRL_STOCK_POSTING_API'))loop
   execute immediate 'alter package '||dbms_assert.simple_sql_name(x.OBJECT_NAME)||' compile body';
  end loop;
 end loop;
end;
/