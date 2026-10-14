declare n number;begin
 select count(*)into n from RRL_TT_TIME_APPROVAL;
 if n>0 then raise_application_error(-20886,'TT_TIME_APPROVAL_FACTS_REMAIN_NO_DROP');end if;
end;
/
drop trigger RRL_TT_TIME_APPROVAL_GUARD;
/
drop package RRL_TT_TIME_API;
/
drop table RRL_TT_TIME_APPROVAL;
/
@000_before_rrl_transport_edit_api.sql
