-- First bounded handler. Reserved/marked/nested/partial moves require their dedicated handlers.
create or replace package RRL_STOCK_MOVE_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure manual_whole(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_MOVE_CORE as
 procedure manual_whole(p_request clob,p_actor varchar2,p_result out clob) is
  v_doc json_object_t:=json_object_t.parse(p_request);v_source json_object_t;v_lines json_array_t;
  v_line json_object_t;v_result json_object_t:=json_object_t();v_facts json_array_t:=json_array_t();v_fact json_object_t;
  v_uid varchar2(200);v_article varchar2(160);v_actual varchar2(160);v_from varchar2(60);v_to varchar2(60);
  v_unit varchar2(20);v_base varchar2(20);v_sscc varchar2(32);v_quality varchar2(40);v_warehouse number;
  v_n number;v_q number;v_p number;v_h number;v_version number;v_num number;v_den number;v_scale number;
  v_policy number;v_marked number;v_event_from number;v_event_to number;v_line_no number;v_expected number;
  type seen_set is table of boolean index by varchar2(200);
  v_seen seen_set;v_line_seen seen_set;v_compat varchar2(20);
 begin
  v_doc.on_error(1);
  if v_doc.get_string('command_type')='COMPAT_MANUAL_MOVE' then
   select nvl(max(SETTING_VALUE),'0') into v_compat from RRL_SYSTEM_SETTINGS where SETTING_KEY='STOCK_LEGACY_TRIGGER_ENABLED';
   if v_compat!='1' then raise_application_error(-20863,'LEGACY_STOCK_POSTING_DISABLED');end if;
  end if;
  if RRL_HAS_WRIGHT(p_actor,'stock_posting_manual_move')!=1 then raise_application_error(-20882,'MANUAL_MOVE_FORBIDDEN'); end if;
  v_source:=v_doc.get_object('source');v_source.on_error(1);
  if v_source.get_string('type') is null or v_source.get_string('type')!='MANUAL' or v_source.get_string('reason') is null
   or length(v_source.get_string('reason'))>1000 then raise_application_error(-20883,'MANUAL_SOURCE_REQUIRED'); end if;
  v_warehouse:=v_source.get_number('warehouse_id');
  if v_warehouse is null or v_warehouse<1 or v_warehouse!=trunc(v_warehouse) then raise_application_error(-20883,'WAREHOUSE_REQUIRED'); end if;
  if v_doc.get_array('units').get_size!=0 then raise_application_error(-20884,'COMPOSITION_HANDLER_REQUIRED'); end if;
  v_lines:=v_doc.get_array('lines');
  for i in 0..v_lines.get_size-1 loop
   v_line:=treat(v_lines.get(i) as json_object_t);v_line.on_error(1);
   v_uid:=v_line.get_string('uid');v_article:=v_line.get_string('article');
   v_from:=v_line.get_string('source_cell');v_to:=v_line.get_string('target_cell');
   v_unit:=v_line.get_string('unit');v_line_no:=v_line.get_number('line_number');
   if v_line_no is null or v_line_no<1 or v_line_no!=trunc(v_line_no)
    or v_line_seen.exists(to_char(v_line_no,'TM9')) then raise_application_error(-20881,'COMMAND_LINE_ID_INVALID'); end if;
   v_line_seen(to_char(v_line_no,'TM9')):=true;
   if v_seen.exists(v_uid) then raise_application_error(-20885,'PALLET_REPEATED'); end if;
   v_seen(v_uid):=true;
   if v_from=v_to or v_line.get_string('target_uid') is null or v_line.get_string('target_uid')!=v_uid
    or v_line.get_string('reservation_action') is null or v_line.get_string('reservation_action')!='NONE' or not v_line.get('reservation_id').is_null then
    raise_application_error(-20886,'DEDICATED_MOVE_HANDLER_REQUIRED');
   end if;
   RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',v_uid));
   RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_uid));
   RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('SKU',v_article),4);
   select ARTICUL,SSCC,QUALITY_STATUS into v_actual,v_sscc,v_quality from RRL_PALLETS where UID_PALLET=v_uid;
   if v_actual!=v_article or v_actual is null then raise_application_error(-20887,'PALLET_ARTICLE_CONFLICT'); end if;

   -- Fail closed: no guessed regulatory status and no rebuilding of existing composition.
   select MARKING_REQUIRED into v_marked from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_article;
   select count(*) into v_n from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article;
   if v_marked!=0 or v_marked is null or v_n!=0 then raise_application_error(-20884,'MARKED_HANDLER_REQUIRED'); end if;
   select count(*) into v_n from RRL_WMS_RECEIPT_UNIT where UID_PALLET=v_uid;
   if v_n!=0 then raise_application_error(-20884,'UNIT_HANDLER_REQUIRED'); end if;
   select count(*) into v_n from RRL_CRPT_AGGREGATION where UID_PALLET=v_uid or SSCC=v_sscc or PARENT_SSCC=v_sscc;
   if v_n!=0 then raise_application_error(-20884,'HU_HANDLER_REQUIRED'); end if;
   RRL_STOCK_LOCATION_CORE.assert_ordinary(v_from,v_warehouse,'SOURCE');
   RRL_STOCK_LOCATION_CORE.assert_ordinary(v_to,v_warehouse,'TARGET');
   select max(POLICY_VERSION) into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit;
   select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE into v_base,v_num,v_den,v_scale
    from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_unit and POLICY_VERSION=v_policy;
   v_q:=RRL_STOCK_MATH.convert_exact(v_line.get_string('quantity'),v_num,v_den,v_scale);
   select max(POLICY_VERSION) into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=v_base and BASE_UOM=v_base and NUMERATOR=1 and DENOMINATOR=1;
   if v_policy is null then raise_application_error(-20868,'MANUAL_BASE_POLICY_REQUIRED');end if;
   select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into v_p,v_h,v_version from RRL_REMAINS where UID_POLETA=v_uid and CELL=v_from;
   if v_line.has('expected_stock_version') and not v_line.get('expected_stock_version').is_null then
    v_expected:=v_line.get_number('expected_stock_version');
    if v_expected is null or v_expected!=v_version then raise_application_error(-20867,'VERSION_CONFLICT'); end if;
   end if;
   select count(*) into v_n from RRL_REMAINS where UID_POLETA=v_uid and CELL!=v_from and (REMAIN!=0 or HARD_RESERVED_BASE!=0);
   if v_n!=0 or v_p!=v_q or v_h!=0 then raise_application_error(-20886,'WHOLE_UNRESERVED_PALLET_REQUIRED'); end if;
   select count(*) into v_n from RRL_STOCK_RESERVATION where UID_PALLET=v_uid and RESERVATION_KIND='HARD'
    and STATUS in('ACTIVE','ALLOCATED','PICKING');
   if v_n!=0 then raise_application_error(-20886,'RESERVATION_HANDLER_REQUIRED'); end if;
   if sys_context('RRL_STOCK_WRITE_CTX','MODE')='EXPLICIT' then
   RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_from,-v_q,0,v_base,v_policy,v_version);
   RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_to,v_q,0,v_base,v_policy);
   end if;
   RRL_STOCK_BALANCE_CORE.write_move(v_uid,v_from,v_to,v_q,v_base,v_policy,v_line_no,p_actor,v_event_from);
   v_event_to:=v_event_from;
   v_fact:=json_object_t();v_fact.put('line_number',v_line_no);v_fact.put('uid',v_uid);
   v_fact.put('source_cell',v_from);v_fact.put('target_cell',v_to);v_fact.put('base_quantity',to_char(v_q,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));
   v_fact.put('base_uom',v_base);v_fact.put('uom_policy_version',v_policy);
   v_fact.put('source_event_id',v_event_from);v_fact.put('target_event_id',v_event_to);v_facts.append(v_fact);
  end loop;
  v_result.put('operation_id',v_doc.get_string('operation_id'));v_result.put('command_type','MANUAL_MOVE');
  v_result.put('status','APPLIED');v_result.put('lines',v_facts);p_result:=v_result.to_clob;
 end;
end;
/
