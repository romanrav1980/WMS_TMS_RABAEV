create or replace package RRL_TT_MEMBERSHIP_CTX_API authid definer
 accessible by(function RRL_TT_ADD_PALL) as
 procedure begin_member(p_id number,p_trip number);
 procedure end_member;
end;
/
create or replace package body RRL_TT_MEMBERSHIP_CTX_API as
 procedure begin_member(p_id number,p_trip number) is
 begin
  if sys_context('RRL_TT_MEMBERSHIP_CTX','ST_ID') is not null then raise_application_error(-20886,'NESTED_TRIP_MEMBERSHIP_WRITE');end if;
  dbms_session.set_context('RRL_TT_MEMBERSHIP_CTX','ST_ID',to_char(p_id,'TM9'));
  dbms_session.set_context('RRL_TT_MEMBERSHIP_CTX','TRIP_ID',to_char(nvl(p_trip,0),'TM9'));
  dbms_session.set_context('RRL_TT_MEMBERSHIP_CTX','TX_ID',dbms_transaction.local_transaction_id(false));
 end;
 procedure end_member is
 begin
  dbms_session.set_context('RRL_TT_MEMBERSHIP_CTX','ST_ID',null);
  dbms_session.set_context('RRL_TT_MEMBERSHIP_CTX','TRIP_ID',null);
  dbms_session.set_context('RRL_TT_MEMBERSHIP_CTX','TX_ID',null);
 end;
end;
/
create or replace context RRL_TT_MEMBERSHIP_CTX using RABAEV.RRL_TT_MEMBERSHIP_CTX_API;
