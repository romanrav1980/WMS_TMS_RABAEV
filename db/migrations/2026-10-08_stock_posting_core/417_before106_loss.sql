create or replace package RRL_STOCK_TARE_LOSS authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/

create or replace package body RRL_STOCK_TARE_LOSS as
 procedure describe_command(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');s json_object_t:=d.get_object('source');kind varchar2(80):=d.get_string('command_type');
 v_claim varchar2(100);claim RRL_TARE_LOSS_CLAIM%rowtype;v_owner number;v_type number;v_condition varchar2(10);v_qty number;v_key raw(32);v_p number;v_version number;v_held number;n number;
 v_reason varchar2(32767):=m.get_string('reason');v_ref varchar2(32767):=m.get_string('decision_reference');v_outcome varchar2(12);
 begin
 select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;if n!=1 then raise_application_error(-20882,'TARE_ACTIVE_ACTOR_REQUIRED');end if;
 if trim(v_reason) is null or lengthb(v_reason)>2000 or trim(v_ref) is null or lengthb(v_ref)>255 then raise_application_error(-20886,'TARE_LOSS_REASON_DECISION_REQUIRED');end if;
 if kind='TARE_LOSS_REPORT' then
  if RRL_HAS_WRIGHT(p_actor,'tare_loss_report')!=1 then raise_application_error(-20882,'TARE_LOSS_REPORT_PERMISSION_REQUIRED');end if;
  v_owner:=m.get_number('owner_ware_id');v_type:=m.get_number('pallet_type_id');v_condition:=m.get_string('condition');
  if v_owner is null or v_type is null or v_condition is null or v_condition not in('GOOD','DAMAGED') then raise_application_error(-20886,'TARE_WAREHOUSE_LOSS_TYPE_REQUIRED');end if;
  if not regexp_like(m.get_string('quantity'),'^[0-9]{1,18}$') then raise_application_error(-20886,'TARE_INTEGER_QUANTITY_REQUIRED');end if;
  v_qty:=RRL_STOCK_MATH.quantity(m.get_string('quantity'));
  RRL_TARE_PARTICIPANT.warehouse_actor(p_actor,v_owner);
 else
  if RRL_HAS_WRIGHT(p_actor,'tare_writeoff')!=1 then raise_application_error(-20882,'TARE_LOSS_DECISION_PERMISSION_REQUIRED');end if;
  v_claim:=s.get_string('claim_operation_id');select * into claim from RRL_TARE_LOSS_CLAIM where OPERATION_ID=v_claim;
  if claim.ACTOR=p_actor then raise_application_error(-20882,'TARE_INDEPENDENT_LOSS_DECISION_REQUIRED');end if;
  v_owner:=claim.OWNER_WARE_ID;v_type:=claim.PALLET_TYPE_ID;v_condition:=claim.CONDITION_CODE;v_qty:=claim.QUANTITY;
  v_outcome:=m.get_string('outcome');if v_outcome is null or v_outcome not in('WRITE_OFF','REJECT') then raise_application_error(-20886,'TARE_LOSS_EXPLICIT_OUTCOME_REQUIRED');end if;
  select count(*) into n from RRL_TARE_LOSS_DECISION where CLAIM_OPERATION_ID=v_claim;if n!=0 then raise_application_error(-20886,'TARE_LOSS_ALREADY_DECIDED');end if;
 end if;
 v_key:=RRL_TARE_BALANCE_KEY(v_owner,v_type,v_condition,'WAREHOUSE',RRL_STOCK_PLAN_HELPER.decimal_text(v_owner));
 select QUANTITY,BALANCE_VERSION into v_p,v_version from RRL_TARE_BALANCE where BALANCE_KEY=v_key;
 v_held:=RRL_TARE_PLANNING.held_quantity(v_key);
 if kind='TARE_LOSS_REPORT' then
  if m.get_number('expected_version') is null or m.get_number('expected_version')!=v_version then raise_application_error(-20886,'TARE_LOSS_BALANCE_VERSION_CONFLICT');end if;
  RRL_TARE_PLANNING.assert_available(v_key,v_p,v_qty);
 elsif v_p<v_held or v_qty>v_p then raise_application_error(-20886,'TARE_LOSS_PENDING_PHYSICAL_BALANCE_CONFLICT');end if;
 p_domain:=json_object_t();p_domain.put('claim_operation_id',v_claim);p_domain.put('owner_ware_id',v_owner);p_domain.put('pallet_type_id',v_type);p_domain.put('condition',v_condition);
 p_domain.put('balance_key',rawtohex(v_key));p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));p_domain.put('physical_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_p));p_domain.put('balance_version',v_version);p_domain.put('held_quantity',v_held);
 p_domain.put('outcome',v_outcome);p_domain.put('reason',v_reason);p_domain.put('decision_reference',v_ref);
 exception when no_data_found then raise_application_error(-20886,'TARE_LOSS_EXISTING_BALANCE_CLAIM_REQUIRED');end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
 describe_command(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_BALANCE',v.get_string('balance_key'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_LOSS_CLAIM',case when d.get_string('command_type')='TARE_LOSS_REPORT' then p_operation else v.get_string('claim_operation_id')end);
 if d.get_string('command_type')='TARE_LOSS_DECIDE' then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TARE_LOSS_DECISION',p_operation);end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');kind varchar2(80):=d.get_string('command_type');plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_key raw(32);v_claim varchar2(100);v_owner number;v_type number;v_condition varchar2(10);v_qty number;v_outcome varchar2(12);v_reason varchar2(2000);v_ref varchar2(255);n number;
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');v_key:=hextoraw(v.get_string('balance_key'));v_claim:=v.get_string('claim_operation_id');
 select QUANTITY into n from RRL_TARE_BALANCE where BALANCE_KEY=v_key for update;
 if v_claim is not null then select QUANTITY into n from RRL_TARE_LOSS_CLAIM where OPERATION_ID=v_claim for update;end if;
 describe_command(p_request,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: tare loss');end if;
 v_owner:=v.get_number('owner_ware_id');v_type:=v.get_number('pallet_type_id');v_condition:=v.get_string('condition');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));v_outcome:=v.get_string('outcome');v_reason:=v.get_string('reason');v_ref:=v.get_string('decision_reference');
 if kind='TARE_LOSS_REPORT' then
 insert into RRL_TARE_LOSS_CLAIM(OPERATION_ID,BALANCE_KEY,OWNER_WARE_ID,PALLET_TYPE_ID,CONDITION_CODE,QUANTITY,REASON_TEXT,DECISION_REFERENCE,ACTOR)values(op,v_key,v_owner,v_type,v_condition,v_qty,v_reason,v_ref,p_actor);
 else
 insert into RRL_TARE_LOSS_DECISION(OPERATION_ID,CLAIM_OPERATION_ID,OUTCOME,REASON_TEXT,DECISION_REFERENCE,ACTOR)values(op,v_claim,v_outcome,v_reason,v_ref,p_actor);
 end if;
 update RRL_TARE_BALANCE set QUANTITY=QUANTITY-case when v_outcome='WRITE_OFF' then v_qty else 0 end,BALANCE_VERSION=BALANCE_VERSION+1,LAST_OPERATION_ID=op,UPDATED_AT=systimestamp where BALANCE_KEY=v_key;
 j.put('operation_id',op);j.put('status',case when kind='TARE_LOSS_REPORT' then 'REPORTED' else v_outcome end);j.put('quantity',v.get_string('quantity'));j.put('total_tare_changed',v_outcome='WRITE_OFF');j.put('goods_stock_changed',false);p_result:=j.to_clob;
 end;
end;
/
