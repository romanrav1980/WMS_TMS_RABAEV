create or replace trigger RRL_DWAIT_RUN_GUARD before insert or update or delete on RRL_ST_DEFER_WAIT_RUN
begin
 if updating or deleting or RRL_ST_DEFER_WAIT_API.write_allowed!=1 then raise_application_error(-20886,'DEFER_WAIT_RUN_APPEND_ONLY_OWNED');end if;
end;
/
create or replace trigger RRL_DWAIT_PLAN_GUARD before insert or update or delete on RRL_ST_DEFER_WAIT_PLAN
begin
 if updating or deleting or RRL_ST_DEFER_WAIT_API.write_allowed!=1 then raise_application_error(-20886,'DEFER_WAIT_PLAN_APPEND_ONLY_OWNED');end if;
end;
/
create or replace trigger RRL_DEFER_WAIT_CELL_GUARD
before insert or update of DEFER_WAIT_CELL,WARE_ID on RRL_RECEIPT_WARE_SETTINGS
for each row
begin
 if :new.DEFER_WAIT_CELL is not null then RRL_ST_DEFER_WAIT_CORE.check_target(:new.DEFER_WAIT_CELL,:new.WARE_ID);end if;
end;
/
