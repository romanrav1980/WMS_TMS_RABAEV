-- MIGRATION_ID: 2026-10-09-005-stock-posting-cutover
-- Called only by stock_posting_cutover.py with exclusive release/config fences and table drain.
-- Caller owns commit; any failure restores PREPARED and the old SOFT forecasts.
declare n number; v_scn number;
begin
 select count(*) into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='PREPARED';
 if n!=1 then raise_application_error(-20808,'CUTOVER_REQUIRES_PREPARED');end if;
 update RRL_STOCK_RELEASE set STATE='CUTOVER',CHANGED_AT=systimestamp,CHANGED_BY='admin' where RELEASE_ID=1;
 v_scn:=dbms_flashback.get_system_change_number;
 insert into RRL_STOCK_BASELINE(BASELINE_ID,SNAPSHOT_SCN,CREATED_BY,STATE,MANIFEST_HASH)
 values(:baseline,v_scn,'admin','READY',:manifest);
 -- P, H and physical-unit tables are verified empty while exclusively locked.
 update RRL_STOCK_RELEASE set STATE='ACTIVE',BASELINE_ID=:baseline,CHANGED_AT=systimestamp,CHANGED_BY='admin' where RELEASE_ID=1;
end;