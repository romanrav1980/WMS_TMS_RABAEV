create or replace package body RRL_IW_CASE_BRIDGE as
 function source_cases(p_load varchar2,p_tree clob)return clob is
  tree json_object_t:=json_object_t.parse(p_tree);nodes json_array_t:=tree.get_array('nodes');x json_object_t;j json_object_t;
  result_value json_array_t:=json_array_t();ct RRL_CASE_PICK_TASK%rowtype;lf RRL_TT_HU_LOAD_FACT%rowtype;
  n number;members number;matched number;books number;book_wire clob;carrier varchar2(200);uid_value varchar2(200);tare_value varchar2(60);
 begin
  if nodes.get_size>200 then raise_application_error(-20881,'INTERWARE_CASE_NODE_BOUND_200');end if;
  select *into lf from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load and STATUS='DEPARTED';
  for i in 0..nodes.get_size-1 loop
   x:=treat(nodes.get(i)as json_object_t);
   if x.get_string('kind')='CASE'then
    select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=x.get_number('case_task_id');
    if ct.STATUS!='SHIPPED'or ct.SHIPPED_OPERATION!=p_load or ct.WARE_ID!=lf.WARE_ID or ct.SSCC is null
     or ct.SSCC!=x.get_string('sscc')or ct.CONTENT_VERSION!=x.get_number('version')+1 then
     raise_application_error(-20886,'INTERWARE_CASE_FROZEN_HISTORY_REQUIRED');end if;
    select count(*)into n from RRL_WMS_HU_LINK where CHILD_CASE_TASK_ID=ct.CASE_PICK_TASK_ID and ACTIVE_FLAG=1;
    if n!=0 then raise_application_error(-20886,'INTERWARE_CASE_ALREADY_PHYSICALLY_LINKED');end if;
    select count(*)into members from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID;
    select count(*)into matched from json_table(p_tree,'$.nodes[*]'columns(K varchar2(20)path '$.kind',C number path '$.case_task_id',U varchar2(200)path '$.uid'))j
     join RRL_CASE_CARRIER_LOT l on l.LOT_UID=j.U and l.CASE_PICK_TASK_ID=j.C where j.K='STOCK'and j.C=ct.CASE_PICK_TASK_ID;
    if members<1 or matched!=members then raise_application_error(-20886,'INTERWARE_CASE_EXACT_FROZEN_LEAVES_REQUIRED');end if;
    carrier:='IW.CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(ct.CASE_PICK_TASK_ID)||':'||substr(lower(rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_load,'AL32UTF8'),sys.dbms_crypto.hash_sh256))),1,24);
    select count(*)into n from RRL_IW_CASE_CARRIER where CASE_TASK_ID=ct.CASE_PICK_TASK_ID or CARRIER_UID=carrier;
    if n!=0 then raise_application_error(-20886,'INTERWARE_CASE_ALREADY_RECEIVED');end if;
    select count(*)into n from RRL_PALLETS where UID_PALLET=carrier or SSCC=ct.SSCC;
    if n!=0 then raise_application_error(-20886,'INTERWARE_CASE_IDENTIFIER_ALREADY_BOUND');end if;
    select count(*),json_arrayagg(json_object('operation_id'value OPERATION_ID,'owner_warehouse_id'value OWNER_WARE_ID,'pallet_type_id'value PALLET_TYPE_ID,'status'value STATUS)order by OPERATION_ID returning clob)
     into books,book_wire from RRL_TARE_BOOK where PLACE_KIND='CASE'and PLACE_ID=RRL_STOCK_PLAN_HELPER.decimal_text(ct.CASE_PICK_TASK_ID)and STATUS='HELD';
    if books>1 then raise_application_error(-20886,'INTERWARE_CASE_ONE_SOURCE_TARE_BOOK_REQUIRED');end if;
    tare_value:=x.get_string('tare_weight_kg');
    j:=json_object_t();j.put('case_task_id',ct.CASE_PICK_TASK_ID);j.put('source_uid',x.get_string('uid'));j.put('carrier_uid',carrier);
    j.put('pallet_identifier',ct.SSCC);j.put('source_case_version',ct.CONTENT_VERSION);j.put('source_warehouse_id',ct.WARE_ID);
    j.put('source_wave_id',ct.PICK_WAVE_ID);j.put('source_st_id',ct.LEGACY_SBORKA_PALLET_ID);j.put('source_load_operation_id',p_load);
    j.put('tare_weight_kg',tare_value);j.put('source_tare_books',json_array_t.parse(nvl(book_wire,'[]')));
    if x.has('scale_qc')then j.put('historical_scale_evidence',x.get_object('scale_qc'));end if;
    result_value.append(j);
   end if;
  end loop;
  return result_value.to_clob;
 end;
 function origin_json(p_uid varchar2)return clob is wire clob;
 begin select SOURCE_JSON into wire from RRL_IW_CASE_CARRIER where CARRIER_UID=p_uid;return wire;
 exception when no_data_found then return null;end;
 function historical_member(p_uid varchar2)return number is n number;
 begin
  select count(*)into n from RRL_CASE_CARRIER_LOT l join RRL_IW_CASE_CARRIER m on m.CASE_TASK_ID=l.CASE_PICK_TASK_ID
   join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=m.CASE_TASK_ID and t.STATUS='SHIPPED'and t.SHIPPED_OPERATION=m.SOURCE_LOAD_OPERATION_ID
   where l.LOT_UID=p_uid;
  return case when n=1 then 1 else 0 end;
 end;
 procedure assert_container(p_uid varchar2,p_type varchar2,p_cell varchar2,p_tare number,p_identifier varchar2)is
  op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');wire clob;kind_value varchar2(80);state_value varchar2(20);n number;cell_value varchar2(60);
 begin
  if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then
   raise_application_error(-20863,'INTERWARE_CASE_CARRIER_ROOT_REQUIRED');end if;
  select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_value,state_value,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
  cell_value:=json_object_t.parse(wire).get_object('domain').get_string('receive_cell');
  select count(*)into n from json_table(wire,'$.domain.nested_source.received_cases[*]'columns(U varchar2(200)path '$.carrier_uid',S varchar2(64)path '$.pallet_identifier',T varchar2(60)path '$.tare_weight_kg'))j
   where U=p_uid and S=p_identifier and case when T is null then 0 else RRL_STOCK_MATH.quantity(T)end=p_tare;
  if kind_value!='INTERWARE_RECEIVE'or state_value!='IN_FLIGHT'or n!=1 or nvl(p_type,'-')!='PALLET'or p_cell is null or p_cell!=cell_value then
   raise_application_error(-20863,'INTERWARE_CASE_EXACT_CARRIER_PLAN_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',p_uid));
 end;
 procedure restore(p_domain json_object_t,p_operation varchar2,p_actor varchar2)is
  a json_array_t;x json_object_t;uid_value varchar2(200);id_value varchar2(64);cell_value varchar2(60):=p_domain.get_string('receive_cell');
  source_load varchar2(100):=p_domain.get_string('source_load_operation_id');case_id number;source_version number;source_ware number;target_ware number:=p_domain.get_number('warehouse_id');
  wire clob;tare_value number;ct RRL_CASE_PICK_TASK%rowtype;
 begin
  if not p_domain.get_object('nested_source').has('received_cases')then return;end if;
  a:=p_domain.get_object('nested_source').get_array('received_cases');
  for i in 0..a.get_size-1 loop
   x:=treat(a.get(i)as json_object_t);case_id:=x.get_number('case_task_id');uid_value:=x.get_string('carrier_uid');id_value:=x.get_string('pallet_identifier');
   source_version:=x.get_number('source_case_version');source_ware:=x.get_number('source_warehouse_id');tare_value:=nvl(x.get_number('tare_weight_kg'),0);
   select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id;
   if ct.STATUS!='SHIPPED'or ct.SHIPPED_OPERATION!=source_load or ct.CONTENT_VERSION!=source_version or ct.SSCC!=id_value or ct.WARE_ID!=source_ware then
    raise_application_error(-20890,'CLOSURE_CHANGED: historical CASE receiving');end if;
   assert_container(uid_value,'PALLET',cell_value,tare_value,id_value);
   insert into RRL_PALLETS(UID_PALLET,ARTICUL,UNIT_COUNT,PRIHOD_NAKLAD_ID,CREATION_DATE,HU_KIND,HU_TYPE,HU_CONTENT_VERSION,HU_CURRENT_CELL,HU_TARE_WEIGHT_KG,SSCC,CREATED_BY_STOCK_OP)
    values(uid_value,null,0,0,sysdate,'CONTAINER','PALLET',0,cell_value,tare_value,id_value,p_operation);
   wire:=x.to_clob;
   insert into RRL_IW_CASE_CARRIER(CARRIER_UID,CASE_TASK_ID,SOURCE_LOAD_OPERATION_ID,RECEIPT_OPERATION_ID,SOURCE_WARE_ID,TARGET_WARE_ID,PALLET_IDENTIFIER,SOURCE_CASE_VERSION,SOURCE_JSON,CREATED_BY)
    values(uid_value,case_id,source_load,p_operation,source_ware,target_ware,id_value,source_version,wire,p_actor);
  end loop;
 end;
end;
/
