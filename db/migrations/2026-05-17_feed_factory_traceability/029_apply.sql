prompt [migration 2026-05-17-029] wave case-pick replenishment settings - apply

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

  procedure drop_constraint_if_exists(p_table varchar2, p_name varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_constraints
     where table_name = upper(p_table)
       and constraint_name = upper(p_name);
    if n > 0 then
      execute immediate 'alter table ' || p_table || ' drop constraint ' || p_name;
    end if;
  end;

  procedure ensure_constraint(p_table varchar2, p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_constraints
     where table_name = upper(p_table)
       and constraint_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;
begin
  ensure_column('RRL_PICK_FACE_ARTICUL', 'REPLENISHMENT_METHOD',
    q'[alter table RRL_PICK_FACE_ARTICUL add REPLENISHMENT_METHOD varchar2(20) default 'IMMEDIATE' not null]');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'REPLENISHMENT_QTY_MODE',
    q'[alter table RRL_PICK_FACE_ARTICUL add REPLENISHMENT_QTY_MODE varchar2(20) default 'FILL_TO_VOLUME' not null]');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'MIN_TRIGGER_BOX_QTY',
    'alter table RRL_PICK_FACE_ARTICUL add MIN_TRIGGER_BOX_QTY number');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'MIN_TRIGGER_LAYER_QTY',
    'alter table RRL_PICK_FACE_ARTICUL add MIN_TRIGGER_LAYER_QTY number');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'BOXES_PER_LAYER',
    'alter table RRL_PICK_FACE_ARTICUL add BOXES_PER_LAYER number');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'BOXES_PER_PALLET',
    'alter table RRL_PICK_FACE_ARTICUL add BOXES_PER_PALLET number');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'BOX_VOLUME_M3',
    'alter table RRL_PICK_FACE_ARTICUL add BOX_VOLUME_M3 number');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'ALLOW_PARTIAL_PALLET',
    'alter table RRL_PICK_FACE_ARTICUL add ALLOW_PARTIAL_PALLET number(1) default 1 not null');

  ensure_column('RRL_PICK_WAVE_DEMAND', 'PICK_FACE_FREE_QTY',
    'alter table RRL_PICK_WAVE_DEMAND add PICK_FACE_FREE_QTY number');
  ensure_column('RRL_PICK_WAVE_DEMAND', 'REPLENISH_QTY',
    'alter table RRL_PICK_WAVE_DEMAND add REPLENISH_QTY number');
  ensure_column('RRL_PICK_WAVE_DEMAND', 'REPLENISHMENT_METHOD',
    'alter table RRL_PICK_WAVE_DEMAND add REPLENISHMENT_METHOD varchar2(20)');
  ensure_column('RRL_PICK_WAVE_DEMAND', 'REPLENISHMENT_QTY_MODE',
    'alter table RRL_PICK_WAVE_DEMAND add REPLENISHMENT_QTY_MODE varchar2(20)');

  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'REPLENISHMENT_METHOD',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add REPLENISHMENT_METHOD varchar2(20)');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'REPLENISHMENT_QTY_MODE',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add REPLENISHMENT_QTY_MODE varchar2(20)');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'RELEASE_TRIGGER_QTY',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add RELEASE_TRIGGER_QTY number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'BOXES_PER_LAYER',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add BOXES_PER_LAYER number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'BOXES_PER_PALLET',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add BOXES_PER_PALLET number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'BOX_VOLUME_M3',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add BOX_VOLUME_M3 number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'PICK_FACE_MAX_VOLUME',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add PICK_FACE_MAX_VOLUME number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'WAIT_REASON',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add WAIT_REASON varchar2(200)');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'RELEASED_AT',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add RELEASED_AT date');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'RELEASED_BY',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add RELEASED_BY varchar2(50)');

  drop_constraint_if_exists('RRL_PICK_WAVE_REPLENISH_TASK', 'RRL_PICK_WAVE_REPL_CHK1');

  ensure_constraint('RRL_PICK_FACE_ARTICUL', 'RRL_PICK_FACE_ART_CHK3',
    q'[alter table RRL_PICK_FACE_ARTICUL add constraint RRL_PICK_FACE_ART_CHK3 check (REPLENISHMENT_METHOD in ('IMMEDIATE', 'MINIMAX'))]');
  ensure_constraint('RRL_PICK_FACE_ARTICUL', 'RRL_PICK_FACE_ART_CHK4',
    q'[alter table RRL_PICK_FACE_ARTICUL add constraint RRL_PICK_FACE_ART_CHK4 check (REPLENISHMENT_QTY_MODE in ('FULL_PALLET', 'HALF_PALLET', 'FILL_TO_VOLUME'))]');
  ensure_constraint('RRL_PICK_FACE_ARTICUL', 'RRL_PICK_FACE_ART_CHK5',
    q'[alter table RRL_PICK_FACE_ARTICUL add constraint RRL_PICK_FACE_ART_CHK5 check (ALLOW_PARTIAL_PALLET in (0, 1))]');

  ensure_constraint('RRL_PICK_WAVE_REPLENISH_TASK', 'RRL_PICK_WAVE_REPL_CHK1',
    q'[alter table RRL_PICK_WAVE_REPLENISH_TASK add constraint RRL_PICK_WAVE_REPL_CHK1 check (STATUS in ('NEW', 'WAIT_MINIMAX', 'RELEASED', 'ASSIGNED', 'IN_PROGRESS', 'DONE', 'CANCELLED', 'FAILED'))]');
  ensure_constraint('RRL_PICK_WAVE_REPLENISH_TASK', 'RRL_PICK_WAVE_REPL_CHK2',
    q'[alter table RRL_PICK_WAVE_REPLENISH_TASK add constraint RRL_PICK_WAVE_REPL_CHK2 check (REPLENISHMENT_METHOD is null or REPLENISHMENT_METHOD in ('IMMEDIATE', 'MINIMAX'))]');
  ensure_constraint('RRL_PICK_WAVE_REPLENISH_TASK', 'RRL_PICK_WAVE_REPL_CHK3',
    q'[alter table RRL_PICK_WAVE_REPLENISH_TASK add constraint RRL_PICK_WAVE_REPL_CHK3 check (REPLENISHMENT_QTY_MODE is null or REPLENISHMENT_QTY_MODE in ('FULL_PALLET', 'HALF_PALLET', 'FILL_TO_VOLUME'))]');

  ensure_index('RRL_PICK_FACE_ARTICUL_I2',
    'create index RRL_PICK_FACE_ARTICUL_I2 on RRL_PICK_FACE_ARTICUL (PICK_FACE_ID, REPLENISHMENT_METHOD, ACTIVE)');
  ensure_index('RRL_PICK_WAVE_REPL_I2',
    'create index RRL_PICK_WAVE_REPL_I2 on RRL_PICK_WAVE_REPLENISH_TASK (PICK_WAVE_ID, REPLENISHMENT_METHOD, STATUS)');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-029-wave-case-pick-replenishment-settings' migration_id,
         'Wave case-pick replenishment settings for immediate and minimax release' description,
         '029_apply.sql' script_name,
         '029_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-029] done
