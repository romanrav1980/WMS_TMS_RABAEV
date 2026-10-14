-- MIGRATION_ID:2026-10-11-204-final-scale-archive
alter table RRL_WH_SCALE_CAPTURE add(
 CAPTURE_PURPOSE varchar2(12) default 'PICK' not null,
 TARE_CAPTURE_KEY varchar2(64),
 PALLET_TYPE_ID number,
 TYPE_VERSION number,
 COMPOSITION_SIGNATURE varchar2(64));
alter table RRL_WH_SCALE_CAPTURE modify(CASE_PICK_LINE_ID null,ARTICLE null,SOURCE_CELL null,SCANNED_PRODUCT null);
alter table RRL_WH_SCALE_CAPTURE add constraint RRL_WH_SCALE_PURPOSE_C check(CAPTURE_PURPOSE in('PICK','EMPTY_TARE','FINAL_GROSS'));
alter table RRL_WH_SCALE_CAPTURE add constraint RRL_WH_SCALE_TARE_F foreign key(TARE_CAPTURE_KEY)references RRL_WH_SCALE_CAPTURE(CAPTURE_KEY);
alter table RRL_WH_SCALE_CAPTURE add constraint RRL_WH_SCALE_TYPE_F foreign key(PALLET_TYPE_ID)references RRL_PALLET_TYPE(PALLET_TYPE_ID);
alter table RRL_WH_SCALE_CAPTURE add constraint RRL_WH_SCALE_SOURCE_C check(
 (CAPTURE_PURPOSE='PICK' and CASE_PICK_LINE_ID is not null and ARTICLE is not null and SOURCE_CELL is not null and SCANNED_PRODUCT is not null and TARE_CAPTURE_KEY is null)
 or(CAPTURE_PURPOSE='EMPTY_TARE' and CASE_PICK_LINE_ID is null and ARTICLE is null and SOURCE_CELL is null and SCANNED_PRODUCT is null
  and PALLET_TYPE_ID is not null and TYPE_VERSION is not null and TARE_CAPTURE_KEY is null and COMPOSITION_SIGNATURE is null)
 or(CAPTURE_PURPOSE='FINAL_GROSS' and CASE_PICK_LINE_ID is null and ARTICLE is null and SOURCE_CELL is null and SCANNED_PRODUCT is null
  and PALLET_TYPE_ID is not null and TYPE_VERSION is not null and TARE_CAPTURE_KEY is not null and COMPOSITION_SIGNATURE is not null));
create index RRL_WH_SCALE_CASE_PURPOSE_I on RRL_WH_SCALE_CAPTURE(CASE_PICK_TASK_ID,CAPTURE_PURPOSE,RECEIVED_AT);
