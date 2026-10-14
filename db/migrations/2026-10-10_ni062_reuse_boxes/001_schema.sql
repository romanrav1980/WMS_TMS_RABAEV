declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RETURN_WARE_POLICY' and COLUMN_NAME='REUSE_RECEIVE_CELL';
 if n=0 then execute immediate 'alter table RRL_STORE_RETURN_WARE_POLICY add(REUSE_RECEIVE_CELL varchar2(60 byte))';end if;
 for r in(select CONSTRAINT_NAME from USER_CONSTRAINTS where TABLE_NAME='RRL_STORE_RETURN_RECEIPT' and CONSTRAINT_TYPE='C' and SEARCH_CONDITION_VC like '%DISPOSITION%' and SEARCH_CONDITION_VC like '%SUPPLIER%')loop execute immediate 'alter table RRL_STORE_RETURN_RECEIPT drop constraint '||dbms_assert.simple_sql_name(r.CONSTRAINT_NAME);end loop;
 execute immediate q'[alter table RRL_STORE_RETURN_RECEIPT add constraint RRL_STORE_RETURN_DISPOSITION_CK check(DISPOSITION in('REUSE','SUPPLIER','DISPOSAL'))]';
end;
/
begin execute immediate q'[create table RRL_RETURN_REUSE_PROOF(
 OPERATION_ID varchar2(100) primary key references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 BOX_COUNT number(18,0) not null check(BOX_COUNT>0),
 BOX_BASE_QTY number(27,9) not null check(BOX_BASE_QTY>0),
 UOM_POLICY_VERSION number(19) not null,
 ARTICLE_BARCODE varchar2(128 byte) not null,
 SOURCE_BATCH varchar2(100 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
