create or replace package body RRL_STOCK_QC_POLICY as
 procedure settings(p_warehouse number,p_mode out varchar2,p_independent out number) is
 begin
  select nvl(s.OUTGOING_QC_MODE,case when nvl(w.BLOCK_IF_NO_PROOVE,0)=1 then 'ANY' else 'NONE' end),
   nvl(s.OUTGOING_QC_INDEPENDENT,0) into p_mode,p_independent from RRL_WARES w
   left join RRL_RECEIPT_WARE_SETTINGS s on s.WARE_ID=w.ID where w.ID=p_warehouse;
 end;
 procedure settings_for_plan(p_domain clob,p_mode out varchar2,p_independent out number)is
  d json_object_t:=json_object_t.parse(p_domain);case_id number:=d.get_number('case_task');required number;policy json_object_t;
 begin
  policy:=json_object_t.parse(RRL_QC_SCOPE_READ.policy_json(p_domain));p_mode:=policy.get_string('mode');p_independent:=policy.get_number('independent');
  if case_id is not null then
   select t.FINAL_WEIGHT_REQUIRED into required from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=c.PALLET_TYPE_ID
    where c.CASE_PICK_TASK_ID=case_id;
   if required=1 then
    if p_mode in('NONE','ANY')then p_mode:='WEIGHT';elsif p_mode='SCAN'then p_mode:='BOTH';end if;
   end if;
  end if;
 end;
 function controller_allowed(p_domain clob,p_actor varchar2) return number is
  d json_object_t:=json_object_t.parse(p_domain);v_mode varchar2(10);v_independent number;
  v_case number:=d.get_number('case_task');v_id number:=d.get_number('document_id');v_known number:=0;v_count number;v_actor varchar2(100);
 begin
  settings_for_plan(p_domain,v_mode,v_independent);if v_independent=0 then return 1;end if;
  if p_actor is null then return 0;end if;
  if v_case is not null then
   for z in(select h.CREATED_BY,op.ACTOR,op.STATE from RRL_CASE_CARRIER_LOT h left join RRL_STOCK_OPERATION op on op.OPERATION_ID=h.CREATED_OPERATION
    where h.CASE_PICK_TASK_ID=v_case order by h.LOT_UID fetch first 201 rows only) loop
    v_known:=v_known+1;
    if v_known>200 or z.ACTOR is null or z.CREATED_BY is null or z.STATE!='APPLIED' or z.CREATED_BY!=z.ACTOR then return 0;end if;
    if z.ACTOR=p_actor then return 0;end if;
   end loop;
  else
   for z in(select m.CREATED_BY,op.ACTOR,op.STATE from RRL_CUSTOMER_ORDER_FULFILLMENT ff
    join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.TASK_ID=ff.PICKED_WAREHOUSE_TASK_ID
    left join RRL_STOCK_OPERATION op on op.OPERATION_ID=m.OPERATION_ID
    where ff.LEGACY_SBORKA_PALLET_ID=v_id order by m.OPERATION_ID fetch first 201 rows only) loop
    v_known:=v_known+1;
    if v_known>200 or z.ACTOR is null or z.CREATED_BY is null or z.STATE!='APPLIED' or z.CREATED_BY!=z.ACTOR then return 0;end if;
    if z.ACTOR=p_actor then return 0;end if;
   end loop;
  end if;
  if v_known=0 then return 0;end if;return 1;
 end;
 procedure assert_controller(p_domain clob,p_actor varchar2) is
 begin if controller_allowed(p_domain,p_actor)!=1 then raise_application_error(-20882,'QUALITY_INDEPENDENT_CONTROLLER_REQUIRED_ACTUAL_PICK_FACTS');end if;end;
 procedure sampling(p_domain clob,p_bucket out number,p_percent out number,p_selected out number,p_rescan out number) is
  d json_object_t:=json_object_t.parse(p_domain);v_id number:=d.get_number('document_id');v_ware number:=d.get_number('warehouse');
 begin
  select QC_SAMPLE_BUCKET,QC_SAMPLE_REQUIRED,QC_RESCAN_REQUIRED into p_bucket,p_selected,p_rescan from RRL_SBORKA_PALLETS where ID=v_id;
  p_percent:=json_object_t.parse(RRL_QC_SCOPE_READ.policy_json(p_domain)).get_number('sample_percent');
  if p_bucket is not null and p_bucket<p_percent*100 then p_selected:=1;end if;
 end;
 function full_scan_required(p_domain clob) return number is
  d json_object_t:=json_object_t.parse(p_domain);v_mode varchar2(10);v_independent number;v_bucket number;v_percent number;v_selected number;v_rescan number;
 begin
  settings_for_plan(p_domain,v_mode,v_independent);sampling(p_domain,v_bucket,v_percent,v_selected,v_rescan);
  if v_bucket is null and v_percent>0 then raise_application_error(-20886,'OUTGOING_CONTROL_PLAN_REQUIRED');end if;
  if v_mode in('SCAN','BOTH') or v_selected=1 or v_rescan=1 then return 1;end if;return 0;
 end;
 procedure assign_sampling(p_domain clob) is
  d json_object_t:=json_object_t.parse(p_domain);v_id number:=d.get_number('document_id');v_bucket number;v_percent number;v_selected number;v_rescan number;
 begin
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(v_id)));
  sampling(p_domain,v_bucket,v_percent,v_selected,v_rescan);
  if v_bucket is null then
   update RRL_SBORKA_PALLETS set QC_SAMPLE_BUCKET=trunc(dbms_random.value(0,10000)) where ID=v_id;
   sampling(p_domain,v_bucket,v_percent,v_selected,v_rescan);
  end if;
  if v_selected=1 then update RRL_SBORKA_PALLETS set QC_SAMPLE_REQUIRED=1 where ID=v_id;end if;
 end;
end;
/
