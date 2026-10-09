declare n number;begin select count(*) into n from RRL_STOCK_OPERATION; if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_PREVENT_CODE_ROLLBACK');end if;end;
/
@@092_event_trigger_rollback.sql
drop trigger RRL_STOCK_COMPAT_FLAG_GUARD;
drop trigger RRL_STOCK_SETTING_AUDIT_GUARD;
create or replace package RRL_STOCK_CTX_API authid definer

 accessible by(package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_BALANCE_CORE,package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_UNIT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_CONFIG_API,package RRL_STOCK_POSTING_API,package RRL_STOCK_OPERATION_CORE) as

 procedure open_operation(p_operation varchar2,p_mode varchar2 default 'EXPLICIT');

 procedure open_configuration(p_actor varchar2,p_permission varchar2);

 procedure begin_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null);

 procedure begin_staging(p_uid varchar2,p_cell varchar2);

 procedure end_effect;

 procedure clear_operation;

end;
/

create or replace package RRL_STOCK_BALANCE_CORE authid definer

 accessible by(package RRL_STOCK_MES_MOVEMENT_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_POSTING_API,package RRL_STOCK_MOVE_CORE,

  package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RECEIPT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_EFFECT_CORE) as

 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,

   p_base_uom varchar2,p_uom_version number,p_expected_version number default null);

 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number);

 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,

   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null);

end;
/

create or replace package RRL_STOCK_OPERATION_CORE authid definer

 accessible by(package RRL_STOCK_POSTING_API) as

 procedure begin_operation(p_request clob,p_actor varchar2,p_operation varchar2,p_kind varchar2,p_replay out clob,p_plan clob default null);

 procedure finish_operation(p_operation varchar2,p_result clob);

end;
/

create or replace package RRL_STOCK_MOVE_CORE authid definer

 accessible by(package RRL_STOCK_POSTING_API) as

 procedure manual_whole(p_request clob,p_actor varchar2,p_result out clob);

end;
/

create or replace package RRL_STOCK_POSTING_API authid definer as

 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null);

 procedure execute_prepared(p_result out clob);

 procedure reset_connection;

end;
/

create or replace package body RRL_STOCK_CTX_API as

 procedure open_operation(p_operation varchar2,p_mode varchar2 default 'EXPLICIT') is v_state varchar2(20);

 begin

  select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;

  if v_state!='ACTIVE' then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE'); end if;

  if p_mode not in('EXPLICIT','COMPAT') then raise_application_error(-20861,'STOCK_CONTEXT_MODE_INVALID'); end if;

  RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',p_operation));

  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then raise_application_error(-20862,'POSTING_ALREADY_ENTERED'); end if;

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','OPERATION_ID',p_operation);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','TX_ID',dbms_transaction.local_transaction_id(false));

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','MODE',p_mode);

 end;

 procedure begin_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null) is v_tx varchar2(100);

 begin

  v_tx:=dbms_transaction.local_transaction_id(false);

  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or v_tx is null or

   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=v_tx

   or p_kind is null or p_kind not in('STOCK','JOURNAL','RESERVATION','UNIT') then raise_application_error(-20863,'EFFECT_CONTEXT_FORBIDDEN');end if;

  if sys_context('RRL_STOCK_WRITE_CTX','EFFECT') is not null then raise_application_error(-20862,'NESTED_EFFECT_FORBIDDEN');end if;

  if p_uid is not null then RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));end if;

  if p_kind in('STOCK','JOURNAL','UNIT') and p_uid is null then raise_application_error(-20863,'EFFECT_UID_REQUIRED');end if;

  if p_kind='RESERVATION' then

   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(p_row_id)));

  end if;

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT',p_kind);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_UID',p_uid);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_CELL',p_cell);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_ROW_ID',RRL_STOCK_PLAN_HELPER.decimal_text(p_row_id));

 end;

 procedure begin_staging(p_uid varchar2,p_cell varchar2) is

 begin

  begin_effect('UNIT',p_uid,p_cell);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT','RECEIPT_CAPTURE');

 end;

 procedure end_effect is

 begin

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT',null);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_UID',null);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_CELL',null);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_ROW_ID',null);

 end;

 procedure open_configuration(p_actor varchar2,p_permission varchar2) is

 begin

  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then raise_application_error(-20862,'POSTING_ALREADY_ENTERED');end if;

  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','TX_ID',dbms_transaction.local_transaction_id(false));

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','MODE','CONFIG');

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','ACTOR',p_actor);

  dbms_session.set_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION',p_permission);

 end;

 procedure clear_operation is

 begin

  dbms_session.clear_context('RRL_STOCK_WRITE_CTX',null);

 end;

