prompt [migration 2026-05-17-022] Slow SQL diagnostics - apply

declare
  procedure ensure_table(p_name varchar2, p_sql varchar2) is
    n number;
  begin
    select count(*) into n from user_tables where table_name = upper(p_name);
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
  ensure_table('RRL_SQL_SLOW_LOG', q'[
    create table RRL_SQL_SLOW_LOG (
      LOG_ID number not null,
      CREATED_AT timestamp default systimestamp not null,
      MODULE varchar2(48),
      ACTION varchar2(200),
      API_CALL_ID number,
      REQUEST_ID varchar2(64),
      API_METHOD varchar2(10),
      API_PATH varchar2(500),
      DB_USER varchar2(128),
      ELAPSED_MS number not null,
      SQL_TEXT_HASH varchar2(64) not null,
      SQL_TEXT varchar2(4000),
      PARAMS_JSON varchar2(4000),
      ROW_COUNT number,
      ERROR_TEXT varchar2(4000),
      CLIENT_IDENTIFIER varchar2(64),
      OPERATION_KIND varchar2(50),
      constraint RRL_SQL_SLOW_LOG_PK primary key (LOG_ID)
    )
  ]');

  ensure_sequence('RRL_SQL_SLOW_LOG_SQ',
    'create sequence RRL_SQL_SLOW_LOG_SQ start with 1 increment by 1 nocache');

  ensure_index('RRL_SQL_SLOW_LOG_I1',
    'create index RRL_SQL_SLOW_LOG_I1 on RRL_SQL_SLOW_LOG (CREATED_AT, LOG_ID)');
  ensure_index('RRL_SQL_SLOW_LOG_I2',
    'create index RRL_SQL_SLOW_LOG_I2 on RRL_SQL_SLOW_LOG (ELAPSED_MS, CREATED_AT)');
  ensure_index('RRL_SQL_SLOW_LOG_I3',
    'create index RRL_SQL_SLOW_LOG_I3 on RRL_SQL_SLOW_LOG (SQL_TEXT_HASH, CREATED_AT)');
  ensure_index('RRL_SQL_SLOW_LOG_I4',
    'create index RRL_SQL_SLOW_LOG_I4 on RRL_SQL_SLOW_LOG (API_CALL_ID)');
  ensure_index('RRL_SQL_SLOW_LOG_I5',
    'create index RRL_SQL_SLOW_LOG_I5 on RRL_SQL_SLOW_LOG (MODULE, API_PATH)');
end;
/

insert into RIGHTS (RIGHT1, USER_GROUP, ID, DESCR)
select s.RIGHT1,
       'GLOBAL_ADMIN',
       (select nvl(max(ID), 0) from RIGHTS) + row_number() over (order by s.RIGHT1),
       s.DESCR
  from (
    select 'SLOW_SQL_VIEW' RIGHT1, 'View slow SQL diagnostics' DESCR from dual
  ) s
 where not exists (
   select 1
     from RIGHTS r
    where r.USER_GROUP = 'GLOBAL_ADMIN'
      and upper(r.RIGHT1) = s.RIGHT1
 );

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-17-022-slow-sql-diagnostics' migration_id,
         'Slow SQL log and Oracle-native diagnostics support' description,
         '022_apply.sql' script_name,
         '022_rollback.sql' rollback_script
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

prompt [migration 2026-05-17-022] done
