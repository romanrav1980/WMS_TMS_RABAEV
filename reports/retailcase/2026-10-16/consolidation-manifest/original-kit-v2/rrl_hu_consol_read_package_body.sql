create or replace package body RRL_HU_CONSOL_READ as
 function digest(p_wire clob)return varchar2 is begin return rawtohex(sys.dbms_crypto.hash(p_wire,sys.dbms_crypto.hash_sh256));end;
 procedure assert_scope(p_actor nvarchar2,p_ware number,p_permission varchar2)is begin
  if p_permission is null or p_permission not in('warehouse_task_view','warehouse_task_execute')or p_ware is null or p_ware<1
   or nvl(RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(p_ware),null),0)!=1 then
   raise_application_error(-20882,'CONSOLIDATION_CURRENT_SCOPE_REQUIRED');end if;
 end;
 procedure assert_plan_scope(p_plan varchar2,p_actor nvarchar2,p_permission varchar2)is h RRL_HU_CONSOL_PLAN%rowtype;n number;begin
  select *into h from RRL_HU_CONSOL_PLAN where PLAN_ID=p_plan;assert_scope(p_actor,h.TARGET_WARE_ID,p_permission);
  select count(*)into n from RRL_HU_CONSOL_MEMBER where PLAN_ID=p_plan;if n>200 then raise_application_error(-20881,'CONSOLIDATION_MEMBER_BOUND_200');end if;
  for w in(select SOURCE_WARE_ID WARE from RRL_HU_CONSOL_MEMBER where PLAN_ID=p_plan union
   select st.WARE_ID from RRL_HU_CONSOL_MEMBER m join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.FULFILLMENT_ID=m.FULFILLMENT_ID
    join RRL_SBORKA_PALLETS st on st.ID=f.LEGACY_SBORKA_PALLET_ID where m.PLAN_ID=p_plan union
   select ct.WARE_ID from RRL_HU_CONSOL_MEMBER m join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.FULFILLMENT_ID=m.FULFILLMENT_ID
    join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=f.PICKED_CASE_TASK_ID where m.PLAN_ID=p_plan union
   select c.WARE_ID from RRL_PALLETS pp join RRL_CELLS c on c.CELL=pp.HU_CURRENT_CELL where pp.UID_PALLET=h.ROOT_UID)loop
   assert_scope(p_actor,w.WARE,'warehouse_task_view');
  end loop;
 end;
 function rows_signature(p_uid varchar2)return varchar2 is a json_array_t:=json_array_t();o json_object_t;begin
  for r in(select ID,ARTICUL,EI,QUANTITY,PACK_COUNT,ORDER_WEIGHT from RRL_SBORKA_PALLET_ROWS where PALLET_UID=p_uid order by ID fetch first 201 rows only)loop
   if a.get_size>=200 then raise_application_error(-20881,'CONSOLIDATION_ST_ROW_BOUND_200');end if;
   o:=json_object_t();o.put('id',r.ID);o.put('article',r.ARTICUL);o.put('unit',r.EI);
   o.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.QUANTITY));o.put('packs',RRL_STOCK_PLAN_HELPER.decimal_text(r.PACK_COUNT));
   o.put('order_weight',RRL_STOCK_PLAN_HELPER.decimal_text(r.ORDER_WEIGHT));a.append(o);
  end loop;
  if a.get_size=0 then raise_application_error(-20886,'CONSOLIDATION_PREPARED_ST_ROWS_REQUIRED');end if;return digest(a.to_clob);
 end;
 function frozen_plan(p_plan varchar2)return clob is h RRL_HU_CONSOL_PLAN%rowtype;j json_object_t:=json_object_t();a json_array_t:=json_array_t();o json_object_t;begin
  select *into h from RRL_HU_CONSOL_PLAN where PLAN_ID=p_plan;
  j.put('plan_id',h.PLAN_ID);j.put('version',h.PLAN_VERSION);j.put('root_identifier',h.ROOT_UID);j.put('warehouse_id',h.TARGET_WARE_ID);j.put('cell',h.TARGET_CELL);j.put('status',h.STATUS);
  for r in(select *from RRL_HU_CONSOL_MEMBER where PLAN_ID=p_plan order by FULFILLMENT_ID)loop
   if a.get_size>=200 then raise_application_error(-20881,'CONSOLIDATION_MEMBER_BOUND_200');end if;
   o:=json_object_t();o.put('fulfillment_id',r.FULFILLMENT_ID);o.put('shipment_id',r.EXPECTED_ST_ID);o.put('pallet_identifier',r.EXPECTED_PALLET_UID);
   o.put('source_warehouse_id',r.SOURCE_WARE_ID);o.put('rows_signature',r.ROWS_SIGNATURE);a.append(o);
  end loop;j.put('members',a);return j.to_clob;
 end;
 function admission(p_plan varchar2,p_snapshot clob)return clob is
  h RRL_HU_CONSOL_PLAN%rowtype;root_value json_object_t;nodes json_array_t:=json_array_t();node json_object_t;
  result_value json_object_t:=json_object_t();members json_array_t:=json_array_t();item json_object_t;
  type key_set is table of boolean index by varchar2(200);type ref_map is table of varchar2(400)index by varchar2(200);actual_st key_set;actual_ref ref_map;expected_st key_set;
  ff RRL_CUSTOMER_ORDER_FULFILLMENT%rowtype;current_uid varchar2(200);current_ware number;st number;case_id_value number;node_uid_value varchar2(200);k varchar2(200);state_value varchar2(60);
  missing number:=0;extra number:=0;unknown_leaves number:=0;changed number:=0;expected_count number:=0;ready boolean:=true;location_ready boolean:=false;
 begin
  select *into h from RRL_HU_CONSOL_PLAN where PLAN_ID=p_plan;
  if p_snapshot is not null then
   root_value:=json_object_t.parse(p_snapshot);nodes:=root_value.get_array('nodes');
   if nodes.get_size>200 then raise_application_error(-20881,'CONSOLIDATION_NODE_BOUND_200');end if;
   location_ready:=root_value.get_string('root')=h.ROOT_UID and root_value.get_number('warehouse')=h.TARGET_WARE_ID
    and root_value.get_string('cell')=h.TARGET_CELL and root_value.get_array('ancestors').get_size=0;
   for i in 0..nodes.get_size-1 loop
    node:=treat(nodes.get(i)as json_object_t);case_id_value:=node.get_number('case_task_id');node_uid_value:=node.get_string('uid');
    if node.get_string('kind')='CASE'then
     select LEGACY_SBORKA_PALLET_ID into st from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=case_id_value;
     if st is null then unknown_leaves:=unknown_leaves+1;else k:=RRL_STOCK_PLAN_HELPER.decimal_text(st);if actual_st.exists(k)then unknown_leaves:=unknown_leaves+1;end if;actual_st(k):=true;actual_ref(k):='CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(case_id_value);end if;
    elsif node.get_string('kind')='STOCK'and node.get_number('case_task_id')is null then
     st:=null;
     for bound in(select LEGACY_SBORKA_PALLET_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_PALLET_UID=node_uid_valueand PICKED_WAREHOUSE_TASK_ID is not null and STATUS='PICKED')loop
      if st is not null then raise_application_error(-20886,'CONSOLIDATION_AMBIGUOUS_STOCK_BINDING');end if;st:=bound.LEGACY_SBORKA_PALLET_ID;
     end loop;
     if st is null then unknown_leaves:=unknown_leaves+1;else k:=RRL_STOCK_PLAN_HELPER.decimal_text(st);if actual_st.exists(k)then unknown_leaves:=unknown_leaves+1;end if;actual_st(k):=true;actual_ref(k):='STOCK:'||node_uid_value;end if;
    end if;
   end loop;
  end if;
  for m in(select *from RRL_HU_CONSOL_MEMBER where PLAN_ID=p_plan order by FULFILLMENT_ID)loop
   expected_count:=expected_count+1;if expected_count>200 then raise_application_error(-20881,'CONSOLIDATION_MEMBER_BOUND_200');end if;
   expected_st(RRL_STOCK_PLAN_HELPER.decimal_text(m.EXPECTED_ST_ID)):=true;
   select *into ff from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=m.FULFILLMENT_ID;
   begin select PALLET_UID,WARE_ID into current_uid,current_ware from RRL_SBORKA_PALLETS where ID=ff.LEGACY_SBORKA_PALLET_ID;exception when no_data_found then current_uid:=null;current_ware:=null;end;
   state_value:='MISSING';
   if nvl(ff.LEGACY_SBORKA_PALLET_ID,-1)!=m.EXPECTED_ST_ID or nvl(ff.PALLET_UID,chr(1))!=m.EXPECTED_PALLET_UID or nvl(current_uid,chr(1))!=m.EXPECTED_PALLET_UID then state_value:='SHIPMENT_CHANGED';changed:=changed+1;
   elsif rows_signature(current_uid)!=m.ROWS_SIGNATURE then state_value:='REQUEST_CHANGED';changed:=changed+1;
   elsif ff.STATUS='PLANNED'then state_value:='NOT_PICKED';missing:=missing+1;
   elsif ff.STATUS!='PICKED'then state_value:='NOT_CURRENT_PICKED';missing:=missing+1;
   elsif actual_st.exists(RRL_STOCK_PLAN_HELPER.decimal_text(m.EXPECTED_ST_ID))then
    k:=RRL_STOCK_PLAN_HELPER.decimal_text(m.EXPECTED_ST_ID);
    if(ff.PICKED_CASE_TASK_ID is not null and actual_ref(k)='CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(ff.PICKED_CASE_TASK_ID))
     or(ff.PICKED_CASE_TASK_ID is null and ff.PICKED_WAREHOUSE_TASK_ID is not null and ff.PICKED_PALLET_UID is not null and actual_ref(k)='STOCK:'||ff.PICKED_PALLET_UID)then state_value:='IN_ROOT';
    else state_value:='BINDING_CHANGED';changed:=changed+1;end if;
   else missing:=missing+1;end if;
   item:=json_object_t();item.put('fulfillment_id',m.FULFILLMENT_ID);item.put('shipment_id',m.EXPECTED_ST_ID);item.put('pallet_identifier',m.EXPECTED_PALLET_UID);item.put('state',state_value);members.append(item);
  end loop;
  k:=actual_st.first;while k is not null loop if not expected_st.exists(k)then extra:=extra+1;end if;k:=actual_st.next(k);end loop;
  ready:=h.STATUS='ACTIVE'and location_ready and expected_count>0 and missing=0 and extra=0 and changed=0 and unknown_leaves=0;
  result_value.put('domain','CONSOLIDATION_READINESS');result_value.put('version',1);result_value.put('plan_id',h.PLAN_ID);result_value.put('plan_version',h.PLAN_VERSION);
  result_value.put('ready',ready);result_value.put('location_ready',location_ready);result_value.put('expected_count',expected_count);result_value.put('missing_count',missing);
  result_value.put('extra_count',extra);result_value.put('changed_count',changed);result_value.put('unknown_leaf_count',unknown_leaves);result_value.put('members',members);
  result_value.put('expectation_signature',digest(frozen_plan(p_plan)));result_value.put('quality_release_approved',false);result_value.put('stock_changed',false);return result_value.to_clob;
 end;
 function plan_json(p_plan varchar2,p_actor nvarchar2)return clob is h RRL_HU_CONSOL_PLAN%rowtype;wire clob;j json_object_t;n number;begin
  assert_plan_scope(p_plan,p_actor,'warehouse_task_view');select *into h from RRL_HU_CONSOL_PLAN where PLAN_ID=p_plan;
  select count(*)into n from RRL_PALLETS where UID_PALLET=h.ROOT_UID and HU_KIND='CONTAINER'and HU_CURRENT_CELL is not null;
  if n=1 then wire:=RRL_STOCK_HU_READ.snapshot_json(h.ROOT_UID);end if;
  j:=json_object_t.parse(frozen_plan(p_plan));j.put('readiness',json_object_t.parse(admission(p_plan,wire)));return j.to_clob;
 end;
 function shipping_admission(p_root varchar2,p_snapshot clob)return clob is plan_id_value varchar2(100);j json_object_t;token json_object_t:=json_object_t();begin
  begin select PLAN_ID into plan_id_value from RRL_HU_CONSOL_PLAN where ROOT_UID=p_root and STATUS='ACTIVE';exception when no_data_found then return null;end;
  j:=json_object_t.parse(admission(plan_id_value,p_snapshot));
  if not j.get_boolean('ready')then raise_application_error(-20886,'CONSOLIDATION_EXPECTED_COMPOSITION_NOT_READY');end if;
  token.put('domain','CONSOLIDATION_EXPECTATIONS');token.put('version',1);token.put('plan_id',plan_id_value);token.put('plan_version',j.get_number('plan_version'));token.put('signature',j.get_string('expectation_signature'));return token.to_clob;
 end;
 procedure assert_shipping_current(p_expected clob,p_root varchar2,p_snapshot clob)is actual_value clob:=shipping_admission(p_root,p_snapshot);begin
  if p_expected is null and actual_value is null then return;end if;
  if p_expected is null or actual_value is null or dbms_lob.compare(p_expected,actual_value)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: consolidation expectations');end if;
 end;
end;
/
