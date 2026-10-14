declare n number;begin select count(*)into n from(select OPERATION_ID from RRL_IW_RECOVERY_DISPATCH group by OPERATION_ID having count(*)>1);if n>0 then raise_application_error(-20899,'CONSOLIDATED_RECOVERY_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_next.sql
@@000_before_ship.sql
@@000_before_dispatch_guard.sql
alter table RRL_IW_RECOVERY_DISPATCH drop constraint RRL_IW_REC_DISPATCH_PK;
alter table RRL_IW_RECOVERY_DISPATCH add constraint SYS_C0018245 primary key(OPERATION_ID);