end;
/

create or replace package body RRL_STOCK_BALANCE_CORE as

 procedure assert_context is v_tx varchar2(100);

 begin

  v_tx:=dbms_transaction.local_transaction_id(false);

  if v_tx is null or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null

   or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=v_tx then

   raise_application_error(-20863,'STOCK_WRITE_FORBIDDEN');

  end if;

 end;

 procedure apply_delta(p_uid varchar2,p_cell varchar2,p_delta_p number,p_delta_h number,

   p_base_uom varchar2,p_uom_version number,p_expected_version number default null) is

  v_p number;v_h number;v_ver number;v_uom varchar2(20);v_article varchar2(160);v_scale number;v_exists boolean:=true;

 begin

  assert_context;

  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));

  if p_cell is null or p_base_uom is null or p_delta_p is null or p_delta_h is null then

   raise_application_error(-20864,'STOCK_IDENTITY_OR_DELTA_MISSING');

  end if;

  select ARTICUL into v_article from RRL_PALLETS where UID_PALLET=p_uid;

  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('SKU',v_article),4);

  begin

   select BASE_SCALE into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article

    and INPUT_UOM=p_base_uom and BASE_UOM=p_base_uom and POLICY_VERSION=p_uom_version

    and NUMERATOR=DENOMINATOR;

  exception when no_data_found then raise_application_error(-20865,'BASE_UOM_POLICY_REQUIRED');

  end;

  RRL_STOCK_MATH.assert_base(p_delta_p,v_scale);RRL_STOCK_MATH.assert_base(p_delta_h,v_scale);

  begin

   select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM into v_p,v_h,v_ver,v_uom

    from RRL_REMAINS where UID_POLETA=p_uid and CELL=p_cell for update;

  exception when no_data_found then v_exists:=false;v_p:=0;v_h:=0;v_ver:=0;v_uom:=p_base_uom;

  end;

  if v_uom is null or v_uom!=p_base_uom then raise_application_error(-20866,'STOCK_BASE_UOM_CONFLICT'); end if;

  if p_expected_version is not null and p_expected_version!=v_ver then raise_application_error(-20867,'VERSION_CONFLICT'); end if;

  RRL_STOCK_MATH.assert_base(v_p+p_delta_p,v_scale);RRL_STOCK_MATH.assert_base(v_h+p_delta_h,v_scale);

  if v_p+p_delta_p<0 then raise_application_error(-20868,'STOCK_INSUFFICIENT'); end if;

  if v_h+p_delta_h<0 or v_h+p_delta_h>v_p+p_delta_p then raise_application_error(-20869,'RESERVATION_CONFLICT'); end if;

  RRL_STOCK_CTX_API.begin_effect('STOCK',p_uid,p_cell);

  if v_exists then

   update RRL_REMAINS set REMAIN=REMAIN+p_delta_p,HARD_RESERVED_BASE=HARD_RESERVED_BASE+p_delta_h,

    STOCK_VERSION=STOCK_VERSION+1,TIME_OF_LAST_UPDATE=sysdate

    where UID_POLETA=p_uid and CELL=p_cell and STOCK_VERSION=v_ver;

   if sql%rowcount!=1 then raise_application_error(-20867,'VERSION_CONFLICT'); end if;

  else

   insert into RRL_REMAINS(UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM,TIME_OF_LAST_UPDATE)

    values(p_uid,p_cell,p_delta_p,p_delta_h,1,p_base_uom,sysdate);

  end if;

  RRL_STOCK_CTX_API.end_effect;

 exception when others then RRL_STOCK_CTX_API.end_effect;raise;

 end;

 procedure write_event(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,

   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null) is

  v_prihod number;v_op varchar2(100);

 begin

  assert_context;

  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));

  if p_qty is null or p_qty=0 or p_base_uom is null or p_line is null or p_line<1 or p_leg is null or p_leg<1 then

   raise_application_error(-20870,'JOURNAL_FACT_INVALID');

  end if;

  v_op:=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');

  select PRIHOD_NAKLAD_ID into v_prihod from RRL_PALLETS where UID_PALLET=p_uid;

  select RRL_EVENT_ID_SQ.nextval into p_event from dual;

  RRL_STOCK_CTX_API.begin_effect('JOURNAL',p_uid,nvl(p_from,p_to));

  insert into RRL_EVENTS(ID_EVENT,CELL_FROM,CELL_TO,DATE_EVENT,COUNT_EVENT,TYPE_EVENT,UID_POLETA,

   USER_ID,PRIHOD_NAKL_ID,OTHOD_NAKL_ID,PALLET_ROW_ID,OPERATION_ID,LINE_NO,LEG_NO,BASE_QTY,BASE_UOM,UOM_POLICY_VERSION)

   values(p_event,p_from,p_to,sysdate,abs(p_qty),p_type,p_uid,p_actor,v_prihod,p_outgoing_doc,p_pallet_row,v_op,p_line,p_leg,p_qty,p_base_uom,p_uom_version);

  RRL_STOCK_CTX_API.end_effect;

 exception when others then RRL_STOCK_CTX_API.end_effect;raise;

 end;

 procedure write_move(p_uid varchar2,p_from varchar2,p_to varchar2,p_qty number,p_base_uom varchar2,p_uom_version number,p_line number,p_actor varchar2,p_event out number) is

 begin

  if p_from is null or p_to is null or p_from=p_to or p_qty is null or p_qty<=0 then raise_application_error(-20870,'MOVE_JOURNAL_CONTRACT');end if;

  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_from),4);

  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CELL',p_to),4);

  write_event(p_uid,p_from,p_to,p_qty,p_base_uom,p_uom_version,p_line,1,2,p_actor,p_event);

 end;

 procedure write_leg(p_uid varchar2,p_from varchar2,p_to varchar2,p_signed_qty number,p_base_uom varchar2,

   p_uom_version number,p_line number,p_leg number,p_type number,p_actor varchar2,p_event out number,p_outgoing_doc number default null,p_pallet_row number default null) is

 begin

  if p_signed_qty is null or p_signed_qty=0 or

   (p_signed_qty<0 and (p_from is null or p_to is not null)) or

   (p_signed_qty>0 and (p_to is null or p_from is not null)) then

   raise_application_error(-20870,'SIGNED_LEG_LOCATION_CONFLICT');

  end if;

  write_event(p_uid,p_from,p_to,p_signed_qty,p_base_uom,p_uom_version,p_line,p_leg,p_type,p_actor,p_event,p_outgoing_doc,p_pallet_row);

 end;

