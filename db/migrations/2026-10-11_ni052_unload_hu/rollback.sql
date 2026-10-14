declare n number;begin select count(*)into n from RRL_TT_UNLOAD_FACT where ROOT_UID is not null;if n>0 then raise_application_error(-20863,'UNLOAD_HU_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_unload.sql
@@000_before_unload_guard.sql
@@000_before_load_guard.sql
@@000_before_sample_guard.sql
@@000_before_link_guard.sql
@@000_before_tare_guard.sql
@@000_before_container_guard.sql
@@000_before_departure_guard.sql
alter table RRL_TT_UNLOAD_FACT drop constraint RRL_TT_UNLOAD_ROOT_CK;
alter table RRL_TT_UNLOAD_FACT drop column ROOT_UID;
alter table RRL_TT_UNLOAD_FACT modify(CASE_PICK_TASK_ID not null);
