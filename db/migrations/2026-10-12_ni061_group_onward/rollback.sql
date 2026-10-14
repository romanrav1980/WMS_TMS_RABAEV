declare n number;begin select count(*)into n from RRL_IW_GROUP_ONWARD;if n!=0 then raise_application_error(-20899,'GROUP_ONWARD_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@000_before_next.sql
@@000_before_ship.sql
drop trigger RRL_IW_GROUP_DISPATCH_GUARD;
drop trigger RRL_IW_GROUP_ST_BIND_GUARD;
drop trigger RRL_IW_GROUP_ONWARD_GUARD;
drop package RRL_IW_GROUP_NEXT;
drop table RRL_IW_GROUP_DISPATCH;
drop table RRL_IW_GROUP_ST_BIND;
drop table RRL_IW_GROUP_ONWARD;
