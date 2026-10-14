declare
begin
 if user!='RABAEV' then raise_application_error(-20801,'RABAEV_ONLY'); end if;
end;
/
-- MIGRATION_ID: 2026-10-14-retailcase-wave-name
-- Cosmetic wave name update: IDs, quantities, task membership and operation keys retained.
lock table RRL_PICK_WAVE in row exclusive mode nowait;
begin
 for r in (select PICK_WAVE_ID from RRL_PICK_WAVE
   where WAVE_NAME=utl_raw.cast_to_varchar2(hextoraw('4E49434F52415F4D494E494D4158'))
   order by PICK_WAVE_ID for update nowait) loop
  update RRL_PICK_WAVE set WAVE_NAME='RETAILCASE_MINIMAX' where PICK_WAVE_ID=r.PICK_WAVE_ID;
 end loop;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-retailcase-wave-name' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Product name update for existing minimax waves; no stock effect',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
