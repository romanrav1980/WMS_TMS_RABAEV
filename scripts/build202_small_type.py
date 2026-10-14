from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni042_small_final_weight");out={}
out[str(f/"001_schema.sql")]="alter table RRL_PALLET_TYPE add(FINAL_WEIGHT_REQUIRED number(1)default 0 not null constraint RRL_PT_FINAL_WEIGHT_CK check(FINAL_WEIGHT_REQUIRED in(0,1)));\n"
out[str(f/"002_api.sql")]="""create or replace package RRL_PALLET_TYPE_API authid definer as
 procedure upsert_request(p_request clob,p_actor varchar2,p_id out number);
end;
/
create or replace package body RRL_PALLET_TYPE_API as
 procedure clear_context is begin dbms_session.clear_context('RRL_PALLET_TYPE_CTX',null,'TX_ID');dbms_session.clear_context('RRL_PALLET_TYPE_CTX',null,'ACTOR');dbms_session.clear_context('RRL_PALLET_TYPE_CTX',null,'TYPE_ID');end;
 procedure upsert_request(p_request clob,p_actor varchar2,p_id out number)is
  j json_object_t:=json_object_t.parse(p_request);id number;code varchar2(50);name_value varchar2(160);class_value varchar2(20);
  volume number;weight number;len_mm number;width_mm number;height_mm number;max_clients number;active number;required number;n number;
 begin
  if p_request is null or dbms_lob.getlength(p_request)>16000 then raise_application_error(-20881,'PALLET_TYPE_REQUEST_BOUND');end if;
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if n!=1 or RRL_HAS_WRIGHT(p_actor,'case_pick_manage')!=1 then raise_application_error(-20882,'PALLET_TYPE_MANAGE_FORBIDDEN');end if;
  RRL_STOCK_LOCK_API.assert_held(6,RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'));
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_POLICY_GUARD','WAREHOUSE.METADATA'));
  id:=j.get_number('pallet_type_id');code:=upper(trim(j.get_string('pallet_type_code')));name_value:=trim(j.get_string('pallet_type_name'));
  class_value:=upper(trim(j.get_string('load_unit_class')));volume:=j.get_number('default_volume_m3');weight:=j.get_number('default_weight_kg');
  len_mm:=j.get_number('length_mm');width_mm:=j.get_number('width_mm');height_mm:=j.get_number('height_mm');
  max_clients:=j.get_number('default_max_client_pallets');active:=j.get_number('active');
  if code is null or name_value is null or class_value is null or nvl(volume,0)<0 or nvl(weight,0)<0 or nvl(len_mm,0)<0
   or nvl(width_mm,0)<0 or nvl(height_mm,0)<0 or max_clients is null or max_clients not between 1 and 3 or max_clients!=trunc(max_clients)
   or active is null or active not in(0,1) then raise_application_error(-20886,'PALLET_TYPE_FIELDS_INVALID');end if;
  if id is null then
   begin select PALLET_TYPE_ID into id from RRL_PALLET_TYPE where PALLET_TYPE_CODE=code;
   exception when no_data_found then select RRL_PALLET_TYPE_SQ.nextval into id from dual;end;
  elsif id<1 or id!=trunc(id)then raise_application_error(-20886,'PALLET_TYPE_ID_INVALID');end if;
  required:=null;
  if j.has('final_weight_required')and not j.get('final_weight_required').is_null then required:=case when j.get_boolean('final_weight_required')then 1 else 0 end;end if;
  dbms_session.set_context('RRL_PALLET_TYPE_CTX','TX_ID',dbms_transaction.local_transaction_id(true));
  dbms_session.set_context('RRL_PALLET_TYPE_CTX','ACTOR',p_actor);dbms_session.set_context('RRL_PALLET_TYPE_CTX','TYPE_ID',RRL_STOCK_PLAN_HELPER.decimal_text(id));
  merge into RRL_PALLET_TYPE d using(select id PALLET_TYPE_ID from dual)s on(d.PALLET_TYPE_ID=s.PALLET_TYPE_ID)
  when matched then update set PALLET_TYPE_CODE=code,PALLET_TYPE_NAME=name_value,LOAD_UNIT_CLASS=class_value,
   DEFAULT_VOLUME_M3=volume,DEFAULT_WEIGHT_KG=weight,LENGTH_MM=len_mm,WIDTH_MM=width_mm,HEIGHT_MM=height_mm,
   DEFAULT_MAX_CLIENT_PALLETS=max_clients,ACTIVE=active,FINAL_WEIGHT_REQUIRED=nvl(required,d.FINAL_WEIGHT_REQUIRED),UPDATED_AT=systimestamp,UPDATED_BY=p_actor
  when not matched then insert(PALLET_TYPE_ID,PALLET_TYPE_CODE,PALLET_TYPE_NAME,LOAD_UNIT_CLASS,DEFAULT_VOLUME_M3,DEFAULT_WEIGHT_KG,
   LENGTH_MM,WIDTH_MM,HEIGHT_MM,DEFAULT_MAX_CLIENT_PALLETS,ACTIVE,FINAL_WEIGHT_REQUIRED,CREATED_AT,CREATED_BY)
   values(id,code,name_value,class_value,volume,weight,len_mm,width_mm,height_mm,max_clients,active,nvl(required,0),systimestamp,p_actor);
  clear_context;p_id:=id;
 exception when others then clear_context;raise;
 end;
end;
/
create context RRL_PALLET_TYPE_CTX using RRL_PALLET_TYPE_API;
"""
out[str(f/"003_guard.sql")]="""create or replace trigger RRL_PALLET_TYPE_FINAL_GUARD before insert or update of FINAL_WEIGHT_REQUIRED on RRL_PALLET_TYPE for each row
begin
 if inserting and :new.FINAL_WEIGHT_REQUIRED=0 then return;end if;
 if sys_context('RRL_PALLET_TYPE_CTX','TX_ID')is null or sys_context('RRL_PALLET_TYPE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_PALLET_TYPE_CTX','ACTOR')is null or sys_context('RRL_PALLET_TYPE_CTX','TYPE_ID')!=RRL_STOCK_PLAN_HELPER.decimal_text(:new.PALLET_TYPE_ID)
  then raise_application_error(-20863,'PALLET_TYPE_FINAL_WEIGHT_TRUSTED_OWNER_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(6,RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'));
end;
/
"""
s=(f/"000_before_policy.sql").read_text(encoding="utf-8")
anchor=" function controller_allowed(p_domain clob,p_actor varchar2) return number;"
s=s.replace(anchor," procedure settings_for_plan(p_domain clob,p_mode out varchar2,p_independent out number);\n"+anchor,1)
anchor=" function controller_allowed(p_domain clob,p_actor varchar2) return number is"
new=""" procedure settings_for_plan(p_domain clob,p_mode out varchar2,p_independent out number)is
  d json_object_t:=json_object_t.parse(p_domain);case_id number:=d.get_number('case_task');required number;
 begin
  settings(d.get_number('warehouse'),p_mode,p_independent);
  if case_id is not null then
   select t.FINAL_WEIGHT_REQUIRED into required from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE t on t.PALLET_TYPE_ID=c.PALLET_TYPE_ID
    where c.CASE_PICK_TASK_ID=case_id;
   if required=1 then
    if p_mode in('NONE','ANY')then p_mode:='WEIGHT';elsif p_mode='SCAN'then p_mode:='BOTH';end if;
   end if;
  end if;
 end;
"""
assert anchor in s;s=s.replace(anchor,new+anchor,1)
s=s.replace("settings(d.get_number('warehouse'),v_mode,v_independent);","settings_for_plan(p_domain,v_mode,v_independent);")
out[str(f/"004_policy.sql")]=s
s=(f/"000_before_gate.sql").read_text(encoding="utf-8")
s=s.replace("RRL_STOCK_QC_POLICY.settings(d.get_number('warehouse'),v_mode,v_independent);","RRL_STOCK_QC_POLICY.settings_for_plan(p_domain,v_mode,v_independent);")
anchor="   j.put('unique_mark_control_required'"
before="""   RRL_STOCK_QC_POLICY.settings_for_plan(domain,v_mode,v_independent);
   j.put('required',v_mode!='NONE');j.put('control_mode',v_mode);j.put('independent_controller_required',v_independent=1);
"""
assert anchor in s;s=s.replace(anchor,before+anchor,1)
out[str(f/"005_gate.sql")]=s
out[str(f/"apply.sql")]="@@001_schema.sql\n@@002_api.sql\n@@003_guard.sql\n@@004_policy.sql\n@@005_gate.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_PALLET_TYPE where FINAL_WEIGHT_REQUIRED=1;if n>0 then raise_application_error(-20863,'SMALL_TYPE_POLICY_USED_FORWARD_REPAIR');end if;end;
/
@@000_before_gate.sql
@@000_before_policy.sql
drop trigger RRL_PALLET_TYPE_FINAL_GUARD;
drop context RRL_PALLET_TYPE_CTX;
drop package RRL_PALLET_TYPE_API;
alter table RRL_PALLET_TYPE drop column FINAL_WEIGHT_REQUIRED;
"""
out["wiki/database/retailcase_ni042_small_final_weight_design_20261011.md"]="""# NI04.2: обязательный финальный вес малой коробки
202 additive FINAL_WEIGHT_REQUIRED default0 on existing pallet type. Existing CASE shipment QC policy upgrades NONE/ANY→WEIGHT, SCAN→BOTH only for the specific child type; parent warehouse exemption never grants child weight approval. Existing immutable root QC records/content signature/actual gross and wood values retained; DEFAULT_WEIGHT_KG remains a reference, never claimed as measured tare. New precise Decimal type DTO/current legacy endpoint delegates to inventory native metadata owner (case_pick_manage/configexclusive/trusted type context); omission preserves flag. No stock writer.203/204 addressed final scale archive and proof integration follow;202 alone is not physical scale acceptance.
"""
for p,line in[("wiki/index.md","- [Проект финального веса малой коробки](database/retailcase_ni042_small_final_weight_design_20261011.md):202 per-type mandatory child QC/current metadata owner; final scale archive next."),
("wiki/log.md","2026-10-11:202 small-box final-weight design: currentCASE type mandatory weight independent of parent/warehouse exemption; reference default weight not measuredtare; precise DTO/existing native QC reuse.203/204 addressed measurements next.")]:
 path=Path(p);out[p]=path.read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
