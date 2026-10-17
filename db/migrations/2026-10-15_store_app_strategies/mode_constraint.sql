declare v_name varchar2(128);begin
 select CONSTRAINT_NAME into v_name from USER_CONSTRAINTS where TABLE_NAME='RRL_STORE_RECEIPT_POLICY'and CONSTRAINT_TYPE='C'and instr(SEARCH_CONDITION_VC,'BARCODE')>0;
 execute immediate 'alter table RRL_STORE_RECEIPT_POLICY drop constraint '||dbms_assert.simple_sql_name(v_name);
 execute immediate q'[alter table RRL_STORE_RECEIPT_POLICY add constraint RRL_STORE_RECEIPT_MODE_CK check(RECEIPT_MODE in('BARCODE','WEIGHT_PHOTO','PAPER_COUNT'))]';
end;
/
