declare n number;begin select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_SBORKA_PALLETS' and COLUMN_NAME='SCAN_MARK_PROVED';
if n=0 then execute immediate 'alter table RRL_SBORKA_PALLETS add(SCAN_MARK_PROVED number default 0 not null check(SCAN_MARK_PROVED in(0,1)),SCAN_PHYSICAL_UNIT_COUNT number default 0 not null check(SCAN_PHYSICAL_UNIT_COUNT>=0))';end if;end;
/