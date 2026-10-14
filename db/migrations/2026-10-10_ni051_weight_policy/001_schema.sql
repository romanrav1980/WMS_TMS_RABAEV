declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_SKU_RULE' and COLUMN_NAME='QC_BASE_WEIGHT_KG';
 if n=0 then execute immediate 'alter table RRL_RECEIPT_SKU_RULE add(QC_BASE_WEIGHT_KG number check(QC_BASE_WEIGHT_KG>0),QC_BOX_WEIGHT_KG number check(QC_BOX_WEIGHT_KG>0),QC_WEIGHT_VERSION number default 0 not null check(QC_WEIGHT_VERSION>=0))';end if;
end;
/
declare n number;begin select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_SKU_RULE' and COLUMN_NAME='QC_WEIGHT_BASE_UOM';if n=0 then execute immediate 'alter table RRL_RECEIPT_SKU_RULE add QC_WEIGHT_BASE_UOM varchar2(20)';end if;end;
/