end;
/

create or replace package body RRL_STOCK_OPERATION_CORE as

 procedure begin_operation(p_request clob,p_actor varchar2,p_operation varchar2,p_kind varchar2,p_replay out clob,p_plan clob default null) is

  v_saved clob;v_hash varchar2(64);v_actor varchar2(50);v_state varchar2(20);v_base varchar2(100);

 begin

  p_replay:=null;

  RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',p_operation));

  if p_request is null or dbms_lob.getlength(p_request)>4194304 or p_actor is null

   or length(p_actor)>50 or p_operation is null or length(p_operation)>100 then raise_application_error(-20871,'OPERATION_CONTRACT_INVALID'); end if;

  v_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));

  begin

   select CANONICAL_REQUEST,ACTOR,STATE,RESULT_JSON into v_saved,v_actor,v_state,p_replay

    from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;

   if v_actor!=p_actor or dbms_lob.getlength(v_saved)!=dbms_lob.getlength(p_request)

    or dbms_lob.compare(v_saved,p_request)!=0 then raise_application_error(-20872,'OPERATION_CONFLICT'); end if;

   if v_state!='APPLIED' then raise_application_error(-20873,'UNFINISHED_OPERATION: unexpected committed envelope'); end if;

   return;

  exception when no_data_found then p_replay:=null;

  end;

  RRL_STOCK_CTX_API.open_operation(p_operation);

  select BASELINE_ID into v_base from RRL_STOCK_RELEASE where RELEASE_ID=1;

  if v_base is null then raise_application_error(-20874,'BASELINE_REQUIRED'); end if;

  insert into RRL_STOCK_OPERATION(OPERATION_ID,CONTRACT_VERSION,COMMAND_TYPE,ACTOR,REQUEST_HASH,

   CANONICAL_REQUEST,RESOLVED_PLAN_JSON,STATE,BASELINE_ID) values(p_operation,2,p_kind,p_actor,v_hash,p_request,p_plan,'IN_FLIGHT',v_base);

 end;

 procedure finish_operation(p_operation varchar2,p_result clob) is

 begin

  RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',p_operation));

  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or

   sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation or p_result is null then

   raise_application_error(-20863,'STOCK_WRITE_FORBIDDEN');

  end if;

  update RRL_STOCK_OPERATION set RESULT_JSON=p_result,STATE='APPLIED',APPLIED_AT=systimestamp

   where OPERATION_ID=p_operation and STATE='IN_FLIGHT';

  if sql%rowcount!=1 then raise_application_error(-20875,'OPERATION_FINISH_CONFLICT'); end if;

 end;

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

  v_seen seen_set;v_line_seen seen_set;

 begin

  v_doc.on_error(1);

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

   if v_quality is not null and v_quality!='RELEASED' then raise_application_error(-20884,'QUALITY_HANDLER_REQUIRED'); end if;

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

   RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_from,-v_q,0,v_base,v_policy,v_version);

   RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_to,v_q,0,v_base,v_policy);

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

