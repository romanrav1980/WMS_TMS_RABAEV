declare n number;begin select count(*)into n from RRL_CLUSTER_CREATE_RESULT;
 if n>0 then raise_application_error(-20899,'CLUSTER139_HISTORY_REQUIRES_FORWARD_FIX');end if;end;
/
drop trigger RRL_CLUSTER_CREATE_GUARD;
drop package RRL_CLUSTER_CREATE_API;
drop table RRL_CLUSTER_CREATE_RESULT;
/
