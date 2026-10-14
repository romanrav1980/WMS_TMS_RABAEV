alter table RRL_TARE_LOAD_RECOVERY modify(CASE_PICK_TASK_ID null);
alter table RRL_TARE_LOAD_RECOVERY add(ROOT_UID varchar2(150)references RRL_PALLETS(UID_PALLET));
alter table RRL_TARE_LOAD_RECOVERY add constraint RRL_TARE_RECOVERY_PLACE_CK check((CASE_PICK_TASK_ID is not null and ROOT_UID is null)or(CASE_PICK_TASK_ID is null and ROOT_UID is not null));
