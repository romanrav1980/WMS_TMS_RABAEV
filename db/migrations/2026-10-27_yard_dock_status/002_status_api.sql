create or replace package RRL_YARD_DOCK_STATUS_API authid definer as
 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob);
 function docks(p_ware number,p_actor varchar2)return clob;
end;
/
create or replace package body RRL_YARD_DOCK_STATUS_API as
 procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;
 function sha(p_text clob)return varchar2 is begin return lower(rawtohex(sys.dbms_crypto.hash(p_text,sys.dbms_crypto.hash_sh256)));end;
 procedure require(p_actor varchar2,p_permission varchar2,p_ware number)is n number;
 begin select RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'YARD_ACCESS_DENIED');end if;end;
 procedure lock_site(p_ware number)is n number;
 begin
  lock table RRL_ACCESS_REV in share mode wait 5;
  select ENABLED into n from RRL_TRADE_SITE where WARE_ID=p_ware for update;
  if n<>1 then fail('TRADE_SITE_DISABLED');end if;
 exception when no_data_found then fail('TRADE_SITE_REQUIRED');end;
 function receipt(p_op varchar2,p_ware number,p_dock varchar2,p_blocked number,p_reason varchar2,p_at timestamp with time zone)return clob is j json_object_t:=json_object_t();
 begin j.put('operation_id',p_op);j.put('warehouse_id',p_ware);j.put('dock',p_dock);j.put('blocked',p_blocked=1);j.put('reason',p_reason);
  j.put('updated_at',to_char(p_at at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"'));return j.to_clob;end;
 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');dock_value varchar2(15):=trim(d.get_string('dock'));
  action_value varchar2(10):=d.get_string('action');reason_value varchar2(500):=trim(d.get_string('reason'));hash_value varchar2(64):=sha(p_request);
  e RRL_YARD_DOCK_STATUS_EVENT%rowtype;rid rowid;current_blocked number;n number;next_blocked number;now_value timestamp with time zone:=systimestamp;
 begin
  if op is null or lengthb(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$') or dock_value is null or lengthb(dock_value)>15
    or action_value is null or action_value not in('BLOCK','UNBLOCK')or reason_value is null or length(reason_value)<3 then fail('YARD_DOCK_STATUS_REQUEST_INVALID');end if;
  require(p_actor,'tradecase_yard_operate',p_ware);lock_site(p_ware);require(p_actor,'tradecase_yard_operate',p_ware);
  begin select*into e from RRL_YARD_DOCK_STATUS_EVENT where OPERATION_ID=op;
   if e.WARE_ID<>p_ware or e.ACTOR<>p_actor or e.REQUEST_HASH<>hash_value then fail('YARD_OPERATION_CONFLICT');end if;
   p_result:=e.RESULT_JSON;return;
  exception when no_data_found then null;end;
  select count(*)into n from RRL_TT_DOCK d where d.WARE_ID=p_ware and d.DOCK=dock_value;
  if n=0 then fail('YARD_DOCK_NOT_FOUND');elsif n>1 then fail('YARD_DOCK_AMBIGUOUS');end if;
  select d.rowid,nvl(d.DOCK_IS_BLOCKED,0)into rid,current_blocked from RRL_TT_DOCK d where d.WARE_ID=p_ware and d.DOCK=dock_value for update;
  if current_blocked not in(0,1)then fail('YARD_DOCK_STATUS_INVALID');end if;
  next_blocked:=case action_value when 'BLOCK'then 1 else 0 end;
  update RRL_TT_DOCK set DOCK_IS_BLOCKED=next_blocked where rowid=rid;
  p_result:=receipt(op,p_ware,dock_value,next_blocked,reason_value,now_value);
  insert into RRL_YARD_DOCK_STATUS_EVENT(OPERATION_ID,WARE_ID,DOCK,ACTION,BLOCKED,REASON,REQUEST_HASH,ACTOR,RESULT_JSON,CREATED_AT)
   values(op,p_ware,dock_value,action_value,next_blocked,reason_value,hash_value,p_actor,p_result,now_value);
 exception when dup_val_on_index then fail('YARD_OPERATION_CONFLICT');end;
 function docks(p_ware number,p_actor varchar2)return clob is a json_array_t:=json_array_t();j json_object_t;r json_object_t:=json_object_t();
 begin
  require(p_actor,'tradecase_view',p_ware);
  for x in(select DOCK,count(*)as DOCK_COUNT,max(nvl(DOCK_IS_BLOCKED,0))as BLOCKED,min(ORD)as FIRST_ORD
    from RRL_TT_DOCK where WARE_ID=p_ware group by DOCK order by min(ORD),DOCK)loop
   j:=json_object_t();j.put('dock',nvl(x.DOCK,'?'));j.put('ambiguous',x.DOCK_COUNT>1);
   if x.DOCK_COUNT>1 then j.put_null('blocked');j.put('status_error','YARD_DOCK_AMBIGUOUS');
   elsif x.DOCK is null or trim(x.DOCK)is null then j.put_null('blocked');j.put('status_error','YARD_DOCK_NAME_REQUIRED');
   elsif x.BLOCKED not in(0,1)then j.put_null('blocked');j.put('status_error','YARD_DOCK_STATUS_INVALID');
   else
    j.put('blocked',x.BLOCKED=1);
    for y in(select REASON,ACTOR,CREATED_AT from RRL_YARD_DOCK_STATUS_EVENT where WARE_ID=p_ware and DOCK=x.DOCK order by CREATED_AT desc,OPERATION_ID desc fetch first 1 rows only)loop
     j.put('reason',y.REASON);j.put('updated_by',y.ACTOR);j.put('updated_at',to_char(y.CREATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"'));
    end loop;
   end if;
   a.append(j);
  end loop;
  r.put('warehouse_id',p_ware);r.put('docks',a);return r.to_clob;
 end;
end;
/
