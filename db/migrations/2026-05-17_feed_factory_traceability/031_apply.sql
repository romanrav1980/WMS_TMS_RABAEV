prompt [migration 2026-05-19-031] wave pick task fact and minimax trigger - apply

declare
  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_tab_cols
     where table_name = upper(p_table)
       and column_name = upper(p_column);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;
begin
  ensure_column('RRL_PICK_TASK', 'FACT_QTY',
    'alter table RRL_PICK_TASK add FACT_QTY number');
  ensure_column('RRL_PICK_TASK', 'DONE_BY',
    'alter table RRL_PICK_TASK add DONE_BY varchar2(50)');

  ensure_column('RRL_PICK_WAVE_TASK', 'FACT_QTY',
    'alter table RRL_PICK_WAVE_TASK add FACT_QTY number');
  ensure_column('RRL_PICK_WAVE_TASK', 'DONE_AT',
    'alter table RRL_PICK_WAVE_TASK add DONE_AT date');
  ensure_column('RRL_PICK_WAVE_TASK', 'DONE_BY',
    'alter table RRL_PICK_WAVE_TASK add DONE_BY varchar2(50)');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-19-031-wave-pick-task-fact-minimax-trigger' migration_id,
         'Wave pick task fact fields for automatic Minimax trigger after case-pick confirmation' description,
         '031_apply.sql' script_name,
         '031_rollback.sql' rollback_script
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

prompt [migration 2026-05-19-031] done
