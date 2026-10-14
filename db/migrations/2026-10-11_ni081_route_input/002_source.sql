create or replace package RRL_TT_ROUTE_SOURCE authid definer as
 procedure snapshot(p_trip number,p_actor varchar2,p_source out clob,p_hash out varchar2);
 procedure durations(p_trip number,p_actor varchar2,p_drive out number,p_back out number,p_basis out varchar2);
end;
/
create or replace package body RRL_TT_ROUTE_SOURCE as
 procedure snapshot(p_trip number,p_actor varchar2,p_source out clob,p_hash out varchar2)is
  v_context clob;b json_object_t;s json_object_t;
 begin
  RRL_TT_TIME_API.context(p_trip,p_actor,v_context);
  b:=json_object_t.parse(v_context);s:=b.get_object('source');s.remove('operations');
  p_source:=s.to_clob;p_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_source,sys.dbms_crypto.hash_sh256)));
 end;
 procedure durations(p_trip number,p_actor varchar2,p_drive out number,p_back out number,p_basis out varchar2)is
  src clob;hash varchar2(64);saved RRL_TT_ROUTE_INPUT%rowtype;
 begin
  p_drive:=null;p_back:=null;p_basis:='CONFIGURED_NORMS_ESTIMATE';
  snapshot(p_trip,p_actor,src,hash);
  begin select *into saved from RRL_TT_ROUTE_INPUT where TT_ID=p_trip and VERSION_NO=(select max(VERSION_NO)from RRL_TT_ROUTE_INPUT where TT_ID=p_trip);
   if saved.SOURCE_HASH=hash then p_drive:=saved.DRIVE_MIN;p_back:=saved.DRIVE_BACK_MIN;p_basis:='MANUAL_DISPATCH_ESTIMATE';end if;
  exception when no_data_found then null;end;
 end;
end;
/
