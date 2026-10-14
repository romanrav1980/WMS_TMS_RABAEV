-- MIGRATION_ID:2026-10-11-207-case-measured-mass-manifest
alter table RRL_TT_LOAD_BOX_WEIGHT add(
 CASE_BOX_TASK_ID number,
 FINAL_SCALE_CAPTURE varchar2(64),
 WAREHOUSE_QC_OPERATION varchar2(100),
 TARE_WEIGHT_KG number(27,9),
 NET_WEIGHT_KG number(27,9),
 DEVICE_MODE varchar2(10),
 COMPOSITION_SIGNATURE varchar2(64),
 SIGNATURE_VERSION number(2),
 MEASURED_CONTENT_VERSION number,
 COVERAGE_COMPLETE number(1)default 1 not null,
 PALLET_BOX_UID generated always as(case when CASE_BOX_TASK_ID is null then BOX_UID else null end)virtual);
declare n number:=0;
begin
 for r in(select c.CONSTRAINT_NAME from USER_CONSTRAINTS c join USER_CONS_COLUMNS k on k.CONSTRAINT_NAME=c.CONSTRAINT_NAME
  join USER_CONSTRAINTS p on p.CONSTRAINT_NAME=c.R_CONSTRAINT_NAME
  where c.TABLE_NAME='RRL_TT_LOAD_BOX_WEIGHT'and c.CONSTRAINT_TYPE='R'and k.COLUMN_NAME='BOX_UID'and p.TABLE_NAME='RRL_PALLETS')loop
  n:=n+1;execute immediate 'alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint '||dbms_assert.enquote_name(r.CONSTRAINT_NAME,false);
 end loop;
 if n!=1 then raise_application_error(-20873,'LOAD_BOX_ORIGINAL_PALLET_FK_REQUIRED');end if;
 n:=0;
 for r in(select CONSTRAINT_NAME from USER_CONSTRAINTS where TABLE_NAME='RRL_TT_LOAD_BOX_WEIGHT'and CONSTRAINT_TYPE='C'
  and SEARCH_CONDITION_VC='MEASUREMENT_ORIGIN=''MANUAL_CONFIRMED''')loop
  n:=n+1;execute immediate 'alter table RRL_TT_LOAD_BOX_WEIGHT drop constraint '||dbms_assert.enquote_name(r.CONSTRAINT_NAME,false);
 end loop;
 if n!=1 then raise_application_error(-20873,'LOAD_BOX_ORIGINAL_ORIGIN_CHECK_REQUIRED');end if;
end;
/
alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_PALLET_F foreign key(PALLET_BOX_UID)references RRL_PALLETS(UID_PALLET);
alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_CASE_F foreign key(CASE_BOX_TASK_ID)references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID);
alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_SCALE_F foreign key(FINAL_SCALE_CAPTURE)references RRL_WH_SCALE_CAPTURE(CAPTURE_KEY);
alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_QC_F foreign key(WAREHOUSE_QC_OPERATION)references RRL_STOCK_OPERATION(OPERATION_ID);
alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_ORIGIN_C check(
 (MEASUREMENT_ORIGIN='MANUAL_CONFIRMED'and CASE_BOX_TASK_ID is null and FINAL_SCALE_CAPTURE is null and WAREHOUSE_QC_OPERATION is null
  and TARE_WEIGHT_KG is null and NET_WEIGHT_KG is null and DEVICE_MODE is null and COMPOSITION_SIGNATURE is null and SIGNATURE_VERSION is null and MEASURED_CONTENT_VERSION is null)
 or(MEASUREMENT_ORIGIN='WAREHOUSE_SCALE_QC'and CASE_BOX_TASK_ID is not null and FINAL_SCALE_CAPTURE is not null and WAREHOUSE_QC_OPERATION is not null
  and BOX_UID='CASE:'||to_char(CASE_BOX_TASK_ID,'FM9999999999999999999990')
  and TARE_WEIGHT_KG is not null and NET_WEIGHT_KG is not null and DEVICE_MODE is not null and SIGNATURE_VERSION is not null
  and TARE_WEIGHT_KG>0 and NET_WEIGHT_KG>0 and GROSS_WEIGHT_KG=TARE_WEIGHT_KG+NET_WEIGHT_KG
  and DEVICE_MODE in('TEST','HARDWARE')and COMPOSITION_SIGNATURE is not null and SIGNATURE_VERSION=3 and MEASURED_CONTENT_VERSION is not null
  and MEASURED_CONTENT_VERSION<=BOX_CONTENT_VERSION));

alter table RRL_TT_LOAD_BOX_WEIGHT add constraint RRL_LOAD_BOX_COVER_C check(COVERAGE_COMPLETE in(0,1));
