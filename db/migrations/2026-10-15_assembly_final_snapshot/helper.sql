create or replace package RRL_ASM_FINAL_SNAPSHOT authid definer accessible by(
 package RRL_ASSEMBLY_SCALE_API,package RRL_WH_SCALE_API,package RRL_WH_WEIGH_REQUEST_API) as
 function status_json(p_session varchar2)return clob;
 function capture_json(p_task number,p_device varchar2,p_sender varchar2)return clob;
end;
/
create or replace package body RRL_ASM_FINAL_SNAPSHOT as
 function status_json(p_session varchar2)return clob is
  s RRL_ASSEMBLY_SESSION%rowtype;t RRL_CASE_PICK_TASK%rowtype;d RRL_WH_SCALE_DEVICE%rowtype;station RRL_ASSEMBLY_STATION%rowtype;typ RRL_PALLET_TYPE%rowtype;
  f RRL_CUSTOMER_ORDER_FULFILLMENT%rowtype;st RRL_SBORKA_PALLETS%rowtype;
  j json_object_t:=json_object_t();o json_object_t;v json_object_t;arr json_array_t;
  tree json_object_t:=json_object_t();rows_json json_array_t:=json_array_t();lines_json json_array_t:=json_array_t();
  st_json json_array_t:=json_array_t();reservations json_array_t;quantity number;held number;total number:=0;n number;row_count number:=0;group_count number:=0;line_total number:=0;all_hard number;unit_count number;only_unit varchar2(20);normalized_qty number;article_value varchar2(100);uom_value varchar2(20);seen_keys json_array_t:=json_array_t();key_value varchar2(512);
 begin
  select *into s from RRL_ASSEMBLY_SESSION where SESSION_ID=p_session;
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID;
  if s.STATE is null or s.STATE!='OPEN'or s.EXPIRES_AT is null or s.EXPIRES_AT<systimestamp or s.LAST_SEQUENCE is null or s.LAST_SEQUENCE<1
   or t.STATUS is null or t.STATUS not in('WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP')
   or t.ASSIGNED_TO is null or t.ASSIGNED_TO!=s.OPERATOR_ID or t.CONTENT_VERSION is null or s.LAST_CONTENT_VERSION is null or t.CONTENT_VERSION!=s.LAST_CONTENT_VERSION
   or s.OPERATOR_ID is null or s.CARRIER_IDENTIFIER is null or t.SSCC is null or t.SSCC!=s.CARRIER_IDENTIFIER or t.WARE_ID is null or s.WARE_ID is null or t.WARE_ID!=s.WARE_ID or t.LEGACY_SBORKA_PALLET_ID is null then
   raise_application_error(-20886,'ASM_FINAL_CURRENT_CLOSED_BOUND_SESSION_REQUIRED');end if;
  RRL_CASE_TASK_ACCESS.assert_scope(t.CASE_PICK_TASK_ID,s.OPERATOR_ID,'case_pick_execute');
  select count(*)into n from RUSERS where ID=s.OPERATOR_ID and nvl(DELETED,0)=0;if n!=1 then raise_application_error(-20882,'ASM_FINAL_CURRENT_OPERATOR_REQUIRED');end if;
  select *into d from RRL_WH_SCALE_DEVICE where DEVICE_ID=s.DEVICE_ID;
  select *into station from RRL_ASSEMBLY_STATION where DEVICE_ID=s.DEVICE_ID;
  if station.ACTIVE_FLAG is null or station.ACTIVE_FLAG!=1 or station.VERSION_NO is null or s.STATION_POLICY_VERSION is null or station.VERSION_NO!=s.STATION_POLICY_VERSION
   or station.CONFIRMATION_MODE is null or s.CONFIRMATION_MODE is null or station.CONFIRMATION_MODE!=s.CONFIRMATION_MODE then raise_application_error(-20886,'ASM_FINAL_STATION_POLICY_CHANGED');end if;
  if d.ACTIVE_FLAG is null or d.ACTIVE_FLAG!=1 or d.POLICY_VERSION is null or s.DEVICE_POLICY_VERSION is null or d.POLICY_VERSION!=s.DEVICE_POLICY_VERSION or d.WARE_ID is null or d.WARE_ID!=s.WARE_ID or d.POST_CELL is null or s.POST_CELL is null or d.POST_CELL!=s.POST_CELL
   or d.SENDER_ID is null or d.SENDER_ID!=s.SENDER_ID or d.CALIBRATION_REF is null or s.CALIBRATION_REF is null or d.CALIBRATION_REF!=s.CALIBRATION_REF or d.DEVICE_MODE is null or s.DEVICE_MODE is null or d.DEVICE_MODE!=s.DEVICE_MODE
   or d.MEASUREMENT_BASIS is null or d.MEASUREMENT_BASIS!='GROSS'or d.CALIBRATED_UNTIL is null or d.CALIBRATED_UNTIL<systimestamp then raise_application_error(-20886,'ASM_FINAL_CURRENT_DEVICE_REQUIRED');end if;
  select count(*)into n from RUSERS where ID=s.SENDER_ID and nvl(DELETED,0)=0 and WARE_ID=s.WARE_ID
   and upper(trim(USER_GROUP))!='GLOBAL_ADMIN'and RRL_HAS_WRIGHT(ID,'warehouse_scale_ingest')=1;
  if n!=1 then raise_application_error(-20882,'ASM_FINAL_CURRENT_SENDER_REQUIRED');end if;
  select count(*)into n from RRL_ASSEMBLY_STEP where SESSION_ID=p_session and STATE not in('APPLIED','CANCELLED');
  if n!=0 then raise_application_error(-20886,'ASM_FINAL_UNRESOLVED_STEPS');end if;
  select *into typ from RRL_PALLET_TYPE where PALLET_TYPE_ID=t.PALLET_TYPE_ID;
  if typ.ACTIVE is null or typ.ACTIVE!=1 or typ.FINAL_WEIGHT_REQUIRED is null or typ.FINAL_WEIGHT_REQUIRED!=1 or typ.LOAD_UNIT_CLASS is null or upper(typ.LOAD_UNIT_CLASS)!='CONTAINER'or typ.TYPE_VERSION is null then raise_application_error(-20886,'ASM_FINAL_CURRENT_CONTAINER_TYPE_REQUIRED');end if;
  select *into st from RRL_SBORKA_PALLETS where ID=t.LEGACY_SBORKA_PALLET_ID;
  if st.WARE_ID is null or st.WARE_ID!=t.WARE_ID or st.RETURN_SUPPLIER_ID is not null or nvl(st.CONDITION,0)>=2 or st.PALLET_UID is null then raise_application_error(-20886,'ASM_FINAL_BOUND_ST_CHANGED');end if;
  select *into f from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=st.ID and PALLET_UID=st.PALLET_UID
   and CUSTOMER_ORDER_ID=t.CUSTOMER_ORDER_ID and STATUS='PICKED'and PICKED_CASE_TASK_ID=t.CASE_PICK_TASK_ID and PICKED_CONTENT_VERSION=t.CONTENT_VERSION;
  tree.put('domain','ASM_FINAL');tree.put('version',3);tree.put('station_version',station.VERSION_NO);tree.put('confirmation_mode',station.CONFIRMATION_MODE);tree.put('session_id',p_session);tree.put('case_task_id',t.CASE_PICK_TASK_ID);
  tree.put('content_version',t.CONTENT_VERSION);tree.put('assignment_version',t.ASSIGNMENT_VERSION);tree.put('carrier',t.SSCC);tree.put('warehouse',t.WARE_ID);tree.put('pallet_type',t.PALLET_TYPE_ID);tree.put('pallet_type_version',typ.TYPE_VERSION);
  tree.put('bound_st_id',st.ID);tree.put('bound_st_uid',st.PALLET_UID);tree.put('order_id',t.CUSTOMER_ORDER_ID);
  tree.put('fulfillment_id',f.FULFILLMENT_ID);tree.put('fulfillment_version',f.PICKED_CONTENT_VERSION);
  select count(*)into n from RRL_CASE_PICK_SHORT where CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID and STATUS in('CREATED','PENDING_APPROVAL');
  if n!=0 then raise_application_error(-20886,'ASM_FINAL_PENDING_SHORT');end if;
  for ln in(select *from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID order by CASE_PICK_LINE_ID)loop
   if lines_json.get_size>=200 then raise_application_error(-20886,'ASM_FINAL_LINE_BOUND200');end if;
   if ln.STATUS is null or ln.STATUS not in('PICKED','SHORT_PICKED','CANCELLED')or ln.PICKED_QTY is null or ln.PICKED_QTY<0 or ln.PLANNED_QTY is null or ln.PICKED_QTY>ln.PLANNED_QTY or(ln.STATUS='PICKED'and ln.PICKED_QTY!=ln.PLANNED_QTY)then raise_application_error(-20886,'ASM_FINAL_OPEN_LINES');end if;
   select nvl(sum(r.REMAIN),0)into quantity from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID and h.CASE_PICK_LINE_ID=ln.CASE_PICK_LINE_ID;
   if quantity!=ln.PICKED_QTY then raise_application_error(-20886,'ASM_FINAL_LINE_PHYSICAL_MISMATCH');end if;
   line_total:=line_total+ln.PICKED_QTY;
   o:=json_object_t();o.put('source_cell',ln.CELL_CODE);o.put('line_id',ln.CASE_PICK_LINE_ID);o.put('pick_task',ln.PICK_TASK_ID);o.put('article',ln.ARTICUL);
   o.put('picked',RRL_STOCK_PLAN_HELPER.decimal_text(ln.PICKED_QTY));o.put('planned',RRL_STOCK_PLAN_HELPER.decimal_text(ln.PLANNED_QTY));o.put('state',ln.STATUS);lines_json.append(o);
  end loop;
  for r in(select h.LOT_UID,h.CASE_PICK_LINE_ID,p.ARTICUL,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.BASE_UOM,r.STOCK_VERSION
   from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID
   where h.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID and r.REMAIN>0 order by h.LOT_UID,r.CELL)loop
   row_count:=row_count+1;if row_count>200 then raise_application_error(-20886,'ASM_FINAL_LOT_BOUND200');end if;
   if r.BASE_UOM is null or r.ARTICUL is null or r.HARD_RESERVED_BASE!=r.REMAIN then raise_application_error(-20886,'ASM_FINAL_OWN_HARD_REQUIRED');end if;
   reservations:=json_array_t();held:=0;
   for rr in(select q.*from RRL_STOCK_RESERVATION q join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=r.CASE_PICK_LINE_ID
    where l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID and q.UID_PALLET=r.LOT_UID and q.CELL=r.CELL and q.WARE_ID=t.WARE_ID
     and q.ARTICUL=r.ARTICUL and q.BASE_UOM=r.BASE_UOM and q.STATUS='ACTIVE'and q.RESERVATION_KIND='HARD'and q.RESERVATION_DOMAIN='PICKING'
     and q.CUSTOMER_ORDER_ID=t.CUSTOMER_ORDER_ID and q.PICK_WAVE_ID=t.PICK_WAVE_ID and q.PICK_PLAN_LINE_ID=l.PICK_PLAN_LINE_ID
     and q.SOURCE_DOC_TYPE='PICK_WAVE'and q.SOURCE_DOC_ID=t.PICK_WAVE_ID and q.SOURCE_LINE_ID=l.PICK_TASK_ID order by q.RESERVATION_ID)loop
    if rr.RESERVATION_VERSION is null or rr.RESERVATION_VERSION<1 or rr.BASE_QTY is null or rr.BASE_QTY<=0 or reservations.get_size>=200 then raise_application_error(-20886,'ASM_FINAL_RESERVATION_INVALID');end if;
    held:=held+rr.BASE_QTY;v:=json_object_t();v.put('id',rr.RESERVATION_ID);v.put('version',rr.RESERVATION_VERSION);v.put('qty',RRL_STOCK_PLAN_HELPER.decimal_text(rr.BASE_QTY));reservations.append(v);
   end loop;
   select nvl(sum(BASE_QTY),0)into all_hard from RRL_STOCK_RESERVATION where UID_PALLET=r.LOT_UID and CELL=r.CELL and STATUS='ACTIVE'and RESERVATION_KIND='HARD';
   if all_hard!=held or held!=r.REMAIN then raise_application_error(-20886,'ASM_FINAL_OWN_PICKED_RESERVATION_INSUFFICIENT');end if;
   o:=json_object_t();o.put('uid',r.LOT_UID);o.put('line_id',r.CASE_PICK_LINE_ID);o.put('article',r.ARTICUL);o.put('cell',r.CELL);
   o.put('qty',RRL_STOCK_PLAN_HELPER.decimal_text(r.REMAIN));o.put('base_uom',r.BASE_UOM);o.put('stock_version',r.STOCK_VERSION);o.put('reservations',reservations);rows_json.append(o);total:=total+r.REMAIN;
  end loop;
  if t.PICKED_QTY is null or t.PICKED_QTY!=line_total or total!=line_total then raise_application_error(-20886,'ASM_FINAL_TASK_QUANTITY_CHANGED');end if;
  if row_count=0 then raise_application_error(-20886,'ASM_FINAL_PHYSICAL_CONTENT_REQUIRED');end if;
  for a in(select p.ARTICUL,r.BASE_UOM,sum(r.REMAIN)QTY from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID
   join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID where h.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID and r.REMAIN>0 group by p.ARTICUL,r.BASE_UOM)loop
   group_count:=group_count+1;
   quantity:=0;
   for z in(select z.QUANTITY,u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE from RRL_SBORKA_PALLET_ROWS z join RRL_STOCK_UOM_CONVERSION u
    on u.ARTICUL=z.ARTICUL and u.INPUT_UOM=z.EI and u.POLICY_VERSION=(select max(v.POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION v where v.ARTICUL=z.ARTICUL and v.INPUT_UOM=z.EI)
    where z.PALLET_UID=st.PALLET_UID and z.ARTICUL=a.ARTICUL and u.BASE_UOM=a.BASE_UOM order by z.ID)loop
    quantity:=quantity+RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(z.QUANTITY),z.NUMERATOR,z.DENOMINATOR,z.BASE_SCALE);
   end loop;
   if quantity is null or quantity!=a.QTY then raise_application_error(-20886,'ASM_FINAL_ST_COMPOSITION_CHANGED');end if;
  end loop;
  for sr in(select z.ID,z.ARTICUL,z.QUANTITY,z.EI,u.BASE_UOM,u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE,u.POLICY_VERSION from RRL_SBORKA_PALLET_ROWS z
   left join RRL_STOCK_UOM_CONVERSION u on u.ARTICUL=z.ARTICUL and u.INPUT_UOM=z.EI and u.POLICY_VERSION=(select max(v.POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION v where v.ARTICUL=z.ARTICUL and v.INPUT_UOM=z.EI)
   where z.PALLET_UID=st.PALLET_UID order by z.ID)loop
   if st_json.get_size>=200 or sr.BASE_UOM is null or sr.QUANTITY is null or sr.QUANTITY<=0 or sr.NUMERATOR is null or sr.DENOMINATOR is null or sr.NUMERATOR<=0 or sr.DENOMINATOR<=0 then raise_application_error(-20886,'ASM_FINAL_ST_ROW_INVALID');end if;
   select count(*)into n from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID where h.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID and r.REMAIN>0 and p.ARTICUL=sr.ARTICUL and r.BASE_UOM=sr.BASE_UOM;
   if n=0 then raise_application_error(-20886,'ASM_FINAL_ST_EXTRA_CONTENT');end if;
   normalized_qty:=RRL_STOCK_MATH.convert_exact(RRL_STOCK_PLAN_HELPER.decimal_text(sr.QUANTITY),sr.NUMERATOR,sr.DENOMINATOR,sr.BASE_SCALE);
   o:=json_object_t();o.put('normalized_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(normalized_qty));o.put('base_scale',sr.BASE_SCALE);o.put('id',sr.ID);o.put('article',sr.ARTICUL);o.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(sr.QUANTITY));o.put('unit',sr.EI);o.put('base_uom',sr.BASE_UOM);o.put('numerator',sr.NUMERATOR);o.put('denominator',sr.DENOMINATOR);o.put('policy',sr.POLICY_VERSION);st_json.append(o);
  end loop;
  if f.FACT_COMPOSITION_JSON is null then raise_application_error(-20886,'ASM_FINAL_FULFILLMENT_COMPOSITION_REQUIRED');end if;
  arr:=json_array_t.parse(f.FACT_COMPOSITION_JSON);if arr.get_size!=group_count then raise_application_error(-20886,'ASM_FINAL_FULFILLMENT_COMPOSITION_CHANGED');end if;
  for k in 0..arr.get_size-1 loop
   o:=treat(arr.get(k)as json_object_t);article_value:=o.get_string('article');uom_value:=o.get_string('base_uom');
   if article_value is null or uom_value is null or o.get_string('quantity')is null then raise_application_error(-20886,'ASM_FINAL_FULFILLMENT_GROUP_REQUIRED');end if;
   quantity:=RRL_STOCK_MATH.quantity(o.get_string('quantity'));if quantity is null or quantity<=0 then raise_application_error(-20886,'ASM_FINAL_FULFILLMENT_QUANTITY_POSITIVE');end if;
   v:=json_object_t();v.put('article',article_value);v.put('unit',uom_value);key_value:=v.to_string;
   if seen_keys.get_size>0 then for z in 0..seen_keys.get_size-1 loop if seen_keys.get_string(z)=key_value then raise_application_error(-20886,'ASM_FINAL_DUPLICATE_FULFILLMENT_GROUP');end if;end loop;end if;seen_keys.append(key_value);
   select sum(r.REMAIN)into held from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID where h.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID and r.REMAIN>0 and p.ARTICUL=article_value and r.BASE_UOM=uom_value;
   if held is null or held!=quantity then raise_application_error(-20886,'ASM_FINAL_FULFILLMENT_COMPOSITION_CHANGED');end if;
  end loop;
  select count(distinct r.BASE_UOM),min(r.BASE_UOM)into unit_count,only_unit from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID and r.REMAIN>0;
  if(unit_count=1 and(f.FACT_QTY is null or f.FACT_QTY!=total or f.FACT_UOM is null or f.FACT_UOM!=only_unit))
   or(unit_count>1 and(f.FACT_QTY is not null or f.FACT_UOM is not null))then raise_application_error(-20886,'ASM_FINAL_FULFILLMENT_QUANTITY_CHANGED');end if;
  tree.put('fulfillment_composition',arr);tree.put('fulfillment_quantity',f.FACT_QTY);tree.put('fulfillment_unit',f.FACT_UOM);
  tree.put('lines',lines_json);tree.put('lots',rows_json);tree.put('st_rows',st_json);
  j.put('composition_signature',rawtohex(sys.dbms_crypto.hash(tree.to_clob,sys.dbms_crypto.hash_sh256)));j.put('composition_signature_version',3);j.put('signature_domain','ASM_FINAL');j.put('session_id',p_session);j.put('snapshot',tree);return j.to_clob;
 exception when no_data_found or too_many_rows then raise_application_error(-20886,'ASM_FINAL_CURRENT_SOURCE_NOT_UNIQUE');
 end;
 function capture_json(p_task number,p_device varchar2,p_sender varchar2)return clob is sid varchar2(100);n number;
 begin
  select count(*),min(SESSION_ID)into n,sid from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=p_task and DEVICE_ID=p_device and STATE in('OPEN','BLOCKED');
  if n=0 then return null;end if;
  if n!=1 then raise_application_error(-20886,'ASM_FINAL_AMBIGUOUS_SESSION');end if;
  select count(*)into n from RRL_ASSEMBLY_SESSION where SESSION_ID=sid and SENDER_ID=p_sender;
  if n!=1 then raise_application_error(-20882,'ASM_FINAL_ORIGINAL_SENDER_REQUIRED');end if;
  return status_json(sid);
 end;
end;
/
