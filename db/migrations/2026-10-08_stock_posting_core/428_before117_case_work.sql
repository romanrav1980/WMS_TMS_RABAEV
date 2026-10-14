create or replace package RRL_STOCK_STORE_CASE_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_STORE_CASE_CMD as
 function timestamp_utc(p_text varchar2) return timestamp with time zone is
 begin
  if p_text is null or not regexp_like(p_text,'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{6}[+]00:00$','c') then raise_application_error(-20886,'CASE_EXPLICIT_UTC_DEADLINE_REQUIRED');end if;
  return to_timestamp_tz(p_text,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
 end;
 procedure investigator(p_user varchar2) is n number;
 begin
  select count(*) into n from RUSERS where ID=p_user and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'store_case_investigate')=1;
  if n!=1 then raise_application_error(-20882,'CASE_ACTIVE_INVESTIGATOR_REQUIRED');end if;
 end;
 procedure describe_case(p_case varchar2,p_metadata clob,p_actor varchar2,p_domain out json_object_t) is
  m json_object_t:=json_object_t.parse(p_metadata);issue RRL_STORE_DISCREPANCY_CASE%rowtype;v_action varchar2(30):=m.get_string('action');v_permission varchar2(30);
  v_exp varchar2(50);v_sec varchar2(50);v_role varchar2(20);v_report varchar2(32767);v_reason varchar2(32767);v_deadline timestamp with time zone;v_line number;n number;obligation RRL_STORE_DELIVERY_OBLIGATION%rowtype;source_line RRL_STORE_RECEIPT_LINE%rowtype;v_units number;
 begin
  v_permission:=case v_action when 'ASSIGN' then 'store_case_manage' when 'FINDING' then 'store_case_investigate' when 'LOSS_CONFIRM' then 'store_loss_confirm' else null end;
  if v_permission is null then raise_application_error(-20886,'CASE_ACTION_UNSUPPORTED');end if;
  if RRL_HAS_WRIGHT(p_actor,v_permission)!=1 then raise_application_error(-20882,'CASE_ACTION_FORBIDDEN');end if;
  select * into issue from RRL_STORE_DISCREPANCY_CASE where CASE_ID=p_case;
  if m.get_number('expected_version') is null or m.get_number('expected_version')!=issue.CASE_VERSION then raise_application_error(-20886,'CASE_VERSION_CONFLICT');end if;
  if issue.STATUS not in('OPEN','ASSIGNED') then raise_application_error(-20886,'CASE_ALREADY_RESOLVED');end if;
  p_domain:=json_object_t();p_domain.put('case_id',p_case);p_domain.put('action',v_action);p_domain.put('version_before',issue.CASE_VERSION);p_domain.put('load_operation_id',issue.LOAD_OPERATION_ID);
  if v_action='ASSIGN' then
   v_exp:=m.get_string('expedition_user');v_sec:=m.get_string('security_user');
   if v_exp is null or v_sec is null or v_exp=v_sec then raise_application_error(-20886,'CASE_SEPARATE_INVESTIGATORS_REQUIRED');end if;
   investigator(v_exp);investigator(v_sec);v_deadline:=timestamp_utc(m.get_string('search_deadline'));
   if v_deadline<=systimestamp then raise_application_error(-20886,'CASE_FUTURE_SEARCH_DEADLINE_REQUIRED');end if;
   p_domain.put('expedition_user',v_exp);p_domain.put('security_user',v_sec);p_domain.put('search_deadline',m.get_string('search_deadline'));
  elsif v_action='FINDING' then
   if issue.STATUS!='ASSIGNED' then raise_application_error(-20886,'CASE_INVESTIGATION_ASSIGNMENT_REQUIRED');end if;
   v_role:=m.get_string('role');v_report:=m.get_string('report');
   if v_role is null or v_role not in('EXPEDITION','SECURITY') or trim(v_report) is null or lengthb(v_report)>2000 then raise_application_error(-20886,'CASE_FINDING_ROLE_AND_REPORT_REQUIRED');end if;
   if (v_role='EXPEDITION' and (issue.EXPEDITION_USER is null or issue.EXPEDITION_USER!=p_actor))
     or(v_role='SECURITY' and(issue.SECURITY_USER is null or issue.SECURITY_USER!=p_actor))then raise_application_error(-20882,'CASE_ASSIGNED_INVESTIGATOR_ONLY');end if;
   p_domain.put('role',v_role);p_domain.put('report',v_report);
  else
   if issue.STATUS!='ASSIGNED' or issue.SEARCH_DEADLINE is null then raise_application_error(-20886,'CASE_INVESTIGATION_ASSIGNMENT_REQUIRED');end if;
   if p_actor=issue.EXPEDITION_USER or p_actor=issue.SECURITY_USER then raise_application_error(-20882,'CASE_LOSS_INDEPENDENT_KRO_REQUIRED');end if;
   select count(distinct ROLE_CODE) into n from RRL_STORE_CASE_FINDING where CASE_ID=p_case
    and((ROLE_CODE='EXPEDITION' and REPORTED_BY=issue.EXPEDITION_USER)or(ROLE_CODE='SECURITY' and REPORTED_BY=issue.SECURITY_USER));
   if n!=2 then raise_application_error(-20886,'CASE_BOTH_INVESTIGATOR_FINDINGS_REQUIRED');end if;
   v_line:=m.get_number('line_no');v_reason:=m.get_string('reason');
   if v_line is null or v_line!=trunc(v_line) or v_line<1 or trim(v_reason) is null or lengthb(v_reason)>2000 then raise_application_error(-20886,'CASE_LOSS_LINE_AND_REASON_REQUIRED');end if;
   select * into obligation from RRL_STORE_DELIVERY_OBLIGATION where CASE_ID=p_case and LINE_NO=v_line and KIND='MISSING_INVESTIGATION';
   if obligation.STATUS not in('OPEN','SEARCHING') then raise_application_error(-20886,'CASE_MISSING_OBLIGATION_ALREADY_DECIDED');end if;
   select * into source_line from RRL_STORE_RECEIPT_LINE where OPERATION_ID=p_case and LINE_NO=v_line;
   if obligation.BASE_QTY!=source_line.MISSING_BASE_QTY or obligation.BASE_UOM!=source_line.BASE_UOM then raise_application_error(-20886,'CASE_ORIGINAL_MISSING_QUANTITY_CONFLICT');end if;
   select nvl(json_value(COMPOSITION_JSON,'$.physical_unit_count' returning number),1) into v_units from RRL_STORE_RECEIPT_FACT where OPERATION_ID=p_case;
   if v_units!=0 then raise_application_error(-20886,'CASE_MARKED_LOSS_UNIT_AND_REGULATORY_FLOW_REQUIRED');end if;
   p_domain.put('line_no',v_line);p_domain.put('lot_uid',source_line.LOT_UID);p_domain.put('article',source_line.ARTICLE);p_domain.put('base_uom',source_line.BASE_UOM);
   p_domain.put('loss_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(obligation.BASE_QTY));p_domain.put('reason',v_reason);
  end if;
 exception when no_data_found then raise_application_error(-20886,'CASE_SOURCE_OR_MISSING_OBLIGATION_NOT_FOUND');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);v_case varchar2(100):=d.get_object('source').get_string('case_id');v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();v_action varchar2(30);
 begin
  describe_case(v_case,d.get_object('metadata').to_clob,d.get_string('actor'),v);v_action:=v.get_string('action');
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_DISCREPANCY_CASE',v_case);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_CASE_ACTION',p_operation);
  if v_action='FINDING' then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_CASE_FINDING',p_operation);end if;
  if v_action='LOSS_CONFIRM' then
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_LOSS_RECOGNITION',p_operation);
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_DELIVERY_OBLIGATION',v_case||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('line_no'))||':MISSING_INVESTIGATION');
  end if;
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');op varchar2(100):=d.get_string('operation_id');v_case varchar2(100):=d.get_object('source').get_string('case_id');
  plan clob;v json_object_t;fresh json_object_t;version_before number;version_after number;v_action varchar2(30);details clob;j json_object_t:=json_object_t();v_exp varchar2(50);v_sec varchar2(50);v_deadline timestamp with time zone;v_role varchar2(20);v_report varchar2(2000);v_line number;v_lot varchar2(200);v_article varchar2(160);v_unit varchar2(20);v_qty number;v_reason varchar2(2000);
 begin
  select CASE_VERSION into version_before from RRL_STORE_DISCREPANCY_CASE where CASE_ID=v_case for update;
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  describe_case(v_case,m.to_clob,p_actor,fresh);
  if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'CASE_VERSION_OR_SOURCE_CONFLICT');end if;
  version_after:=version_before+1;v_action:=v.get_string('action');details:=v.to_clob;
  insert into RRL_STORE_CASE_ACTION(OPERATION_ID,CASE_ID,ACTION_CODE,VERSION_BEFORE,VERSION_AFTER,ACTOR,DETAILS_JSON)values(op,v_case,v_action,version_before,version_after,p_actor,details);
  if v_action='ASSIGN' then
   v_exp:=v.get_string('expedition_user');v_sec:=v.get_string('security_user');v_deadline:=timestamp_utc(v.get_string('search_deadline'));
   update RRL_STORE_DISCREPANCY_CASE set STATUS='ASSIGNED',EXPEDITION_USER=v_exp,SECURITY_USER=v_sec,ASSIGNED_TO=v_exp,SEARCH_DEADLINE=v_deadline,CASE_VERSION=version_after,LAST_DECISION_OPERATION=op where CASE_ID=v_case;
  elsif v_action='FINDING' then
   v_role:=v.get_string('role');v_report:=v.get_string('report');
   insert into RRL_STORE_CASE_FINDING(OPERATION_ID,CASE_ID,ROLE_CODE,REPORT_TEXT,REPORTED_BY)values(op,v_case,v_role,v_report,p_actor);
  else
   v_line:=v.get_number('line_no');v_lot:=v.get_string('lot_uid');v_article:=v.get_string('article');v_unit:=v.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('loss_quantity'));v_reason:=v.get_string('reason');
   update RRL_STORE_DELIVERY_OBLIGATION set STATUS='LOSS_CONFIRMED' where CASE_ID=v_case and LINE_NO=v_line and KIND='MISSING_INVESTIGATION' and STATUS in('OPEN','SEARCHING');
   if sql%rowcount!=1 then raise_application_error(-20886,'CASE_MISSING_OBLIGATION_ALREADY_DECIDED');end if;
   insert into RRL_STORE_LOSS_RECOGNITION(OPERATION_ID,CASE_ID,LINE_NO,LOT_UID,ARTICLE,BASE_UOM,BASE_QTY,REASON_TEXT,CONFIRMED_BY)values(op,v_case,v_line,v_lot,v_article,v_unit,v_qty,v_reason,p_actor);
   j.put('loss_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));j.put('base_uom',v_unit);j.put('original_load_operation',v.get_string('load_operation_id'));
  end if;
  if v_action!='ASSIGN' then update RRL_STORE_DISCREPANCY_CASE set CASE_VERSION=version_after,LAST_DECISION_OPERATION=op where CASE_ID=v_case;end if;
  j.put('operation_id',op);j.put('case_id',v_case);j.put('action',v_action);j.put('case_version',version_after);j.put('warehouse_stock_changed',false);j.put('government_ack_created',false);p_result:=j.to_clob;
 end;
end;
/
