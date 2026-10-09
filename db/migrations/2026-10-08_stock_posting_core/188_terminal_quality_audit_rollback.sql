declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
create or replace package RRL_STOCK_PALLET_QC_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_PALLET_QC_CMD as
 procedure quality(p_request clob,p_id number,p_pass out number,p_ship out number,p_expected out number,p_tolerance out number) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v_uid varchar2(150);
  v_errors number;v_gross number;v_wood number;auto_ship number;v_kind varchar2(20);
 begin
  v_uid:=d.get_object('source').get_string('pallet_identifier');v_kind:=m.get_string('quality_kind');
  select nvl(w.SPIS_OTBOR_ON_SCAN_OPALL,0) into auto_ship from RRL_SBORKA_PALLETS p join RRL_WARES w on w.ID=p.WARE_ID where p.ID=p_id and p.PALLET_UID=v_uid;
  p_pass:=0;p_ship:=0;p_expected:=null;p_tolerance:=null;
  if v_kind='SCAN' then
   v_errors:=m.get_number('error_count');
   if v_errors is null or v_errors<0 or v_errors!=trunc(v_errors) then raise_application_error(-20871,'QUALITY_ERROR_COUNT_INVALID');end if;
   if v_errors=0 then p_pass:=1;end if;
  elsif v_kind in('WEIGHT','WEIGHT2') then
   v_gross:=RRL_STOCK_MATH.quantity(m.get_string('gross_weight'));v_wood:=RRL_STOCK_MATH.quantity(m.get_string('wood_weight'));
   if v_gross<v_wood then raise_application_error(-20871,'QUALITY_NET_WEIGHT_NEGATIVE');end if;
   p_tolerance:=RRL_TT_POGRESHNOST(p_id);
   p_expected:=case when v_kind='WEIGHT2' then RRL_PALLET_WEIGHT2(v_uid) else RRL_PALLET_WEIGHT(v_uid) end;
   if p_tolerance is null or p_tolerance<=0 or p_expected is null or p_expected<0 then raise_application_error(-20887,'QUALITY_WEIGHT_POLICY_REQUIRED');end if;
   if abs(v_gross-v_wood-p_expected)<p_tolerance then p_pass:=1;end if;
  else raise_application_error(-20871,'QUALITY_KIND_INVALID');end if;
  if p_pass=1 and auto_ship=1 and v_kind in('SCAN','WEIGHT2') then p_ship:=1;end if;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);sh json_object_t;q json_object_t:=json_object_t();v json_object_t:=json_object_t();
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v_uid varchar2(150);v_id number;ware number;passed number;shipped number;expected number;tolerance number;
 begin
  v_uid:=d.get_object('source').get_string('pallet_identifier');
  select ID,WARE_ID into v_id,ware from RRL_SBORKA_PALLETS where PALLET_UID=v_uid;
  quality(p_request,v_id,passed,shipped,expected,tolerance);
  if shipped=1 then
   sh:=json_object_t.parse(p_request);sh.put('command_type','SHIP_PALLET');
   RRL_STOCK_SHIPPING_CORE.compile_shipment(sh.to_clob,p_operation,p_policies,p_resources,p_domain);
   f:=json_array_t.parse(p_policies);r:=json_array_t.parse(p_resources);v:=json_object_t.parse(p_domain);
  else
   RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
   RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
   RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(v_id));
   for z in(select ID from RRL_SBORKA_PALLET_ROWS where PALLET_UID=v_uid order by ID) loop
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_SBORKA_PALLET_ROWS',RRL_STOCK_PLAN_HELPER.decimal_text(z.ID));
   end loop;
  end if;
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WARES',RRL_STOCK_PLAN_HELPER.decimal_text(ware));
  q.put('pallet_id',v_id);q.put('identifier',v_uid);q.put('warehouse',ware);q.put('passed',passed);q.put('ship',shipped);q.put('expected',expected);q.put('tolerance',tolerance);
  v.put('quality',q);p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');q json_object_t;v json_object_t;
  sh json_object_t;j json_object_t:=json_object_t();plan clob;shipment clob;op varchar2(100);v_uid varchar2(150);v_id number;ware number;actual_ware number;
  passed number;shipped number;expected number;tolerance number;v_condition number;gross number;wood number;errors number;note varchar2(1000);picker varchar2(100);v_kind varchar2(20);n number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'outgoing_pallet_check')!=1 and RRL_HAS_WRIGHT(p_actor,'stock_posting_shipping')!=1 and RRL_HAS_WRIGHT(p_actor,'CLOSE_OTHOD_NAKLAD')!=1 then
   raise_application_error(-20882,'OUTGOING_QUALITY_FORBIDDEN');end if;
  op:=d.get_string('operation_id');select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(plan).get_object('domain');q:=v.get_object('quality');v_id:=q.get_number('pallet_id');v_uid:=q.get_string('identifier');ware:=q.get_number('warehouse');
  select WARE_ID,CONDITION into actual_ware,v_condition from RRL_SBORKA_PALLETS where ID=v_id and PALLET_UID=v_uid for update;
  if actual_ware!=ware or nvl(v_condition,0)>=2 then raise_application_error(-20886,'QUALITY_PALLET_ALREADY_CLOSED');end if;
  select ID into n from RRL_WARES where ID=ware for update;
  for z in(select ID from RRL_SBORKA_PALLET_ROWS where PALLET_UID=v_uid order by ID for update) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLET_ROWS',RRL_STOCK_PLAN_HELPER.decimal_text(z.ID)));
  end loop;
  quality(p_request,v_id,passed,shipped,expected,tolerance);
  if passed!=q.get_number('passed') or shipped!=q.get_number('ship')
   or nvl(expected,-1)!=nvl(q.get_number('expected'),-1) or nvl(tolerance,-1)!=nvl(q.get_number('tolerance'),-1) then
   raise_application_error(-20890,'CLOSURE_CHANGED: quality calculation');end if;
  v_kind:=m.get_string('quality_kind');
  if v_kind='SCAN' then
   errors:=m.get_number('error_count');note:=m.get_string('note');picker:=m.get_string('picker');
   update RRL_SBORKA_PALLETS set PROOVED_BY_SCAN=passed,COUNT_OF_ERRORS=errors,PRIM=note,SBORSHIK=nvl(picker,SBORSHIK),KLADOVSHIK=p_actor where ID=v_id;
  else
   gross:=RRL_STOCK_MATH.quantity(m.get_string('gross_weight'));wood:=RRL_STOCK_MATH.quantity(m.get_string('wood_weight'));
   update RRL_SBORKA_PALLETS set TRIAL_WEIGHT=gross,WOOD_WEIGHT=wood,VESOVSHIK=p_actor,PROOVED=passed,
    STATE=case when passed=1 then unistr('\041F\0440\043E\0432\0435\0440\0435\043D\0412\0435\0441\0430\043C\0438') else unistr('\0412\044B\0434\0430\043D \0432 \0441\0431\043E\0440\043A\0443') end where ID=v_id;
   insert into RRL_SBORKA_PALLETS_HISTORY(PALLET_UID,USER_ID,ZONE,EVENT,WEIGHT)
    values(v_uid,p_actor,'STOCK_QC',case when passed=1 then 'WEIGHT_PASSED' else 'WEIGHT_FAILED' end,gross-wood);
  end if;
  if shipped=1 then
   sh:=json_object_t.parse(p_request);sh.put('command_type','SHIP_PALLET');
   RRL_STOCK_SHIPPING_CORE.execute_shipment(sh.to_clob,p_actor,shipment);j.put('shipment',json_object_t.parse(shipment));
  end if;
  j.put('operation_id',op);j.put('verified',passed);j.put('shipped',shipped);j.put('return_code',case when v_kind='SCAN' then 0 else passed end);p_result:=j.to_clob;
 end;
end;
/
