prompt Isolated restore only, refuses if the event journal or kept rows changed
declare n number; v_max number; v_current number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'RABAEV/orcl only'); end if;
 select JOURNAL_MAX_ID into v_max from RRL_STOCK_CLEANUP_LOG where CLEANUP_ID='2026-10-08-013-stock-dev-cleanup';
 select max(ID_EVENT) into v_current from RRL_EVENTS;
 if nvl(v_max,-1)!=nvl(v_current,-1) then raise_application_error(-20804,'Journal changed; use isolated recovery, not rollback'); end if;
 select count(*) into n from RRL_STOCK_CLEANUP_BAK_20261008 b where b.CLEANUP_ACTION='KEEP'
  and not exists(select 1 from RRL_REMAINS r where r.CELL=b.CELL and r.UID_POLETA=b.UID_POLETA
   and r.REMAIN=b.REMAIN and nvl(r.OTHOD_NAKL_ID,-1)=nvl(b.OTHOD_NAKL_ID,-1)
   and (r.TIME_OF_LAST_UPDATE=b.TIME_OF_LAST_UPDATE or(r.TIME_OF_LAST_UPDATE is null and b.TIME_OF_LAST_UPDATE is null)));
 if n>0 then raise_application_error(-20805,'Kept balances changed; restore refused'); end if;
 select count(*) into n from user_constraints where CONSTRAINT_NAME='RRL_REMAINS_HARD_CK';
 if n>0 then raise_application_error(-20806,'Posting schema installed; rollback cleanup before kernel or restore checkpoint'); end if;
end;
/
alter table RRL_REMAINS drop constraint RRL_REMAINS_STOCK_UK;
alter table RRL_REMAINS drop constraint RRL_REMAINS_QTY_CK;
alter table RRL_REMAINS modify(CELL null,UID_POLETA null,REMAIN null);
lock table RRL_REMAINS in exclusive mode wait 10;
insert into RRL_REMAINS(CELL,UID_POLETA,REMAIN,OTHOD_NAKL_ID,TIME_OF_LAST_UPDATE)
 select CELL,UID_POLETA,REMAIN,OTHOD_NAKL_ID,TIME_OF_LAST_UPDATE from RRL_STOCK_CLEANUP_BAK_20261008 where CLEANUP_ACTION='DELETE';
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-08-013-stock-dev-cleanup';
commit;