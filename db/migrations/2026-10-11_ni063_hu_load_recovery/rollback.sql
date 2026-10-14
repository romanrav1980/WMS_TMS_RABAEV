declare n number;begin select count(*)into n from RRL_TARE_LOAD_RECOVERY where ROOT_UID is not null;if n>0 then raise_application_error(-20863,'HU_TARE_RECOVERY_HISTORY_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_tare_load_recovery_api.sql
@@000_before_rrl_stock_tare_book_cmd.sql
@@000_before_guard.sql
alter table RRL_TARE_LOAD_RECOVERY drop constraint RRL_TARE_RECOVERY_PLACE_CK;
alter table RRL_TARE_LOAD_RECOVERY drop column ROOT_UID;
alter table RRL_TARE_LOAD_RECOVERY modify(CASE_PICK_TASK_ID not null);
