prompt [migration 2026-05-17-030] wave replenishment source reservation - apply

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

  procedure ensure_index(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_indexes
     where index_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;
begin
  ensure_column('RRL_PICK_WAVE_DEMAND', 'MIN_SHELF_LIFE_DAYS',
    'alter table RRL_PICK_WAVE_DEMAND add MIN_SHELF_LIFE_DAYS number');
  ensure_column('RRL_PICK_WAVE_DEMAND', 'MIN_SHELF_LIFE_PERCENT',
    'alter table RRL_PICK_WAVE_DEMAND add MIN_SHELF_LIFE_PERCENT number');

  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'SOURCE_RESERVATION_ID',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add SOURCE_RESERVATION_ID number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'SOURCE_AVAILABLE_QTY',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add SOURCE_AVAILABLE_QTY number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'SOURCE_PRODUCED_DATE',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add SOURCE_PRODUCED_DATE date');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'SOURCE_EXPIRY_DATE',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add SOURCE_EXPIRY_DATE date');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'MIN_SHELF_LIFE_DAYS',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add MIN_SHELF_LIFE_DAYS number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'MIN_SHELF_LIFE_PERCENT',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add MIN_SHELF_LIFE_PERCENT number');

  ensure_index('RRL_PICK_WAVE_REPL_I3',
    'create index RRL_PICK_WAVE_REPL_I3 on RRL_PICK_WAVE_REPLENISH_TASK (SOURCE_RESERVATION_ID)');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-030-wave-replenishment-source-reservation' migration_id,
         'Wave replenishment source-pallet reservation and customer shelf-life snapshot' description,
         '030_apply.sql' script_name,
         '030_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-030] done
