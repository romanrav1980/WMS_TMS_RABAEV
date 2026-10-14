create or replace package body RRL_STOCK_HU_SHIP_CMD as  
 function digest(s clob) return varchar2 is begin return rawtohex(sys.dbms_crypto.hash(s,sys.dbms_crypto.hash_sh256));end;  
 procedure append_all(a in out nocopy json_array_t,b json_array_t) is begin for i in 0..b.get_size-1 loop a.append(b.get(i));end loop;end;  
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is  
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v json_object_t:=json_object_t();snap json_object_t;  
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;plans json_array_t:=json_array_t();x json_object_t;sub json_object_t;src json_object_t;subdomain json_object_t;  
  v_uid varchar2(200):=d.get_object('source').get_string('uid');s clob;nodes clob;p clob;q clob;dom clob;st number;ident varchar2(200);total number:=0;leaf_qty number;leg_uid varchar2(200);leg_cell varchar2(60);leg_qty number;leg_count number;all_legs json_array_t:=json_array_t();type quantity_map is table of number index by varchar2(200);expected_qty quantity_map;consumed_qty quantity_map;loading_domain json_object_t;v_profiles clob;v_first_profiles clob;v_profile_count number;v_warehouse number;v_source_cell varchar2(60);  
 begin  
  s:=RRL_STOCK_HU_READ.snapshot_json(v_uid);snap:=json_object_t.parse(s);v_warehouse:=snap.get_number('warehouse');v_source_cell:=snap.get_string('cell');a:=snap.get_array('nodes');nodes:=a.to_clob;  
  if snap.get_array('ancestors').get_size>0 or a.get_size<2 or treat(a.get(0) as json_object_t).get_string('kind')!='CONTAINER' then raise_application_error(-20886,'HU_SHIP_TOP_CONTAINER_REQUIRED');end if;  
  if m.get_number('expected_version') is null or m.get_number('expected_version')!=treat(a.get(0) as json_object_t).get_number('version') then raise_application_error(-20890,'CLOSURE_CHANGED: HU shipment version');end if;  
  for i in 0..a.get_size-1 loop  
   x:=treat(a.get(i) as json_object_t);  
   if x.get_number('open_task_count')>0 then raise_application_error(-20886,'HU_SHIP_PHYSICAL_TASK_OPEN');end if;  
   if x.get_string('kind')='STOCK' then  
    expected_qty(x.get_string('uid')):=RRL_STOCK_MATH.quantity(x.get_string('quantity'));  
   end if;  
   RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',x.get_string('uid'));  
   if x.get_string('kind')='CASE' then  
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('case_task_id')));  
   else RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',x.get_string('uid'));end if;  
  end loop;  
  for ct in(select LEGACY_SBORKA_PALLET_ID from(  
   select LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(  
    select CASE_ID from json_table(nodes,'$[*]' columns(CASE_ID number path '$.case_task_id')))  
   union  
   select LEGACY_SBORKA_PALLET_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where STATUS='PICKED' and PICKED_WAREHOUSE_TASK_ID is not null  
    and PICKED_PALLET_UID in(select U from json_table(nodes,'$[*]' columns(U varchar2(200) path '$.uid',K varchar2(20) path '$.kind',CASE_ID number path '$.case_task_id')) where K='STOCK' and CASE_ID is null))  
   union 
   select b.ST_ID from RRL_INTERWARE_ONWARD_BIND b where b.WARE_ID=v_warehouse and b.SOURCE_CELL=v_source_cell and not exists(select 1 from RRL_INTERWARE_ONWARD_DISPATCH dispatched where dispatched.BIND_OPERATION_ID=b.OPERATION_ID)and b.ROOT_UID in( 
    select U from json_table(nodes,'$[*]'columns(U varchar2(200)path '$.uid',K varchar2(20)path '$.kind'))where K='STOCK') 
   union 
   select b.ST_ID from RRL_IW_RECOVERY_ST_BIND b where b.WARE_ID=v_warehouse and b.SOURCE_CELL=v_source_cell and not exists(select 1 from RRL_IW_RECOVERY_DISPATCH dispatched where dispatched.BIND_OPERATION_ID=b.OPERATION_ID)and b.ROOT_UID in( 
    select U from json_table(nodes,'$[*]'columns(U varchar2(200)path '$.uid',K varchar2(20)path '$.kind'))where K='STOCK') 
   order by 1) loop  
   st:=ct.LEGACY_SBORKA_PALLET_ID;if st is null then raise_application_error(-20886,'HU_SHIP_CASE_BINDING_REQUIRED');end if;  
   select PALLET_UID into ident from RRL_SBORKA_PALLETS where ID=st;  
   sub:=json_object_t();src:=json_object_t();src.put('pallet_identifier',ident);  
   sub.put('command_type','SHIP_PALLET');sub.put('operation_id',p_operation);sub.put('source',src);sub.put('metadata',json_object_t());  
   RRL_STOCK_SHIPPING_CORE.compile_shipment(sub.to_clob,p_operation,p,q,dom,true);  
   subdomain:=json_object_t.parse(dom);RRL_STOCK_QC_GATE.assert_approved(dom);  
   total:=total+subdomain.get_array('legs').get_size;if total>200 then raise_application_error(-20881,'HU_SHIP_ALLOCATION_BOUND_200');end if;  
   declare sublegs json_array_t:=subdomain.get_array('legs');leg json_object_t;begin  
    for z in 0..sublegs.get_size-1 loop  
     leg:=treat(sublegs.get(z) as json_object_t);leg_uid:=leg.get_string('uid');leg_cell:=leg.get_string('cell');leg_qty:=RRL_STOCK_MATH.quantity(leg.get_string('quantity'));  
     if not expected_qty.exists(leg_uid) or leg_cell!=snap.get_string('cell') then raise_application_error(-20886,'HU_SHIP_ALLOCATION_OUTSIDE_PHYSICAL_TREE');end if;  
     if not consumed_qty.exists(leg_uid) then consumed_qty(leg_uid):=0;end if;  
     consumed_qty(leg_uid):=consumed_qty(leg_uid)+leg_qty;  
    end loop;  
   end;  
   x:=json_object_t();x.put('request',sub);x.put('domain',subdomain);plans.append(x);  
   append_all(f,json_array_t.parse(p));append_all(r,json_array_t.parse(q));  
  end loop;  
  if plans.get_size=0 then raise_application_error(-20886,'HU_SHIP_BOUND_SHIPMENT_REQUIRED');end if;  
  leg_uid:=expected_qty.first;  
  while leg_uid is not null loop  
   if not consumed_qty.exists(leg_uid) or consumed_qty(leg_uid)!=expected_qty(leg_uid) then raise_application_error(-20886,'HU_SHIP_WHOLE_PHYSICAL_LEAF_BINDING_REQUIRED');end if;  
   leg_uid:=expected_qty.next(leg_uid);  
  end loop;  
  for i in 0..plans.get_size-1 loop 
   x:=treat(plans.get(i)as json_object_t);subdomain:=x.get_object('domain'); 
   if subdomain.has('interwarehouse_onward_source')and(plans.get_size!=1 or expected_qty.count!=1)then
    if subdomain.get_object('interwarehouse_onward_source').has('recovery_operation_id')then raise_application_error(-20886,'INTERWARE_MULTI_RECOVERY_EXPLICIT_LINEAGE_REQUIRED');end if;
    for t in(select UID_VALUE,ARTICLE_VALUE,KIND_VALUE from json_table(nodes,'$[*]'columns(UID_VALUE varchar2(200)path '$.uid',ARTICLE_VALUE varchar2(160)path '$.article',KIND_VALUE varchar2(20)path '$.kind')))loop
     if t.KIND_VALUE not in('CONTAINER','STOCK')then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_STOCK_ONLY_REQUIRED');end if;
     if t.KIND_VALUE='STOCK'then
      select count(*),json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)into v_profile_count,v_profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=t.ARTICLE_VALUE;
      select count(*)into leg_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=t.UID_VALUE;
      if leg_count>0 and v_profile_count=0 then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_SERIALIZED_PROFILE_REQUIRED');end if;
      if v_profile_count>0 then
       select count(*)into leg_count from RRL_SKU_RECEIPT_PROFILE where ARTICUL=t.ARTICLE_VALUE and SCAN_MODE not in('UNIT','UNIT_OR_AGGREGATION');
       if leg_count>0 then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_UNIT_SCAN_MODE_REQUIRED');end if;
      else v_profiles:=json_array_t().to_clob;end if;

     end if;
    end loop;
   end if;
  end loop; 
  a:=snap.get_array('links');  
  for i in 0..a.get_size-1 loop x:=treat(a.get(i) as json_object_t);  
   if x.get_number('id') is not null then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));end if;  
  end loop;  
  for c in(select TASK_ID,CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=v_uid and STATUS='OCCUPIED') loop  
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RECEIPT_SLOT_CLAIM',RRL_STOCK_PLAN_HELPER.decimal_text(c.TASK_ID));  
   RRL_STOCK_PLAN_HELPER.anchor(r,40,'SLOT',RRL_STOCK_PLAN_HELPER.decimal_text(c.CELL_SLOT_ID));  
  end loop;  
  RRL_STOCK_HU_LOAD_CORE.compile_load(p_request,snap.to_clob,plans.to_clob,f,r,loading_domain);  
  v.put('loading',loading_domain);  
  v.put('uid',v_uid);v.put('snapshot',snap);v.put('signature',digest(s));v.put('shipments',plans);v.put('allocation_count',total);  
  p_domain:=v.to_clob;p_resources:=r.to_clob;p_policies:=f.to_clob;  
 end;  
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is  
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');op varchar2(100):=d.get_string('operation_id');plan clob;  
  v json_object_t;snap json_object_t;a json_array_t;entry json_object_t;subdomain json_object_t;req json_object_t;j json_object_t:=json_object_t();results json_array_t:=json_array_t();  
  v_uid varchar2(200);alias varchar2(32);nodes clob;shipments clob;offset_no number:=0;n number;result clob;dom clob;ident varchar2(200);  
 begin  
  if RRL_HAS_WRIGHT(p_actor,'CLOSE_OTHOD_NAKLAD')!=1 and RRL_HAS_WRIGHT(p_actor,'stock_posting_shipping')!=1 then raise_application_error(-20882,'SHIPPING_FORBIDDEN');end if;  
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');  
  v_uid:=v.get_string('uid');snap:=v.get_object('snapshot');nodes:=snap.get_array('nodes').to_clob;shipments:=v.get_array('shipments').to_clob;  
  select SSCC into alias from RRL_PALLETS where UID_PALLET=v_uid;  
  if m.get_string('scan_container') is null or(m.get_string('scan_container')!=v_uid and(alias is null or m.get_string('scan_container')!=alias))  
   or m.get_string('scan_cell') is null or m.get_string('scan_cell')!=snap.get_string('cell') then raise_application_error(-20886,'HU_SHIP_CONTAINER_CELL_SCAN_REQUIRED');end if;  
  if v.has('loading') and not v.get('loading').is_null then  
   if RRL_HAS_WRIGHT(p_actor,'stock_posting_shipping')!=1 then raise_application_error(-20882,'PHYSICAL_LOAD_FORBIDDEN');end if;  
   RRL_STOCK_HU_LOAD_CORE.begin_load(v.get_object('loading').to_clob);  
  end if;  
  -- All real ST rows precede all CASE rows; logical closure was acquired globally by root.  
  for z in(select ID from RRL_SBORKA_PALLETS where ID in(select ID from json_table(shipments,'$[*]' columns(ID number path '$.domain.document_id'))) order by ID) loop select ID into n from RRL_SBORKA_PALLETS where ID=z.ID for update;end loop;  
  for z in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(select ID from json_table(nodes,'$[*]' columns(ID number path '$.case_task_id'))) order by CASE_PICK_TASK_ID) loop select CASE_PICK_TASK_ID into n from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=z.CASE_PICK_TASK_ID for update;end loop;  
  if digest(RRL_STOCK_HU_READ.snapshot_json(v_uid))!=v.get_string('signature') then raise_application_error(-20890,'CLOSURE_CHANGED: HU shipment tree');end if;  
  a:=v.get_array('shipments');  
  -- Recheck all approvals before any leg; later execution also rechecks its own frozen plan.  
  for i in 0..a.get_size-1 loop entry:=treat(a.get(i) as json_object_t);dom:=entry.get_object('domain').to_clob;RRL_STOCK_QC_GATE.assert_approved(dom);end loop;  
  for i in 0..a.get_size-1 loop  
   entry:=treat(a.get(i) as json_object_t);req:=entry.get_object('request');subdomain:=entry.get_object('domain');  
   RRL_STOCK_SHIPPING_CORE.execute_resolved(req.to_clob,subdomain.to_clob,offset_no,p_actor,result);  
   results.append(json_object_t.parse(result));offset_no:=offset_no+subdomain.get_array('legs').get_size;  
  end loop;  
  a:=snap.get_array('links');  
  for i in 0..a.get_size-1 loop entry:=treat(a.get(i) as json_object_t);n:=entry.get_number('id');  
   if n is not null then update RRL_WMS_HU_LINK set ACTIVE_FLAG=0,LINK_VERSION=LINK_VERSION+1,UNLINKED_OPERATION_ID=op,UNLINKED_AT=systimestamp,UNLINKED_BY=p_actor where HU_LINK_ID=n and ACTIVE_FLAG=1;  
    if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: HU departure link');end if;end if;  
  end loop;  
  a:=snap.get_array('nodes');  
  for i in 0..a.get_size-1 loop entry:=treat(a.get(i) as json_object_t);ident:=entry.get_string('uid');  
   if entry.get_string('kind')='CONTAINER' then  
    update RRL_PALLETS set HU_CURRENT_CELL=null,HU_SHIPPED_OPERATION=op,HU_CONTENT_VERSION=HU_CONTENT_VERSION+1 where UID_PALLET=ident and HU_SHIPPED_OPERATION is null;  
    if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: HU departure');end if;  
    delete from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=ident and STATUS='OCCUPIED';  
   end if;  
  end loop;  
  if v.has('loading') and not v.get('loading').is_null then  
   RRL_STOCK_HU_LOAD_CORE.finish_load(v.get_object('loading').to_clob,snap.to_clob,op,p_actor);j.put('physical_load',v.get_object('loading'));  
  end if;  
  j.put('operation_id',op);j.put('status','SHIPPED');j.put('uid',v_uid);j.put('shipments',results);j.put('composition_at_departure',snap);j.put('top_place_count',1);  
  p_result:=j.to_clob;  
 end;  
end;
/
