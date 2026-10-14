declare n number;begin
 select count(*)into n from RRL_ST_DEFER_WAIT_PLAN p join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID
 where p.BASE_UOM='HU'and t.STATUS not in('DONE','CANCELLED');
 if n>0 then raise_application_error(-20886,'ROLLBACK_REQUIRES_RECOVERY_OF_OPEN_HU_WAIT_TASKS');end if;
end;
/
