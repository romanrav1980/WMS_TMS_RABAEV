declare n number;
 procedure add_col(p_name varchar2,p_def varchar2) is v number;
 begin select count(*) into v from user_tab_columns where TABLE_NAME='RRL_MES_MOVEMENT' and COLUMN_NAME=p_name;
  if v=0 then execute immediate 'alter table RRL_MES_MOVEMENT add('||p_def||')';end if;
 end;
begin
 select count(*) into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='PREPARED';
 if n!=1 then raise_application_error(-20808,'MES_BINDING_INSTALL_REQUIRES_PREPARED');end if;
 add_col('SOURCE_UID_PALLET','SOURCE_UID_PALLET varchar2(200)');
 add_col('TARGET_UID_PALLET','TARGET_UID_PALLET varchar2(200)');
 add_col('STOCK_OPERATION_ID','STOCK_OPERATION_ID varchar2(100)');
 add_col('POSTED_BASE_QTY','POSTED_BASE_QTY number');
 add_col('STOCK_BASE_UOM','STOCK_BASE_UOM varchar2(20)');
end;
/
