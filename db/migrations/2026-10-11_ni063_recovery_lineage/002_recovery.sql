create or replace package RRL_TARE_LOAD_RECOVERY_API authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TARE_BOOK_CMD,package RRL_STOCK_UNLOAD_CMD)as
 procedure assert_scope(p_request clob,p_actor varchar2);
 function describe_recovery(p_request clob,p_actor varchar2)return clob;
 procedure declare_recovery(p_domain clob,p_operation varchar2,r in out nocopy json_array_t);
 procedure record_recovery(p_domain clob,p_operation varchar2,p_actor varchar2);
end;
/

create or replace package body RRL_TARE_LOAD_RECOVERY_API as
 procedure assert_scope(p_request clob,p_actor varchar2)is d json_object_t:=json_object_t.parse(p_request);m json_object_t;v json_object_t;book_id varchar2(100);ware number;
 begin
  if d.get_string('command_type')!='TARE_BOOK'then return;end if;m:=d.get_object('metadata');
  if not m.has('load_recovery')or m.get('load_recovery').is_null then return;end if;
  if RRL_HAS_WRIGHT(p_actor,'tare_plan')!=1 then raise_application_error(-20882,'TARE_RECOVERY_PLANNING_PERMISSION_REQUIRED');end if;
  v:=m.get_object('load_recovery');book_id:=v.get_string('original_booking_operation_id');
  select OWNER_WARE_ID into ware from RRL_TARE_BOOK where OPERATION_ID=book_id;
  RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,ware);
 end;
 function describe_recovery(p_request clob,p_actor varchar2)return clob is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');s json_object_t:=d.get_object('source');v json_object_t;j json_object_t:=json_object_t();
  old_book RRL_TARE_BOOK%rowtype;load_fact RRL_TT_HU_LOAD_FACT%rowtype;old_offer RRL_TARE_OFFER%rowtype;back_offer RRL_TARE_OFFER%rowtype;back_accept RRL_TARE_ACCEPT%rowtype;old_accept RRL_TARE_ACCEPT%rowtype;ct RRL_CASE_PICK_TASK%rowtype;
  load_id varchar2(100);book_id varchar2(100);return_id varchar2(100);old_offer_id varchar2(100);case_id number;n number;wire clob;scan_value varchar2(200);original_version number;pp RRL_PALLETS%rowtype;root_uid varchar2(150);root_kind varchar2(20);cell_value varchar2(60);p_total number;h_total number;stock_version number;task_id number;wave_id number;ff_id number;order_id number;node json_object_t;tree json_object_t;
 begin
  assert_scope(p_request,p_actor);v:=m.get_object('load_recovery');load_id:=v.get_string('load_operation_id');book_id:=v.get_string('original_booking_operation_id');return_id:=v.get_string('return_offer_operation_id');
  select *into old_book from RRL_TARE_BOOK where OPERATION_ID=book_id;
  if old_book.STATUS!='TRANSFERRED'or old_book.PLACE_KIND not in('CASE','HU')or old_book.QUANTITY!=1 or s.get_string('place_kind')!=old_book.PLACE_KIND or s.get_string('place_id')!=old_book.PLACE_ID then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_TRANSFERRED_PLACE_REQUIRED');end if;
  select *into load_fact from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=load_id;
  if load_fact.STATUS!='LOADED'or load_fact.DEPARTURE_OPERATION_ID is not null or load_fact.CUSTODY_RELEASE_OPERATION_ID is not null or old_book.OWNER_WARE_ID!=load_fact.WARE_ID or v.get_number('expected_load_version')is null or v.get_number('expected_load_version')!=load_fact.CONTENT_VERSION then raise_application_error(-20886,'TARE_RECOVERY_PREDEPARTURE_ORIGINAL_LOAD_REQUIRED');end if;
  select o.OPERATION_ID into old_offer_id from RRL_TARE_OFFER o join RRL_TARE_OFFER_BOOK b on b.OFFER_OPERATION_ID=o.OPERATION_ID join RRL_TARE_ACCEPT a on a.OFFER_OPERATION_ID=o.OPERATION_ID
   where b.LOAD_OPERATION_ID=load_id and b.BOOK_OPERATION_ID=book_id and a.OPERATION_ID=old_book.CLOSED_OPERATION_ID and a.ACCEPTED_QTY=o.QUANTITY;
  select *into old_offer from RRL_TARE_OFFER where OPERATION_ID=old_offer_id;
  select *into old_accept from RRL_TARE_ACCEPT where OPERATION_ID=old_book.CLOSED_OPERATION_ID;
  select *into back_offer from RRL_TARE_OFFER where OPERATION_ID=return_id;
  select *into back_accept from RRL_TARE_ACCEPT where OFFER_OPERATION_ID=return_id;
  if old_offer.FROM_KIND!='WAREHOUSE'or old_offer.TO_KIND!='VEHICLE'or old_offer.OWNER_WARE_ID!=load_fact.WARE_ID or old_offer.VEHICLE_ID!=load_fact.VEHICLE_ID or old_offer.TT_ID!=load_fact.TT_ID
   or back_offer.FROM_KIND!='VEHICLE'or back_offer.TO_KIND!='WAREHOUSE'or back_offer.FROM_BALANCE_KEY!=old_offer.TO_BALANCE_KEY or back_offer.TO_BALANCE_KEY!=old_book.BALANCE_KEY
   or back_offer.OWNER_WARE_ID!=old_book.OWNER_WARE_ID or back_offer.PALLET_TYPE_ID!=old_book.PALLET_TYPE_ID or back_offer.CONDITION_CODE!='GOOD'
   or back_offer.VEHICLE_ID!=load_fact.VEHICLE_ID or back_offer.TT_ID!=load_fact.TT_ID or back_offer.QUANTITY!=old_book.QUANTITY or back_accept.ACCEPTED_QTY!=old_book.QUANTITY or back_accept.SHORT_QTY!=0
   or back_offer.OFFERED_AT<old_accept.ACCEPTED_AT or back_accept.ACCEPTED_AT<back_offer.OFFERED_AT
   or back_accept.ACCEPTED_BY=back_offer.OFFERED_BY then raise_application_error(-20886,'TARE_RECOVERY_EXACT_ACCEPTED_VEHICLE_RETURN_REQUIRED');end if;
  if old_book.PLACE_KIND='CASE'then
  case_id:=to_number(old_book.PLACE_ID);select *into ct from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id;
  if ct.STATUS!='SHIPPED'or ct.SHIPPED_OPERATION!=load_id or ct.WARE_ID!=old_book.OWNER_WARE_ID or ct.PALLET_TYPE_ID!=old_book.PALLET_TYPE_ID then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_CASE_OWNER_REQUIRED');end if;
  wire:=load_fact.COMPOSITION_JSON;
  select count(*),max(S),max(V)into n,scan_value,original_version from json_table(wire,'$.nodes[*]'columns(K varchar2(20)path '$.kind',C number path '$.case_task_id',S varchar2(200)path '$.sscc',V number path '$.version'))where K='CASE'and C=case_id;
  if n!=1 or ct.CONTENT_VERSION!=original_version+1 or v.get_string('scan_place')is null or v.get_string('scan_place')!=scan_value then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_CASE_SCAN_EPOCH_REQUIRED');end if;
  else
   root_uid:=old_book.PLACE_ID;
   if load_fact.ROOT_UID is null or load_fact.ROOT_UID!=root_uid or load_fact.ROOT_CASE_TASK_ID is not null then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_WHOLE_ROOT_REQUIRED');end if;
   tree:=json_object_t.parse(load_fact.COMPOSITION_JSON);node:=treat(tree.get_array('nodes').get(0)as json_object_t);
   root_kind:=node.get_string('kind');original_version:=node.get_number('version');cell_value:=tree.get_string('cell');
   if node.get_string('uid')!=root_uid or root_kind not in('CONTAINER','STOCK')then raise_application_error(-20886,'TARE_RECOVERY_ARCHIVED_ROOT_KIND_REQUIRED');end if;
   scan_value:=nvl(node.get_string('sscc'),root_uid);
   if v.get_string('scan_place')is null or v.get_string('scan_place')!=scan_value then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_ROOT_SCAN_REQUIRED');end if;
   select *into pp from RRL_PALLETS where UID_PALLET=root_uid;
   if nvl(pp.HU_KIND,'STOCK')!=root_kind then raise_application_error(-20886,'TARE_RECOVERY_CURRENT_ROOT_KIND_REQUIRED');end if;
   select count(*)into n from RRL_WMS_HU_LINK where CHILD_PALLET_UID=root_uid and ACTIVE_FLAG=1;
   if n!=0 then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_ROOT_NOT_FREE');end if;
   if root_kind='CONTAINER'then
    if pp.HU_SHIPPED_OPERATION is null or pp.HU_SHIPPED_OPERATION!=load_id or pp.HU_CONTENT_VERSION!=original_version+1 or pp.HU_CURRENT_CELL is not null then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_CONTAINER_EPOCH_REQUIRED');end if;
   else
    select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)into p_total,h_total from RRL_REMAINS where UID_POLETA=root_uid;
    if p_total!=0 or h_total!=0 or pp.HU_CONTENT_VERSION!=original_version then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_FULLPAL_ZERO_EPOCH_REQUIRED');end if;
    select count(*),max(PICKED_WAREHOUSE_TASK_ID),max(FULFILLMENT_ID),max(CUSTOMER_ORDER_ID)into n,task_id,ff_id,order_id from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_CASE_TASK_ID is null and PICKED_PALLET_UID=root_uid and STATUS='SHIPPED'and SHIPPED_OPERATION_ID=load_id;
    if n!=1 or task_id is null then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_FULLPAL_BIND_REQUIRED');end if;
    select count(*),max(SOURCE_DOC_ID)into n,wave_id from RRL_WAREHOUSE_TASK where TASK_ID=task_id and STATUS='DONE'and TASK_TYPE='PICKING_MOVE'and UID_PALLET=root_uid and SOURCE_DOC_TYPE='PICK_WAVE'and TO_WARE_ID=load_fact.WARE_ID;
    if n!=1 then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_FULLPAL_TASK_REQUIRED');end if;
    select count(*)into n from RRL_PICK_WAVE where PICK_WAVE_ID=wave_id and STATUS='LAUNCHED';
    if n!=1 then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_FULLPAL_WAVE_REQUIRED');end if;
    select STOCK_VERSION into stock_version from RRL_REMAINS where UID_POLETA=root_uid and CELL=cell_value;
   end if;
   select count(*)into n from RRL_CELLS where CELL=cell_value and WARE_ID=load_fact.WARE_ID;
   if n!=1 then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_ROOT_CELL_WARE_REQUIRED');end if;
   j.put('root_uid',root_uid);j.put('root_kind',root_kind);j.put('root_cell',cell_value);j.put('root_article',pp.ARTICUL);j.put('root_stock_version',stock_version);j.put('root_version',pp.HU_CONTENT_VERSION);
   j.put('fullpal_fulfillment_id',ff_id);j.put('fullpal_order_id',order_id);j.put('fullpal_task_id',task_id);j.put('fullpal_wave_id',wave_id);
  end if;
  j.put('place_kind',old_book.PLACE_KIND);j.put('place_id',old_book.PLACE_ID);
  select count(*)into n from RRL_TARE_LOAD_RECOVERY where ORIGINAL_BOOK_OPERATION_ID=book_id or RETURN_OFFER_OPERATION_ID=return_id or RETURN_ACCEPT_OPERATION_ID=back_accept.OPERATION_ID;
  if n!=0 then raise_application_error(-20886,'TARE_RECOVERY_SOURCE_ALREADY_USED');end if;
  j.put('load_operation_id',load_id);j.put('original_booking_operation_id',book_id);j.put('return_offer_operation_id',return_id);j.put('return_accept_operation_id',back_accept.OPERATION_ID);j.put('original_offer_operation_id',old_offer_id);
  j.put('warehouse_id',old_book.OWNER_WARE_ID);j.put('pallet_type_id',old_book.PALLET_TYPE_ID);j.put('case_id',case_id);j.put('case_version',ct.CONTENT_VERSION);j.put('balance_key',rawtohex(old_book.BALANCE_KEY));j.put('load_version',load_fact.CONTENT_VERSION);
  return j.to_clob;
 exception when no_data_found then raise_application_error(-20886,'TARE_RECOVERY_ORIGINAL_ACCEPTED_RETURN_REQUIRED');end;
 procedure declare_recovery(p_domain clob,p_operation varchar2,r in out nocopy json_array_t)is v json_object_t:=json_object_t.parse(p_domain);
 begin
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_LOAD_RECOVERY',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BOOK',v.get_string('original_booking_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',v.get_string('load_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',v.get_string('original_offer_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_OFFER',v.get_string('return_offer_operation_id'));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_ACCEPT',v.get_string('return_accept_operation_id'));
  if v.get_string('place_kind')='CASE'then
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU','CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('case_id')));
  else
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v.get_string('root_uid'));
   if v.get_number('fullpal_task_id')is not null then
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_FULFILLMENT',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fullpal_fulfillment_id')));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fullpal_order_id')));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fullpal_task_id')));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_WAVE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('fullpal_wave_id')));
   end if;
  end if;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TARE.RECOVER.BOOK:'||v.get_string('original_booking_operation_id'));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','TARE.RECOVER.RETURN:'||v.get_string('return_offer_operation_id'));
 end;
 procedure record_recovery(p_domain clob,p_operation varchar2,p_actor varchar2)is
  v json_object_t:=json_object_t.parse(p_domain);load_id varchar2(100):=v.get_string('load_operation_id');book_id varchar2(100):=v.get_string('original_booking_operation_id');return_id varchar2(100):=v.get_string('return_offer_operation_id');accept_id varchar2(100):=v.get_string('return_accept_operation_id');ware number:=v.get_number('warehouse_id');typ number:=v.get_number('pallet_type_id');ct number:=v.get_number('case_id');root_id varchar2(150):=v.get_string('root_uid');
 begin
  insert into RRL_TARE_LOAD_RECOVERY(OPERATION_ID,LOAD_OPERATION_ID,ORIGINAL_BOOK_OPERATION_ID,RETURN_OFFER_OPERATION_ID,RETURN_ACCEPT_OPERATION_ID,WARE_ID,PALLET_TYPE_ID,CASE_PICK_TASK_ID,ROOT_UID,CREATED_BY)values(p_operation,load_id,book_id,return_id,accept_id,ware,typ,ct,root_id,p_actor);
 end;
end;
/
