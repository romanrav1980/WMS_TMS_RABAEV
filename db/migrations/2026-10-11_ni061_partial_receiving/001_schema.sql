declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_INTERWARE_RECEIPT'and COLUMN_NAME='ORIGINAL_ROOT_UID';
 if n=0 then execute immediate 'alter table RRL_INTERWARE_RECEIPT add(ORIGINAL_ROOT_UID varchar2(200),EXPECTED_BASE_QTY number,DISCREPANCY_REASON varchar2(1000 CHAR),DISCREPANCY_REFERENCE varchar2(255 CHAR))';end if;
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_IW_RECEIPT_PART_CK';
 if n=0 then execute immediate 'alter table RRL_INTERWARE_RECEIPT add constraint RRL_IW_RECEIPT_PART_CK check((ORIGINAL_ROOT_UID is null and EXPECTED_BASE_QTY is null and DISCREPANCY_REASON is null and DISCREPANCY_REFERENCE is null)or(ORIGINAL_ROOT_UID is not null and ORIGINAL_ROOT_UID!=ROOT_UID and EXPECTED_BASE_QTY is not null and EXPECTED_BASE_QTY>BASE_QTY and DISCREPANCY_REASON is not null and DISCREPANCY_REFERENCE is not null))';end if;
end;
/
