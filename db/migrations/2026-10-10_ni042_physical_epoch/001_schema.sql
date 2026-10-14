declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_REMAINS' and COLUMN_NAME='PHYSICAL_VERSION';
 if n=0 then execute immediate 'alter table RRL_REMAINS add PHYSICAL_VERSION number default 0 not null check(PHYSICAL_VERSION>=0 and PHYSICAL_VERSION=trunc(PHYSICAL_VERSION))';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_SLOT_CLAIM' and COLUMN_NAME='HU_PHYSICAL_VERSION';
 if n=0 then execute immediate 'alter table RRL_RECEIPT_SLOT_CLAIM add(HU_PHYSICAL_VERSION number,HU_UNIT_SIGNATURE varchar2(64))';end if;
end;
/
