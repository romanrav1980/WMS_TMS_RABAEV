prompt [migration 2026-05-20-037] replenishment release policy rules - apply

declare
  procedure ensure_table(p_table varchar2, p_sql clob) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_table);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_sequence(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_sequences where sequence_name = upper(p_name);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_column(p_table varchar2, p_column varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n
      from user_tab_columns
     where table_name = upper(p_table)
       and column_name = upper(p_column);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_index(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_indexes where index_name = upper(p_name);
    if n = 0 then
      begin
        execute immediate p_sql;
      exception
        when others then
          if sqlcode = -1408 then
            null;
          else
            raise;
          end if;
      end;
    end if;
  end;
begin
  ensure_table('RRL_ARTICUL_REPLENISH_RULE', q'[
    create table RRL_ARTICUL_REPLENISH_RULE (
      ARTICUL_REPLENISH_RULE_ID number not null,
      ARTICUL varchar2(80) not null,
      REPLENISHMENT_METHOD varchar2(20) default 'MINIMAX' not null,
      REPLENISHMENT_RELEASE_POLICY varchar2(40) default 'LAYER_TRIGGER' not null,
      REPLENISHMENT_QTY_MODE varchar2(20) default 'FILL_TO_VOLUME' not null,
      MIN_TRIGGER_BOX_QTY number,
      MIN_TRIGGER_LAYER_QTY number default 1,
      SAFETY_LAYER_QTY number,
      BOXES_PER_LAYER number,
      BOXES_PER_PALLET number,
      BOX_VOLUME_M3 number,
      ALLOW_PARTIAL_PALLET number(1) default 1 not null,
      PREDICTIVE_BUFFER_MIN number,
      PICK_RATE_SOURCE varchar2(20) default 'MIXED' not null,
      RECHECK_ON_PICK_EVENT number(1) default 1 not null,
      ACTIVE number(1) default 1 not null,
      COMMENT_TEXT varchar2(500),
      CREATED_AT date default sysdate not null,
      CREATED_BY varchar2(50),
      UPDATED_AT date default sysdate not null,
      UPDATED_BY varchar2(50),
      constraint RRL_ART_REPL_RULE_PK primary key (ARTICUL_REPLENISH_RULE_ID),
      constraint RRL_ART_REPL_RULE_U1 unique (ARTICUL),
      constraint RRL_ART_REPL_RULE_CHK1 check (REPLENISHMENT_METHOD in ('IMMEDIATE', 'MINIMAX')),
      constraint RRL_ART_REPL_RULE_CHK2 check (REPLENISHMENT_RELEASE_POLICY in ('LAYER_TRIGGER', 'PREDICTIVE_LEAD_TIME')),
      constraint RRL_ART_REPL_RULE_CHK3 check (REPLENISHMENT_QTY_MODE in ('FULL_PALLET', 'HALF_PALLET', 'FILL_TO_VOLUME')),
      constraint RRL_ART_REPL_RULE_CHK4 check (ALLOW_PARTIAL_PALLET in (0, 1)),
      constraint RRL_ART_REPL_RULE_CHK5 check (PICK_RATE_SOURCE in ('PLAN', 'FACT', 'MIXED')),
      constraint RRL_ART_REPL_RULE_CHK6 check (RECHECK_ON_PICK_EVENT in (0, 1)),
      constraint RRL_ART_REPL_RULE_CHK7 check (ACTIVE in (0, 1))
    )
  ]');

  ensure_sequence('RRL_ART_REPL_RULE_SQ',
    'create sequence RRL_ART_REPL_RULE_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_ART_REPL_RULE_I1',
    'create index RRL_ART_REPL_RULE_I1 on RRL_ARTICUL_REPLENISH_RULE (upper(ARTICUL), ACTIVE)');

  ensure_column('RRL_PICK_FACE_ARTICUL', 'USE_ARTICUL_REPLENISH_RULE',
    'alter table RRL_PICK_FACE_ARTICUL add USE_ARTICUL_REPLENISH_RULE number(1) default 1 not null');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'REPLENISHMENT_RELEASE_POLICY',
    q'[alter table RRL_PICK_FACE_ARTICUL add REPLENISHMENT_RELEASE_POLICY varchar2(40) default 'LAYER_TRIGGER' not null]');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'SAFETY_LAYER_QTY',
    'alter table RRL_PICK_FACE_ARTICUL add SAFETY_LAYER_QTY number');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'PREDICTIVE_BUFFER_MIN',
    'alter table RRL_PICK_FACE_ARTICUL add PREDICTIVE_BUFFER_MIN number');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'PICK_RATE_SOURCE',
    q'[alter table RRL_PICK_FACE_ARTICUL add PICK_RATE_SOURCE varchar2(20) default 'MIXED' not null]');
  ensure_column('RRL_PICK_FACE_ARTICUL', 'RECHECK_ON_PICK_EVENT',
    'alter table RRL_PICK_FACE_ARTICUL add RECHECK_ON_PICK_EVENT number(1) default 1 not null');

  ensure_column('RRL_PICK_WAVE_DEMAND', 'REPLENISHMENT_RELEASE_POLICY',
    'alter table RRL_PICK_WAVE_DEMAND add REPLENISHMENT_RELEASE_POLICY varchar2(40)');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'REPLENISHMENT_RELEASE_POLICY',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add REPLENISHMENT_RELEASE_POLICY varchar2(40)');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'SAFETY_LAYER_QTY',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add SAFETY_LAYER_QTY number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'PREDICTIVE_BUFFER_MIN',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add PREDICTIVE_BUFFER_MIN number');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'PICK_RATE_SOURCE',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add PICK_RATE_SOURCE varchar2(20)');
  ensure_column('RRL_PICK_WAVE_REPLENISH_TASK', 'RECHECK_ON_PICK_EVENT',
    'alter table RRL_PICK_WAVE_REPLENISH_TASK add RECHECK_ON_PICK_EVENT number(1)');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-20-037-replenishment-release-policy-rules' migration_id,
         'Article-level and pick-face override rules for layer-trigger and predictive replenishment release policies' description,
         '037_apply.sql' script_name,
         '037_rollback.sql' rollback_script
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

prompt [migration 2026-05-20-037] apply done
