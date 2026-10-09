-- Reverse physical receipt without deleting history or guessing consumed stock.
create or replace package RRL_STOCK_RECEIPT_REVERSE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_RECEIPT_REVERSE as
 function physical_rows(p_document number) return clob is
  a json_array_t:=json_array_t();x json_object_t;
 begin
  for r in(select s.UID_POLETA,s.CELL,s.REMAIN,s.HARD_RESERVED_BASE,s.STOCK_VERSION,s.BASE_UOM,p.ARTICUL
   from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
   where p.PRIHOD_NAKLAD_ID=p_document and s.REMAIN>0 order by s.UID_POLETA,s.CELL fetch first 201 rows only) loop
   if a.get_size=200 then raise_application_error(-20881,'RECEIPT_REVERSE_BATCH_BOUND');end if;
   x:=json_object_t();x.put('uid',r.UID_POLETA);x.put('cell',r.CELL);x.put('article',r.ARTICUL);
   x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.REMAIN));x.put('hard',RRL_STOCK_PLAN_HELPER.decimal_text(r.HARD_RESERVED_BASE));
   x.put('version',r.STOCK_VERSION);x.put('base',r.BASE_UOM);a.append(x);
  end loop;
  return a.to_clob;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t:=json_object_t();x json_object_t;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;
  doc number;ware number;sap varchar2(32);receive_cell varchar2(60);n number:=0;
 begin
  doc:=d.get_object('source').get_number('receipt_document_id');
  if doc is null or doc<1 or trim(d.get_object('metadata').get_string('reason')) is null then raise_application_error(-20871,'RECEIPT_REVERSE_IDENTITY_REASON_REQUIRED');end if;
  select WARE_ID into ware from RRL_PRIHOD_NAKLAD where ID=doc;
  begin select ORDER_ID,RECEIVE_CELL into sap,receive_cell from RRL_SAP_SUPPLY_ORDER where NAKLAD_ID=doc;
  exception when no_data_found then sap:=null;receive_cell:='IN_DOCK';end;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(doc));
  if sap is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SAP_SUPPLY_ORDER',sap);end if;
  a:=json_array_t.parse(physical_rows(doc));
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),x.get_string('article'),x.get_string('cell'),null);
  end loop;
  for t in(select TASK_ID,TO_CELL_SLOT_ID from RRL_WAREHOUSE_TASK where TASK_SOURCE='SAP_RECEIPT' and SOURCE_DOC_ID=doc order by TASK_ID fetch first 201 rows only) loop
   n:=n+1;if n>200 then raise_application_error(-20881,'RECEIPT_REVERSE_TASK_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.TASK_ID));
   for c in(select CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=t.TASK_ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(t.TASK_ID));
    RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(c.CELL_SLOT_ID));
   end loop;
  end loop;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','SAP.REVERSE:'||p_operation);
  v.put('document',doc);v.put('warehouse',ware);v.put('sap_order',sap);v.put('receive_cell',receive_cell);v.put('stocks',a);
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;j json_object_t:=json_object_t();
  a json_array_t;facts json_array_t:=json_array_t();fact json_object_t;plan clob;nowrows clob;oldrows clob;
  doc number;ware number;cond number;op varchar2(100);uid varchar2(200);cell varchar2(60);base varchar2(20);
  qty number;ver number;event_id number;n number;expected number;actual number;sap varchar2(32);receive_cell varchar2(60);current_ware number;sap_sender varchar2(100);sap_number varchar2(100);
 begin
  if RRL_HAS_WRIGHT(p_actor,'stock_receipt_reverse')!=1 then raise_application_error(-20882,'RECEIPT_REVERSE_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(plan).get_object('domain');doc:=v.get_number('document');ware:=v.get_number('warehouse');
  sap:=v.get_string('sap_order');receive_cell:=v.get_string('receive_cell');a:=v.get_array('stocks');
  select CONDITION,WARE_ID into cond,current_ware from RRL_PRIHOD_NAKLAD where ID=doc for update;
  if current_ware!=ware or current_ware is null then raise_application_error(-20890,'CLOSURE_CHANGED: receipt warehouse');end if;
  if cond is null or cond not in(0,1,2) then raise_application_error(-20886,'RECEIPT_REVERSE_DOCUMENT_STATE');end if;
  nowrows:=physical_rows(doc);oldrows:=a.to_clob;
  if dbms_lob.compare(nowrows,oldrows)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: receipt stock');end if;
  select count(*) into n from RRL_EVENTS e join RRL_PALLETS p on p.UID_PALLET=e.UID_POLETA
   where p.PRIHOD_NAKLAD_ID=doc and e.TYPE_EVENT=3;
  if n>0 then raise_application_error(-20886,'RECEIPT_REVERSE_SUBSEQUENT_ISSUE: explicit correction required');end if;
  -- Original admitted quantity must still exist, including every derived lot.
  -- No automatic reversal after consumption/shipment or an unrecorded shortage.
  expected:=0;
  for born in(select p.UID_PALLET,p.UNIT_COUNT from RRL_PALLETS p
   where p.PRIHOD_NAKLAD_ID=doc and (p.STOCK_ORIGIN_UID=p.UID_PALLET or p.STOCK_ORIGIN_UID is null)
    and (p.CREATED_BY_STOCK_OP is not null or exists(select 1 from RRL_EVENTS e
     where e.UID_POLETA=p.UID_PALLET and e.TYPE_EVENT=1 and e.COUNT_EVENT>0))) loop
   select nvl(sum(s.REMAIN),0) into actual from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
    where p.PRIHOD_NAKLAD_ID=doc and nvl(p.STOCK_ORIGIN_UID,p.UID_PALLET)=born.UID_PALLET;
   expected:=expected+nvl(born.UNIT_COUNT,0);
   if born.UNIT_COUNT is null or born.UNIT_COUNT<=0 or actual!=born.UNIT_COUNT then raise_application_error(-20886,'RECEIPT_REVERSE_SUBSEQUENT_EFFECT: explicit correction required');end if;
  end loop;
  select nvl(sum(s.REMAIN),0) into actual from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA
   where p.PRIHOD_NAKLAD_ID=doc and s.REMAIN>0;
  if actual!=expected then raise_application_error(-20886,'RECEIPT_REVERSE_UNPROVEN_ORIGIN');end if;
  if a.get_size=0 then raise_application_error(-20886,'RECEIPT_REVERSE_NO_PHYSICAL_STOCK');end if;
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i) as json_object_t);uid:=x.get_string('uid');cell:=x.get_string('cell');base:=x.get_string('base');
   qty:=RRL_STOCK_MATH.quantity(x.get_string('quantity'));
   if cell!=receive_cell or x.get_string('hard')!='0' then raise_application_error(-20869,'RECEIPT_REVERSE_LOCATION_OR_RESERVE_CONFLICT');end if;
   RRL_STOCK_LOCATION_CORE.assert_quarantine(cell,ware);
   declare
 v_json_sql_1_1 varchar2(32767):=x.get_string('article');
