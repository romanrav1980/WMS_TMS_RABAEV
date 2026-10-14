-- MIGRATION_ID:2026-10-11-205-final-scale-qc-use
create table RRL_WH_FINAL_SCALE_USE(
 CAPTURE_KEY varchar2(64) primary key references RRL_WH_SCALE_CAPTURE(CAPTURE_KEY),
 STOCK_OPERATION_ID varchar2(100) not null unique references RRL_STOCK_OPERATION(OPERATION_ID),
 TARE_CAPTURE_KEY varchar2(64) not null references RRL_WH_SCALE_CAPTURE(CAPTURE_KEY),
 CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 CASE_CONTENT_VERSION number not null,
 COMPOSITION_SIGNATURE varchar2(64) not null,
 ACTOR varchar2(50) not null,
 USED_AT timestamp with time zone default systimestamp not null);
