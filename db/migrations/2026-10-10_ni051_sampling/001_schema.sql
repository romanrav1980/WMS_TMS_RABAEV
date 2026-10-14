declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_SBORKA_PALLETS' and COLUMN_NAME='QC_SAMPLE_BUCKET';
 if n=0 then execute immediate 'alter table RRL_SBORKA_PALLETS add(QC_SAMPLE_BUCKET number check(QC_SAMPLE_BUCKET>=0 and QC_SAMPLE_BUCKET<10000 and QC_SAMPLE_BUCKET=trunc(QC_SAMPLE_BUCKET)),QC_SAMPLE_REQUIRED number default 0 not null check(QC_SAMPLE_REQUIRED in(0,1)),QC_RESCAN_REQUIRED number default 0 not null check(QC_RESCAN_REQUIRED in(0,1)),SCAN_ITEM_PROVED number default 0 not null check(SCAN_ITEM_PROVED in(0,1)))';end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_WARE_SETTINGS' and COLUMN_NAME='OUTGOING_QC_SAMPLE_PERCENT';
 if n=0 then execute immediate 'alter table RRL_RECEIPT_WARE_SETTINGS add OUTGOING_QC_SAMPLE_PERCENT number default 0 not null check(OUTGOING_QC_SAMPLE_PERCENT>=0 and OUTGOING_QC_SAMPLE_PERCENT<=100 and OUTGOING_QC_SAMPLE_PERCENT=trunc(OUTGOING_QC_SAMPLE_PERCENT,2))';end if;
end;
/