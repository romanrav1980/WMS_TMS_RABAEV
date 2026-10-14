alter table RRL_TT_UNLOAD_FACT modify(CASE_PICK_TASK_ID null);
alter table RRL_TT_UNLOAD_FACT add(ROOT_UID varchar2(150) references RRL_PALLETS(UID_PALLET));
alter table RRL_TT_UNLOAD_FACT add constraint RRL_TT_UNLOAD_ROOT_CK check((CASE_PICK_TASK_ID is not null and ROOT_UID is null)or(CASE_PICK_TASK_ID is null and ROOT_UID is not null));