create or replace package body RRL_STOCK_POSTING_API as

 g_request clob;g_resolution clob;g_actor varchar2(50);g_operation varchar2(100);g_kind varchar2(80);g_tx varchar2(100);g_prepared boolean:=false;

 procedure reset_connection is

 begin

  RRL_STOCK_CTX_API.clear_operation;RRL_STOCK_LOCK_API.clear_plan;

  g_request:=null;g_resolution:=null;g_actor:=null;g_operation:=null;g_kind:=null;g_tx:=null;g_prepared:=false;

 end;

 procedure prepare_command(p_request clob,p_actor varchar2,p_replay out clob,p_hints clob default null) is

  v_doc json_object_t;v_policies clob;v_resources clob;v_exists number;v_release varchar2(20);v_domain clob;v_resolution json_object_t:=json_object_t();

  v_plan json_array_t:=json_array_t();v_entry json_object_t:=json_object_t();v_resources_json json_array_t:=json_array_t();

 begin

  p_replay:=null;

  if g_prepared or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then

   raise_application_error(-20862,'POSTING_ALREADY_ENTERED');

  end if;

  if p_request is null or dbms_lob.getlength(p_request)>4194304 then raise_application_error(-20871,'OPERATION_CONTRACT_INVALID'); end if;

  v_doc:=json_object_t.parse(p_request);v_doc.on_error(1);

  g_operation:=v_doc.get_string('operation_id');g_kind:=v_doc.get_string('command_type');

  if v_doc.get_number('contract_version') is null or v_doc.get_number('contract_version')!=2 or v_doc.get_string('actor') is null

   or v_doc.get_string('actor')!=p_actor or p_actor is null or length(p_actor)>50

   or g_operation is null or length(g_operation)>100 or g_kind is null then

   raise_application_error(-20871,'OPERATION_CONTRACT_INVALID');

  end if;

  -- Immutable committed replay is considered before any mutable article/cell/UOM validation.

  select count(*) into v_exists from RRL_STOCK_OPERATION where OPERATION_ID=g_operation;

  if v_exists!=0 then

   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('RELEASE','STOCK')));v_entry.put('mode',4);v_plan.append(v_entry);

   v_entry:=json_object_t();v_entry.put('rank',10);

   v_entry.put('key_hex',rawtohex(RRL_STOCK_LOCK_API.resource_key('OP',g_operation)));v_resources_json.append(v_entry);

   v_policies:=v_plan.to_clob;v_resources:=v_resources_json.to_clob;

  else

   if g_kind='MANUAL_MOVE' then RRL_STOCK_COMMAND_PLAN.compile_move(p_request,g_operation,v_policies,v_resources);

   elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);

   elsif g_kind='MES_RELEASE_TO_PRODUCTION' then RRL_STOCK_MES_SUPPLY_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);

   elsif g_kind='DOCUMENT_RELEASE_RESERVATIONS' then RRL_STOCK_DOC_RESERVE_CMD.compile_release(p_request,g_operation,v_policies,v_resources,v_domain);

   elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.compile_reserve(p_request,g_operation,v_policies,v_resources,v_domain);

   elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.compile_shipment(p_request,g_operation,v_policies,v_resources,v_domain);

   elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.compile_move(p_request,g_operation,v_policies,v_resources,v_domain);

   elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_PLAN.compile_movements(p_request,g_operation,v_policies,v_resources,v_domain);

   elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_PLAN.compile_receipt(p_request,g_operation,p_hints,v_policies,v_resources,v_domain);

   elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_PLAN.compile_task(p_request,g_operation,v_policies,v_resources,v_domain);

   elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);

   else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED');end if;

  end if;

  RRL_STOCK_LOCK_API.begin_plan;

  RRL_STOCK_LOCK_API.acquire_policies(v_policies);

  RRL_STOCK_LOCK_API.acquire_resources(v_resources);

  select STATE into v_release from RRL_STOCK_RELEASE where RELEASE_ID=1;

  if v_release!='ACTIVE' then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE'); end if;

  if v_domain is not null then v_resolution.put('domain',json_object_t.parse(v_domain));end if;

  v_resolution.put('stock_before',json_array_t.parse(RRL_STOCK_INVARIANT_CORE.snapshot_stock(v_resources)));

  v_resolution.put('resources',json_array_t.parse(v_resources));

  v_resolution.put('policies',json_array_t.parse(v_policies));

  RRL_STOCK_OPERATION_CORE.begin_operation(p_request,p_actor,g_operation,g_kind,p_replay,v_resolution.to_clob);

  if p_replay is not null then return; end if;

  g_request:=p_request;g_resolution:=v_resolution.to_clob;g_actor:=p_actor;g_tx:=dbms_transaction.local_transaction_id(false);g_prepared:=true;

  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.begin_staging(v_resolution.get_object('domain').get_string('uid'),v_resolution.get_object('domain').get_string('receive_cell'));end if;

 end;

 procedure execute_prepared(p_result out clob) is

  v_outbox number;v_existing number;v_key varchar2(100);v_json json_object_t;v_resolved json_object_t;

 begin

  if not g_prepared or g_tx is null or dbms_transaction.local_transaction_id(false) is null

   or g_tx!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20850,'WRITE_PLAN_VIOLATION'); end if;

  if g_kind='SAP_RECEIPT' then RRL_STOCK_CTX_API.end_effect;end if;

  if g_kind='MANUAL_MOVE' then RRL_STOCK_MOVE_CORE.manual_whole(g_request,g_actor,p_result);

  elsif g_kind='MES_RAW_TASK_CANCEL' then RRL_STOCK_MES_CANCEL_CMD.execute_command(g_request,g_actor,p_result);

   elsif g_kind='MES_RELEASE_TO_PRODUCTION' then RRL_STOCK_MES_SUPPLY_CMD.execute_command(g_request,g_actor,p_result);

   elsif g_kind='DOCUMENT_RELEASE_RESERVATIONS' then RRL_STOCK_DOC_RESERVE_CMD.execute_release(g_request,g_actor,p_result);

  elsif g_kind='WAVE_RESERVE_SOURCES' then RRL_STOCK_WAVE_CMD.execute_reserve(g_request,g_actor,p_result);

  elsif g_kind in('SHIP_DOCUMENT','SHIP_PALLET') then RRL_STOCK_SHIPPING_CORE.execute_shipment(g_request,g_actor,p_result);

  elsif g_kind in('INTERNAL_MOVE','MOVE_QUARANTINE') then RRL_STOCK_INTERNAL_CMD.execute_move(g_request,g_actor,p_result);

  elsif g_kind='MES_MOVEMENTS' then RRL_STOCK_MES_MOVEMENT_CORE.execute_movements(g_request,g_actor,p_result);

  elsif g_kind='SAP_RECEIPT' then RRL_STOCK_RECEIPT_CORE.execute_receipt(g_request,g_actor,p_result);

  elsif g_kind='TASK_COMPLETE' then RRL_STOCK_TASK_CORE.execute_task(g_request,g_actor,p_result);

  elsif g_kind in('RESERVATION_CREATE','RESERVATION_PROMOTE','RESERVATION_RELEASE','RESERVATION_CANCEL','RESERVATION_CONSUME') then RRL_STOCK_RESERVATION_CMD.execute_command(g_request,g_actor,p_result);

  else raise_application_error(-20888,'COMMAND_HANDLER_NOT_INSTALLED'); end if;

  v_resolved:=json_object_t.parse(g_resolution);

  RRL_STOCK_INVARIANT_CORE.verify_posting(v_resolved.get_array('resources').to_clob,v_resolved.get_array('stock_before').to_clob,g_operation);

  v_key:='STOCK:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(g_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256));

  RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE','STOCK.OUTBOX:'||substr(v_key,7)));

  select count(*) into v_existing from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=v_key;

  if v_existing!=0 then raise_application_error(-20889,'OUTBOX_IDENTITY_CONFLICT'); end if;

  v_outbox:=RRL_TRACEABILITY_API.enqueue_event('STOCK_POSTED','STOCK_OPERATION',g_operation,v_key,p_result,'WMS',g_operation);

  v_json:=json_object_t.parse(p_result);v_json.put('outbox_id',v_outbox);p_result:=v_json.to_clob;

  RRL_STOCK_OPERATION_CORE.finish_operation(g_operation,p_result);

  g_prepared:=false;

 end;

end;
/
