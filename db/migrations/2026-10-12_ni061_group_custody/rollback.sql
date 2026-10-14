declare n number;begin select count(*)into n from RRL_IW_GROUP_CUSTODY;if n!=0 then raise_application_error(-20899,'GROUP_CUSTODY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_custody.sql
@@000_before_load_guard.sql
drop trigger RRL_IW_GROUP_CUSTODY_GUARD;
drop package RRL_IW_GROUP_CUSTODY_CORE;
drop table RRL_IW_GROUP_CUSTODY;
