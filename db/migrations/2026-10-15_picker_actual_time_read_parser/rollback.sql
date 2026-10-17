-- Aware time history already exists: rollback is intentionally unavailable here.
declare n number;begin
 select(select count(*)from RRL_PICKER_TIME_STREAM)+(select count(*)from RRL_PICKER_TIME_EVENT)+(select count(*)from RRL_PICKER_TIME_SPAN)+(select count(*)from RRL_PICKER_TIME_COMMAND)into n from dual;
 if n!=0 then raise_application_error(-20886,'PICKER_TIME_HISTORY_FORWARD_REPAIR_REQUIRED');end if;
end;
/
-- Even an empty future database requires a separately reviewed checkpoint: no blind downgrade.
begin raise_application_error(-20886,'PICKER_TIME_READ_PARSER_REVIEWED_FORWARD_REPAIR_ONLY');end;
/