begin
select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION
    where ARTICUL=v_json_sql_1_1 and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;
end;
   if ver is null then raise_application_error(-20868,'RECEIPT_REVERSE_BASE_POLICY_REQUIRED');end if;
   RRL_STOCK_UNIT_CORE.issue_free_units(uid,cell,qty,null);
   RRL_STOCK_BALANCE_CORE.apply_delta(uid,cell,-qty,0,base,ver,x.get_number('version'));
   RRL_STOCK_BALANCE_CORE.write_leg(uid,cell,null,-qty,base,ver,i+1,1,3,p_actor,event_id);
   fact:=json_object_t();fact.put('uid',uid);fact.put('article',x.get_string('article'));fact.put('quantity',x.get_string('quantity'));
   fact.put('unit',base);fact.put('event_id',event_id);facts.append(fact);
  end loop;
  for t in(select TASK_ID,STATUS from RRL_WAREHOUSE_TASK where TASK_SOURCE='SAP_RECEIPT' and SOURCE_DOC_ID=doc) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.TASK_ID)));
   if t.STATUS='IN_PROGRESS' then raise_application_error(-20886,'RECEIPT_REVERSE_TASK_IN_PROGRESS');end if;
   if t.STATUS in('PLANNED','ASSIGNED') then
    update RRL_WAREHOUSE_TASK set STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=p_actor,LAST_ERROR='Receipt reversed'
     where TASK_ID=t.TASK_ID;
    for c in(select CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=t.TASK_ID and STATUS='RESERVED') loop
     RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(t.TASK_ID)));
     RRL_STOCK_LOCK_API.assert_held(40,RRL_STOCK_LOCK_API.resource_key('SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(c.CELL_SLOT_ID)));
     delete from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=t.TASK_ID and STATUS='RESERVED';
    end loop;
   end if;
  end loop;
  update RRL_PRIHOD_NAKLAD set CONDITION=3 where ID=doc;
  j.put('operation_id',op);j.put('receipt_document_id',doc);j.put('sap_order_id',sap);j.put('status','REVERSED');j.put('facts',facts);
  if sap is not null then
   select SENDER,ORDER_NUMBER into sap_sender,sap_number from RRL_SAP_SUPPLY_ORDER where ORDER_ID=sap;
   j.put('sap_sender',sap_sender);j.put('sap_order_number',sap_number);
  end if;
  j.put('reason',d.get_object('metadata').get_string('reason'));p_result:=j.to_clob;
  if sap is not null then
   RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','SAP.REVERSE:'||op));
   insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON) values(op,'RECEIPT_REVERSED',p_result);
  end if;
 end;
end;
/
