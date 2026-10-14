-- Logical warehouse belongs to a demand pool; SOFT keeps physical WARE_ID/CELL/UID null.
declare
 procedure add_col(t varchar2,c varchar2,ddl varchar2) is n number;begin
  select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME=t and COLUMN_NAME=c;
  if n=0 then execute immediate ddl;end if;
 end;
begin
 add_col('RRL_RECEIPT_SKU_RULE','SHIP_FROM_STOCK','alter table RRL_RECEIPT_SKU_RULE add SHIP_FROM_STOCK number');
 add_col('RRL_RECEIPT_SKU_RULE','STOCK_ALLOC_CLASS','alter table RRL_RECEIPT_SKU_RULE add STOCK_ALLOC_CLASS varchar2(20) default ''OTHER'' not null');
 add_col('RRL_RECEIPT_SKU_RULE','PICK_STEP_BASE','alter table RRL_RECEIPT_SKU_RULE add PICK_STEP_BASE number default 1 not null');
 add_col('RRL_RECEIPT_SKU_RULE','ALLOCATION_VERSION','alter table RRL_RECEIPT_SKU_RULE add ALLOCATION_VERSION number default 1 not null');
 add_col('RRL_STOCK_RESERVATION','POOL_WARE_ID','alter table RRL_STOCK_RESERVATION add POOL_WARE_ID number');
end;
/
declare n number;begin
 select count(*) into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_ALLOCATION_RULE_CK';
 if n=0 then execute immediate 'alter table RRL_RECEIPT_SKU_RULE add constraint RRL_ALLOCATION_RULE_CK check(SHIP_FROM_STOCK in(0,1) and STOCK_ALLOC_CLASS in(''DRY_RACK'',''FRESH'',''OTHER'') and PICK_STEP_BASE>0 and ALLOCATION_VERSION>=1)';end if;
 select count(*) into n from USER_INDEXES where INDEX_NAME='RRL_SOFT_POOL_LINE_U';
 if n=0 then execute immediate 'create unique index RRL_SOFT_POOL_LINE_U on RRL_STOCK_RESERVATION(
 case when RESERVATION_KIND=''SOFT'' and POOL_WARE_ID is not null and STATUS in(''ACTIVE'',''ALLOCATED'') then POOL_WARE_ID end,
 case when RESERVATION_KIND=''SOFT'' and POOL_WARE_ID is not null and STATUS in(''ACTIVE'',''ALLOCATED'') then ARTICUL end,
 case when RESERVATION_KIND=''SOFT'' and POOL_WARE_ID is not null and STATUS in(''ACTIVE'',''ALLOCATED'') then SOURCE_LINE_ID end)';end if;
end;
/
