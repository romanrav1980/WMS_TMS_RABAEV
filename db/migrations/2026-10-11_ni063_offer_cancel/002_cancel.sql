create or replace package RRL_STOCK_TARE_CANCEL_CMD authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure assert_scope(p_request clob,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_TARE_CANCEL_CMD as
 procedure assert_scope(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);o RRL_TARE_OFFER%rowtype;t RRL_TRANSPORT_TASK%rowtype;n number;offer_id varchar2(100);
 begin
  offer_id:=d.get_object('source').get_string('offer_operation_id');
  select *into o from RRL_TARE_OFFER where OPERATION_ID=offer_id;
  select *into t from RRL_TRANSPORT_TASK where ID=o.TT_ID;
  if RRL_HAS_WRIGHT(p_actor,'tare_offer')!=1 then raise_application_error(-20882,'TARE_CANCEL_CURRENT_PERMISSION_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and upper(trim(USER_GROUP))='GLOBAL_ADMIN';
  if n=0 then
   if p_actor!=o.OFFERED_BY then raise_application_error(-20882,'TARE_CANCEL_ORIGINAL_SENDER_REQUIRED');end if;
   RRL_TARE_PARTICIPANT.holder_actor(p_actor,o.FROM_KIND,o.FROM_ID,o.OWNER_WARE_ID,t,'tare_offer');
  end if;
 exception when no_data_found then raise_application_error(-20886,'TARE_CANCEL_ORIGINAL_OFFER_REQUIRED');end;
 function describe_command(p_request clob,p_actor varchar2)return json_object_t is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');j json_object_t:=json_object_t();a json_array_t:=json_array_t();x json_object_t;
  id varchar2(100):=d.get_object('source').get_string('offer_operation_id');o RRL_TARE_OFFER%rowtype;t RRL_TRANSPORT_TASK%rowtype;veh RRL_TR_VEHICLE%rowtype;n number;
 begin
  assert_scope(p_request,p_actor);select *into o from RRL_TARE_OFFER where OPERATION_ID=id;
  select count(*)into n from RRL_TARE_ACCEPT where OFFER_OPERATION_ID=id;
  if n!=0 then raise_application_error(-20886,'TARE_CANCEL_ACCEPTED_RETURN_REQUIRED');end if;
  select count(*)into n from RRL_TARE_OFFER_CANCEL where OFFER_OPERATION_ID=id;
  if n!=0 then raise_application_error(-20886,'TARE_OFFER_ALREADY_CANCELLED');end if;
  if trim(m.get_string('reason'))is null or length(m.get_string('reason'))>500 or m.get_string('scan_vehicle')is null or m.get_string('scan_vehicle')!=o.VEHICLE_NUMBER then raise_application_error(-20886,'TARE_CANCEL_REASON_ORIGINAL_VEHICLE_SCAN_REQUIRED');end if;
  select *into t from RRL_TRANSPORT_TASK where ID=o.TT_ID;
  select *into veh from RRL_TR_VEHICLE where ID=o.VEHICLE_ID;
  if nvl(t.DELETED,0)!=0 or t.TRANSPORT!=o.VEHICLE_NUMBER or nvl(veh.DELETED,0)!=0 or veh.NUM!=o.VEHICLE_NUMBER then raise_application_error(-20886,'TARE_CANCEL_CURRENT_ORIGINAL_TRIP_REQUIRED');end if;
  for b in(select ob.BOOK_OPERATION_ID,ob.LOAD_OPERATION_ID,tb.STATUS,lf.STATUS LOAD_STATUS,lf.DEPARTURE_OPERATION_ID from RRL_TARE_OFFER_BOOK ob join RRL_TARE_BOOK tb on tb.OPERATION_ID=ob.BOOK_OPERATION_ID join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=ob.LOAD_OPERATION_ID where ob.OFFER_OPERATION_ID=id order by ob.BOOK_OPERATION_ID)loop
   if b.STATUS!='HELD'or b.LOAD_STATUS!='LOADED'or b.DEPARTURE_OPERATION_ID is not null then raise_application_error(-20886,'TARE_CANCEL_HELD_UNDEPARTED_BOOK_REQUIRED');end if;
   x:=json_object_t();x.put('book',b.BOOK_OPERATION_ID);x.put('load',b.LOAD_OPERATION_ID);a.append(x);
   if a.get_size>100 then raise_application_error(-20881,'TARE_CANCEL_BOOK_BOUND_100');end if;
  end loop;
  j.put('offer_operation_id',id);j.put('task_id',o.TT_ID);j.put('vehicle_id',o.VEHICLE_ID);j.put('warehouse_id',o.OWNER_WARE_ID);j.put('books',a);j.put('reason',m.get_string('reason'));j.put('vehicle',o.VEHICLE_NUMBER);return j;
 exception when no_data_found then raise_application_error(-20886,'TARE_CANCEL_ORIGINAL_CONTEXT_REQUIRED');end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;x json_object_t;
 begin
  v:=describe_command(p_request,d.get_string('actor'));RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',v.get_string('offer_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER_CANCEL',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRANSPORT_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('task_id')));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TR_VEHICLE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('vehicle_id')));
  a:=v.get_array('books');
  for i in 0..a.get_size-1 loop x:=treat(a.get(i)as json_object_t);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',x.get_string('book'));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',x.get_string('load'));
  end loop;
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');wire clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();offer_id varchar2(100);reason_value nvarchar2(500);
 begin
  select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(wire).get_object('domain');
  fresh:=describe_command(p_request,p_actor);
  if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: tare cancellation');end if;
  offer_id:=v.get_string('offer_operation_id');reason_value:=v.get_string('reason');
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_OFFER',offer_id));
  insert into RRL_TARE_OFFER_CANCEL(OPERATION_ID,OFFER_OPERATION_ID,REASON,CANCELLED_BY)values(op,offer_id,reason_value,p_actor);
  j.put('operation_id',op);j.put('offer_operation_id',offer_id);j.put('status','CANCELLED');j.put('tare_balance_changed',false);j.put('original_offer_preserved',true);p_result:=j.to_clob;
 end;
end;
/
