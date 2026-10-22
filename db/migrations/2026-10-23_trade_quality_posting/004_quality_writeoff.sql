create or replace package RRL_STOCK_QUALITY_WRITEOFF authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_EFFECT_CORE) as
 -- Owner of TRADE_QUALITY_WRITE_OFF: writes off the whole quarantined pallet of an approved quality case (WAITING_POSTING), exactly its
 -- frozen codes, in the posting runner's transaction together with the case state, the hold release and the outgoing document.
 procedure assert_scope(p_case number,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure validate_consume(p_case number,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_QUALITY_WRITEOFF as
 procedure fail(p_code varchar2)is begin raise_application_error(-20886,p_code);end;
 function hash_key(p_prefix varchar2,p_operation varchar2)return varchar2 is
 begin return p_prefix||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256));end;

 -- Current management right on the case's warehouse and write right on every owner of its codes (checked before and under the locks).
 procedure assert_scope(p_case number,p_actor varchar2)is v_ware number;n number;
 begin
  begin select WARE_ID into v_ware from RRL_TRADE_QUALITY_CASE where CASE_ID=p_case;
  exception when no_data_found then raise_application_error(-20882,'QUALITY_WRITE_OFF_SCOPE_REQUIRED');end;
  select RRL_ACCESS_API.allowed(p_actor,'tradecase_quality_post','WAREHOUSE',to_char(v_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'QUALITY_WRITE_OFF_SCOPE_REQUIRED');end if;
  for o in(select distinct a.OWNER_ID from RRL_TRADE_QUALITY_CASE_UNIT cu join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY
    where cu.CASE_ID=p_case)loop
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,v_ware,o.OWNER_ID,1);
  end loop;
 end;

 -- The whole frozen pallet, as it is now: anything that changed since the approval refuses the posting (no partial effect).
 procedure describe(p_request clob,p_actor varchar2,p_domain out json_object_t)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');s json_object_t:=d.get_object('source');
  v_case number:=s.get_number('case_id');v_expected number:=m.get_number('expected_case_version');q RRL_TRADE_QUALITY_CASE%rowtype;
  v_qty number;v_h number;v_ver number;v_uom varchar2(20);v_cell varchar2(60);v_article varchar2(160);v_policy number;n number;total number;actual number;
  unit_wire clob;key_wire clob;profiles clob;summary clob;j json_object_t:=json_object_t();
 begin
  if v_case is null or v_expected is null then fail('QUALITY_WRITE_OFF_REQUEST_INVALID');end if;
  begin select*into q from RRL_TRADE_QUALITY_CASE where CASE_ID=v_case;
  exception when no_data_found then fail('QUALITY_WRITE_OFF_CASE_REQUIRED');end;
  if s.get_number('warehouse_id')is null or s.get_number('warehouse_id')<>q.WARE_ID then fail('QUALITY_WRITE_OFF_WAREHOUSE_CONFLICT');end if;
  if q.STATE<>'WAITING_POSTING'then fail('QUALITY_WRITE_OFF_APPROVED_CASE_REQUIRED');end if;
  if q.VERSION_NO<>v_expected then raise_application_error(-20911,'VERSION_CONFLICT');end if;
  assert_scope(v_case,p_actor);
  select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM,CELL into v_qty,v_h,v_ver,v_uom,v_cell from RRL_REMAINS where UID_POLETA=q.PALLET_UID and REMAIN>0;
  if v_cell<>q.CELL or v_ver<>q.STOCK_VERSION or v_h<>0 then fail('QUALITY_WRITE_OFF_CURRENT_WHOLE_UNRESERVED_REQUIRED');end if;
  select count(*)into n from RRL_CELLS where CELL=v_cell and WARE_ID=q.WARE_ID and nvl(BLOCKED_FOR_REMAINS,0)=1;
  if n<>1 then fail('QUALITY_WRITE_OFF_QUARANTINE_REQUIRED');end if;
  select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and(CHILD_PALLET_UID=q.PALLET_UID or PARENT_UID=q.PALLET_UID);
  if n<>0 then fail('QUALITY_WRITE_OFF_STANDALONE_REQUIRED');end if;  -- not attached to a load unit or a shipment
  if RRL_TRADE_QUALITY_CASE_API.composition_hash(q.PALLET_UID)<>q.COMPOSITION_HASH then fail('QUALITY_COMPOSITION_CHANGED');end if;
  -- Exactly the frozen codes, available and unreserved, and nothing else on the pallet.
  select count(*),sum(u.BASE_QTY),
   json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,
    'version'value u.UNIT_VERSION,'origin_uid'value u.UID_PALLET,'unit_id'value u.UNIT_ID)order by u.PHYSICAL_UNIT_KEY returning clob),
   json_arrayagg(u.PHYSICAL_UNIT_KEY order by u.PHYSICAL_UNIT_KEY returning clob)
   into n,total,unit_wire,key_wire from RRL_TRADE_QUALITY_CASE_UNIT cu join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY
   where cu.CASE_ID=v_case and u.CURRENT_UID=q.PALLET_UID and u.CURRENT_CELL=v_cell and u.UNIT_VERSION=cu.UNIT_VERSION
    and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and u.BASE_UOM=v_uom;
  select count(*)into actual from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=q.PALLET_UID and STOCK_STATUS<>'ISSUED';
  select count(*)into total from RRL_TRADE_QUALITY_CASE_UNIT where CASE_ID=v_case;
  if n<1 or n>10000 or actual<>n or total<>n then fail('QUALITY_WRITE_OFF_EXACT_FROZEN_UNITS_REQUIRED');end if;
  select sum(u.BASE_QTY)into total from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=q.PALLET_UID and u.STOCK_STATUS<>'ISSUED';
  if total<>v_qty then fail('QUALITY_WRITE_OFF_EXACT_FROZEN_UNITS_REQUIRED');end if;
  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=q.PALLET_UID;
  select max(POLICY_VERSION)into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
  if v_policy is null then fail('QUALITY_WRITE_OFF_BASE_UOM_REQUIRED');end if;
  -- Marked codes: the regulatory withdrawal event is enqueued in the same transaction (target systems from the units' own codes).
  select json_arrayagg(json_object('system_code'value S)order by S returning clob)into profiles from(select distinct c.SYSTEM_CODE S
   from RRL_TRADE_QUALITY_CASE_UNIT cu join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY
   join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID where cu.CASE_ID=v_case);
  select json_arrayagg(json_object('sku_id'value g.SKU_ID,'owner_id'value g.OWNER_ID,'base_uom'value g.BASE_UOM,
    'base_qty'value RRL_STOCK_PLAN_HELPER.decimal_text(g.QTY),'units'value g.UNITS)order by g.SKU_ID,g.OWNER_ID returning clob)into summary
   from(select a.SKU_ID,a.OWNER_ID,u.BASE_UOM,sum(u.BASE_QTY)QTY,count(*)UNITS from RRL_TRADE_QUALITY_CASE_UNIT cu
    join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY
    where cu.CASE_ID=v_case group by a.SKU_ID,a.OWNER_ID,u.BASE_UOM)g;
  j.put('case_id',v_case);j.put('case_version',q.VERSION_NO);j.put('warehouse_id',q.WARE_ID);j.put('uid',q.PALLET_UID);j.put('article',v_article);
  j.put('cell',v_cell);j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));j.put('base_uom',v_uom);j.put('uom_version',v_policy);
  j.put('stock_version',v_ver);j.put('composition_hash',q.COMPOSITION_HASH);j.put('quality_hold_id',q.QUALITY_HOLD_ID);
  j.put('reason',q.REASON_TEXT);j.put('decision_note',q.DECISION_TEXT);j.put('approval_note',q.APPROVAL_TEXT);j.put('approved_by',q.APPROVED_BY);
  j.put('composition',json_array_t.parse(summary));j.put('unit_keys',json_array_t.parse(key_wire));j.put('units',json_array_t.parse(unit_wire));
  if profiles is not null then j.put('profiles',json_array_t.parse(profiles));end if;
  p_domain:=j;
 exception when no_data_found then fail('QUALITY_WRITE_OFF_SOURCE_REQUIRED');when too_many_rows then fail('QUALITY_WRITE_OFF_ONE_SOURCE_REQUIRED');
 end;

 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();keys json_array_t;
 begin
  describe(p_request,d.get_string('actor'),v);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TRADE_QUALITY_CASE',RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('case_id')));
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),v.get_string('cell'),null);
  keys:=v.get_array('unit_keys');
  for i in 0..keys.get_size-1 loop RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',keys.get_string(i));end loop;
  if v.has('profiles')then RRL_REGULATORY_API.declare_stock_events(p_operation,'MARKED_GOODS_DISPOSED',v.get_array('profiles').to_clob,r);end if;
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE',hash_key('STOCK.OUTBOX:',p_operation));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE',hash_key('SAP.OUTBOX:QUALITY_WRITE_OFF:',p_operation));
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;

 -- Called by RRL_STOCK_EFFECT_CORE.consume: the quarantine exception is granted only to the in-flight write-off of this exact case.
 procedure validate_consume(p_case number,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2)is
  op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);req clob;v json_object_t;
 begin
  select COMMAND_TYPE,CANONICAL_REQUEST into kind_name,req from RRL_STOCK_OPERATION where OPERATION_ID=op and STATE='IN_FLIGHT';
  if kind_name<>'TRADE_QUALITY_WRITE_OFF'then fail('QUALITY_WRITE_OFF_EXPLICIT_ROOT_REQUIRED');end if;
  describe(req,p_actor,v);
  if v.get_number('case_id')<>p_case or v.get_string('uid')<>p_uid or v.get_string('cell')<>p_cell or v.get_number('warehouse_id')<>p_ware
   or RRL_STOCK_MATH.quantity(v.get_string('quantity'))<>p_quantity then fail('QUALITY_WRITE_OFF_EXACT_SOURCE_REQUIRED');end if;
 exception when no_data_found then fail('QUALITY_WRITE_OFF_EXPLICIT_ROOT_REQUIRED');
 end;

 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');plan clob;v json_object_t;fresh json_object_t;
  j json_object_t:=json_object_t();payload json_object_t;v_case number;v_uid varchar2(200);v_hold number;v_version number;now timestamp with time zone:=systimestamp;
  gov_ids json_array_t;
 begin
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;
  v:=json_object_t.parse(plan).get_object('domain');describe(p_request,p_actor,fresh);
  if dbms_lob.compare(v.to_clob,fresh.to_clob)<>0 then raise_application_error(-20890,'CLOSURE_CHANGED: quality write-off');end if;
  v_case:=v.get_number('case_id');v_uid:=v.get_string('uid');v_hold:=v.get_number('quality_hold_id');v_version:=v.get_number('case_version');
  RRL_STOCK_EFFECT_CORE.consume(v_uid,v.get_string('cell'),RRL_STOCK_MATH.quantity(v.get_string('quantity')),v.get_string('base_uom'),
   v.get_number('uom_version'),v.get_number('warehouse_id'),p_actor,1,p_units=>v.get_array('unit_keys').to_clob,p_quality_case=>v_case);
  update RRL_TRADE_QUALITY_CASE set STATE='POSTED',POSTED_BY=p_actor,POSTED_AT=now,POST_OPERATION_ID=op,VERSION_NO=VERSION_NO+1
   where CASE_ID=v_case and STATE='WAITING_POSTING'and VERSION_NO=v_version;
  if sql%rowcount<>1 then raise_application_error(-20890,'CLOSURE_CHANGED: quality case');end if;
  RRL_TRACEABILITY_API.release_quality_hold(v_hold,p_actor,'WRITTEN_OFF '||op);  -- the stock is gone; the hold has done its job
  j.put('operation_id',op);j.put('status','POSTED');j.put('case_id',v_case);j.put('pallet_identifier',v_uid);j.put('quantity',v.get_string('quantity'));
  j.put('base_uom',v.get_string('base_uom'));j.put('physical_unit_count',v.get_array('unit_keys').get_size);j.put('external_sap_ack',false);
  if v.has('profiles')then
   gov_ids:=json_array_t.parse(RRL_REGULATORY_API.enqueue_stock_events(op,'MARKED_GOODS_DISPOSED',v.to_clob,v.get_array('units').to_clob,v.get_array('profiles').to_clob));
   j.put('regulatory_event_ids',gov_ids);j.put('regulatory_status','PENDING');j.put('external_regulatory_ack',false);
  end if;
  -- Outgoing document with the exact written-off composition; the external answer is a later, separate state.
  payload:=json_object_t.parse(v.to_clob);payload.put('operation_id',op);payload.put('status','POSTED');payload.put('actor',p_actor);
  insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values(hash_key('QUALITY.WRITE_OFF:',op),'TRADE_QUALITY_WRITTEN_OFF',payload.to_clob);
  p_result:=j.to_clob;
 end;
end;
/
