prompt [migration 2026-05-19-032] wave replenishment queue statuses - apply

declare
  procedure drop_constraint_if_exists(p_table varchar2, p_constraint varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_constraints
     where table_name = upper(p_table)
       and constraint_name = upper(p_constraint);
    if n > 0 then
      execute immediate 'alter table ' || p_table || ' drop constraint ' || p_constraint;
    end if;
  end;
begin
  drop_constraint_if_exists('RRL_PICK_WAVE_REPLENISH_TASK', 'RRL_PICK_WAVE_REPL_CHK1');

  execute immediate q'[
    alter table RRL_PICK_WAVE_REPLENISH_TASK add constraint RRL_PICK_WAVE_REPL_CHK1
    check (STATUS in (
      'NEW',
      'QUEUED',
      'WAIT_FREE_CELL',
      'WAIT_MINIMAX',
      'RELEASED',
      'ASSIGNED',
      'IN_PROGRESS',
      'DONE',
      'CANCELLED',
      'FAILED'
    ))
  ]';
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-19-032-wave-replenishment-queue-statuses' migration_id,
         'Wave replenishment queue statuses for same-SKU repeated drops and dynamic pick-face waiting' description,
         '032_apply.sql' script_name,
         '032_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when matched then update set
  d.DESCRIPTION = s.DESCRIPTION,
  d.SCRIPT_NAME = s.SCRIPT_NAME,
  d.ROLLBACK_SCRIPT = s.ROLLBACK_SCRIPT,
  d.APPLIED_AT = sysdate,
  d.APPLIED_BY = user
when not matched then insert (
  MIGRATION_ID, DESCRIPTION, SCRIPT_NAME, ROLLBACK_SCRIPT, APPLIED_AT, APPLIED_BY
) values (
  s.MIGRATION_ID, s.DESCRIPTION, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, sysdate, user
);

commit;

prompt [migration 2026-05-19-032] done
