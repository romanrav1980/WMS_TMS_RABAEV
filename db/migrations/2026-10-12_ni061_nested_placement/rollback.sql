declare n number;begin select count(*)into n from RRL_INTERWARE_PUT_PLAN p join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID where t.SOURCE_DOC_TYPE='WAREHOUSE_HU';if n>0 then raise_application_error(-20899,'RETAINED_HU_TASK_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_put_spec.sql
@@000_before_put.sql
@@000_before_hu_task.sql
@@000_before_task_guard.sql
@@000_before_placement_guard.sql
@@000_before_hu_cmd.sql
@@006_recompile.sql
