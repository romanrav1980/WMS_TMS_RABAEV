prompt [migration 2026-05-19-033] dynamic pick-face assignments - apply

declare
  procedure ensure_table(p_table varchar2, p_sql clob) is
    n number;
  begin
    select count(*)
      into n
      from user_tables
     where table_name = upper(p_table);
    if n = 0 then
      execute immediate p_sql;
    end if;
  end;

  procedure ensure_sequence(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*)
      into n
      from user_sequences
     where sequence_name = upper(p_name);
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
  ensure_table('RRL_PICK_FACE_ASSIGNMENT', q'[
    create table RRL_PICK_FACE_ASSIGNMENT (
      PICK_FACE_ASSIGNMENT_ID number not null,
      PICK_FACE_ID number not null,
      CELL_CODE varchar2(60) not null,
      PICK_WAVE_ID number not null,
      PICK_WAVE_REPLENISH_TASK_ID number,
      ARTICUL varchar2(40) not null,
      ASSIGNMENT_KIND varchar2(20) default 'DYNAMIC' not null,
      STATUS varchar2(20) default 'ACTIVE' not null,
      ASSIGNED_AT date default sysdate not null,
      ASSIGNED_BY varchar2(50),
      RELEASED_AT date,
      RELEASED_BY varchar2(50),
      RELEASE_REASON varchar2(200),
      constraint RRL_PICK_FACE_ASSIGN_PK primary key (PICK_FACE_ASSIGNMENT_ID),
      constraint RRL_PICK_FACE_ASSIGN_FK1 foreign key (PICK_FACE_ID) references RRL_PICK_FACE (PICK_FACE_ID),
      constraint RRL_PICK_FACE_ASSIGN_FK2 foreign key (PICK_WAVE_ID) references RRL_PICK_WAVE (PICK_WAVE_ID),
      constraint RRL_PICK_FACE_ASSIGN_CHK1 check (ASSIGNMENT_KIND in ('DYNAMIC', 'OVERFLOW')),
      constraint RRL_PICK_FACE_ASSIGN_CHK2 check (STATUS in ('ACTIVE', 'RELEASED', 'CANCELLED'))
    )
  ]');

  ensure_sequence('RRL_PICK_FACE_ASSIGN_SQ', 'create sequence RRL_PICK_FACE_ASSIGN_SQ start with 1 increment by 1 nocache');
  ensure_index('RRL_PICK_FACE_ASSIGN_I1',
    'create index RRL_PICK_FACE_ASSIGN_I1 on RRL_PICK_FACE_ASSIGNMENT (PICK_WAVE_ID, STATUS)');
  ensure_index('RRL_PICK_FACE_ASSIGN_I2',
    'create index RRL_PICK_FACE_ASSIGN_I2 on RRL_PICK_FACE_ASSIGNMENT (ARTICUL, STATUS)');
  ensure_index('RRL_PICK_FACE_ASSIGN_U1',
    q'[create unique index RRL_PICK_FACE_ASSIGN_U1 on RRL_PICK_FACE_ASSIGNMENT (
      case when STATUS = 'ACTIVE' then CELL_CODE end
    )]');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-19-033-dynamic-pick-face-assignments' migration_id,
         'Temporary dynamic pick-face assignment by wave and articul for queued replenishment release' description,
         '033_apply.sql' script_name,
         '033_rollback.sql' rollback_script
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

prompt [migration 2026-05-19-033] done
