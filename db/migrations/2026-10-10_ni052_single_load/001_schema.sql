-- Exactly one physical owner: an existing pallet/container OR an existing CASE task.
-- Keep the original pallet FK and immutable old facts; no history backfill or fictitious pallet.
declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_TT_HU_LOAD_FACT' and COLUMN_NAME='ROOT_CASE_TASK_ID';
 if n=0 then
  execute immediate 'alter table RRL_TT_HU_LOAD_FACT modify ROOT_UID null';
  execute immediate 'alter table RRL_TT_HU_LOAD_FACT add ROOT_CASE_TASK_ID number(10)';
  execute immediate 'alter table RRL_TT_HU_LOAD_FACT add constraint RRL_TT_LOAD_CASE_FK foreign key(ROOT_CASE_TASK_ID) references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID)';
  execute immediate 'alter table RRL_TT_HU_LOAD_FACT add constraint RRL_TT_LOAD_OWNER_CK check((ROOT_UID is not null and ROOT_CASE_TASK_ID is null) or(ROOT_UID is null and ROOT_CASE_TASK_ID is not null))';
  execute immediate q'[create unique index RRL_TT_LOAD_CASE_U1 on RRL_TT_HU_LOAD_FACT(case when STATUS in('LOADED','DEPARTED') then ROOT_CASE_TASK_ID end)]';
 end if;
end;
/
