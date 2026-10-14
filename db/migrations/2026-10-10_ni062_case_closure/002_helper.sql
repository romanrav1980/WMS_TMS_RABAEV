create or replace package RRL_STOCK_CASE_CLOSE authid definer accessible by(package RRL_STOCK_STORE_CASE_CMD) as
 procedure actor_scope(p_case varchar2,p_actor varchar2,p_action varchar2);
 procedure describe(p_case varchar2,p_metadata clob,p_actor varchar2,p_domain in out nocopy json_object_t);
 procedure declare_resources(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure persist(p_domain json_object_t,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_CASE_CLOSE as
 procedure actor_scope(p_case varchar2,p_actor varchar2,p_action varchar2)is v_ware number;n number;
 begin
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;if n!=1 then raise_application_error(-20882,'CASE_CURRENT_ACTIVE_ACTOR_REQUIRED');end if;
 if p_action='FINDING'then return;end if;
 select WARE_ID into v_ware from RRL_TT_HU_LOAD_FACT l join RRL_STORE_DISCREPANCY_CASE c on c.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID where c.CASE_ID=p_case;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=v_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN');
 if n!=1 then raise_application_error(-20882,'CASE_CURRENT_WAREHOUSE_MANAGER_REQUIRED');end if;
 end;
 procedure describe(p_case varchar2,p_metadata clob,p_actor varchar2,p_domain in out nocopy json_object_t)is
 m json_object_t:=json_object_t.parse(p_metadata);issue RRL_STORE_DISCREPANCY_CASE%rowtype;
 v_exp varchar2(100);v_sec varchar2(100);v_ware number;v_reason varchar2(2000);v_ref varchar2(255);n number;
 begin
 select *into issue from RRL_STORE_DISCREPANCY_CASE where CASE_ID=p_case;
 if issue.STATUS!='ASSIGNED' or issue.EXPEDITION_USER is null or issue.SECURITY_USER is null or issue.EXPEDITION_USER=issue.SECURITY_USER then raise_application_error(-20886,'CASE_CLOSE_ASSIGNED_INVESTIGATION_REQUIRED');end if;
 if p_actor=issue.EXPEDITION_USER or p_actor=issue.SECURITY_USER then raise_application_error(-20882,'CASE_CLOSE_INDEPENDENT_KRO_REQUIRED');end if;
 select OPERATION_ID into v_exp from RRL_STORE_CASE_FINDING where CASE_ID=p_case and ROLE_CODE='EXPEDITION'and REPORTED_BY=issue.EXPEDITION_USER order by CREATED_AT desc,OPERATION_ID desc fetch first 1 row only;
 select OPERATION_ID into v_sec from RRL_STORE_CASE_FINDING where CASE_ID=p_case and ROLE_CODE='SECURITY'and REPORTED_BY=issue.SECURITY_USER order by CREATED_AT desc,OPERATION_ID desc fetch first 1 row only;
 select count(*)into n from RRL_STORE_DELIVERY_OBLIGATION where CASE_ID=p_case and STATUS not in('LOSS_CONFIRMED','CLOSED');
 if n!=0 then raise_application_error(-20886,'CASE_CLOSE_UNRESOLVED_QUANTITY_OBLIGATIONS');end if;
 select count(*)into n from RRL_STORE_RECEIPT_FACT where OPERATION_ID=p_case and nvl(json_value(COMPOSITION_JSON,'$.physical_unit_count'returning number),1)!=0;
 if n!=0 then raise_application_error(-20886,'CASE_CLOSE_MARKED_REGULATORY_FLOW_REQUIRED');end if;
 select count(*)into n from RRL_STORE_RECEIPT_LINE l where l.OPERATION_ID=p_case and(exists(select 1 from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=l.ARTICLE)or exists(select 1 from RRL_SKU_RECEIPT_POLICY p where p.ARTICUL=l.ARTICLE and p.MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU p where p.ARTICUL=l.ARTICLE and p.CRPT_REQUIRED=1));
 if n!=0 then raise_application_error(-20886,'CASE_CLOSE_CURRENT_MARKED_POLICY_REQUIRED');end if;
 v_reason:=m.get_string('reason');v_ref:=m.get_string('decision_reference');
 if trim(v_reason)is null or lengthb(v_reason)>2000 or trim(v_ref)is null or lengthb(v_ref)>255 then raise_application_error(-20886,'CASE_CLOSE_REASON_AND_DECISION_REQUIRED');end if;
 select WARE_ID into v_ware from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=issue.LOAD_OPERATION_ID;
 p_domain.put('warehouse_id',v_ware);p_domain.put('expedition_finding_op',v_exp);p_domain.put('security_finding_op',v_sec);p_domain.put('reason',v_reason);p_domain.put('decision_reference',v_ref);
 exception when no_data_found then raise_application_error(-20886,'CASE_CLOSE_BOTH_ORIGINAL_FINDINGS_REQUIRED');end;
 procedure declare_resources(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t)is
 begin
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_CASE_CLOSURE',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_CASE_FINDING',p_domain.get_string('expedition_finding_op'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_CASE_FINDING',p_domain.get_string('security_finding_op'));
 RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE','SAP.OUTBOX:CASE.CLOSE:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 end;
 procedure persist(p_domain json_object_t,p_actor varchar2)is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_case varchar2(100);v_ware number;v_exp varchar2(100);v_sec varchar2(100);v_reason varchar2(2000);v_ref varchar2(255);payload json_object_t;body clob;event_id varchar2(100);
 begin
 v_case:=p_domain.get_string('case_id');v_ware:=p_domain.get_number('warehouse_id');v_exp:=p_domain.get_string('expedition_finding_op');v_sec:=p_domain.get_string('security_finding_op');v_reason:=p_domain.get_string('reason');v_ref:=p_domain.get_string('decision_reference');
 insert into RRL_STORE_CASE_CLOSURE(OPERATION_ID,CASE_ID,WARE_ID,EXPEDITION_FINDING_OP,SECURITY_FINDING_OP,REASON_TEXT,DECISION_REFERENCE,ACTOR)values(op,v_case,v_ware,v_exp,v_sec,v_reason,v_ref,p_actor);
 payload:=json_object_t.parse(p_domain.to_clob);payload.put('operation_id',op);payload.put('status','CLOSED');payload.put('actor',p_actor);payload.put('warehouse_stock_changed',false);payload.put('external_sap_ack',false);body:=payload.to_clob;
 event_id:='CASE.CLOSE:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values(event_id,'STORE_DISCREPANCY_CLOSED',body);
 end;
end;
/
