prompt Authorized dev-only stock cleanup; preserve archive; no quantity sum
declare
 n number;
 procedure ensure_table(p_name varchar2,p_ddl varchar2) is
 begin
  select count(*) into n from user_tables where table_name=p_name;
  if n=0 then execute immediate p_ddl; end if;
 end;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then
  raise_application_error(-20801,'Authorized dev RABAEV/orcl only');
 end if;
 ensure_table('RRL_STOCK_CLEANUP_BAK_20261008',q'[
  create table RRL_STOCK_CLEANUP_BAK_20261008 as
   select r.*,cast(null as varchar2(18)) SOURCE_ROW_ID,
          cast(null as varchar2(6)) CLEANUP_ACTION from RRL_REMAINS r where 1=0]');
 ensure_table('RRL_STOCK_CLEANUP_LOG',q'[
  create table RRL_STOCK_CLEANUP_LOG(
   CLEANUP_ID varchar2(100) primary key,CREATED_AT timestamp not null,
   ARCHIVED_ROWS number not null,DELETED_ROWS number not null,KEPT_ROWS number not null,
   JOURNAL_MAX_ID number,REASON varchar2(1000) not null)]');
end;
/
declare n number; v_archived number; v_deleted number; v_kept number; v_max number;
begin
 select count(*) into n from RRL_STOCK_CLEANUP_LOG where CLEANUP_ID='2026-10-08-013-stock-dev-cleanup';
 if n=0 then
  lock table RRL_REMAINS in exclusive mode wait 10;
  select count(*) into n from RRL_STOCK_CLEANUP_BAK_20261008;
  if n!=0 then raise_application_error(-20802,'Nonempty unregistered archive; investigate before cleanup'); end if;
  insert into RRL_STOCK_CLEANUP_BAK_20261008
   (CELL,UID_POLETA,REMAIN,OTHOD_NAKL_ID,TIME_OF_LAST_UPDATE,SOURCE_ROW_ID,CLEANUP_ACTION)
  select CELL,UID_POLETA,REMAIN,OTHOD_NAKL_ID,TIME_OF_LAST_UPDATE,SOURCE_ROW_ID,
         case when INVALID_ROW=1 or RN>1 then 'DELETE' else 'KEEP' end
    from (
     select r.*,rowidtochar(rowid) SOURCE_ROW_ID,
      case when CELL is null or UID_POLETA is null or REMAIN is null or REMAIN<0 then 1 else 0 end INVALID_ROW,
      count(*) over(partition by CELL,UID_POLETA) GROUP_COUNT,
      row_number() over(partition by CELL,UID_POLETA order by
       case when REMAIN is null or REMAIN<0 then 1 else 0 end,
       TIME_OF_LAST_UPDATE desc nulls last,rowid desc) RN
      from RRL_REMAINS r)
    where INVALID_ROW=1 or GROUP_COUNT>1;
  v_archived:=sql%rowcount;
  select count(*) into v_kept from RRL_STOCK_CLEANUP_BAK_20261008 where CLEANUP_ACTION='KEEP';
  select max(ID_EVENT) into v_max from RRL_EVENTS;
  delete from RRL_REMAINS
   where rowid in(select chartorowid(SOURCE_ROW_ID) from RRL_STOCK_CLEANUP_BAK_20261008 where CLEANUP_ACTION='DELETE');
  v_deleted:=sql%rowcount;
  if v_deleted!=v_archived-v_kept then raise_application_error(-20803,'Cleanup archive/delete count differs'); end if;
  insert into RRL_STOCK_CLEANUP_LOG
   values('2026-10-08-013-stock-dev-cleanup',systimestamp,v_archived,v_deleted,v_kept,v_max,
    'Owner authorized cleaning test stock. Keep latest valid row by timestamp/ROWID; archive all affected rows; no summing.');
  commit;
 end if;
exception when others then rollback; raise;
end;
/
declare n number;
begin
 for c in(select COLUMN_NAME from user_tab_columns where TABLE_NAME='RRL_REMAINS'
           and COLUMN_NAME in('CELL','UID_POLETA','REMAIN') and NULLABLE='Y') loop
  execute immediate 'alter table RRL_REMAINS modify ('||c.COLUMN_NAME||' not null)';
 end loop;
 select count(*) into n from user_constraints where CONSTRAINT_NAME='RRL_REMAINS_STOCK_UK';
 if n=0 then execute immediate 'alter table RRL_REMAINS add constraint RRL_REMAINS_STOCK_UK unique(UID_POLETA,CELL)'; end if;
 select count(*) into n from user_constraints where CONSTRAINT_NAME='RRL_REMAINS_QTY_CK';
 if n=0 then execute immediate 'alter table RRL_REMAINS add constraint RRL_REMAINS_QTY_CK check(REMAIN>=0)'; end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-013-stock-dev-cleanup' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Authorized dev stock cleanup with row archive and exact key',sysdate,user,'013_apply.sql','013_rollback.sql','APPLIED');
commit;