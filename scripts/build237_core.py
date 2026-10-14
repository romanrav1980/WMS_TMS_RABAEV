from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni062_marked_supplier")
core="""create or replace package RRL_REGULATORY_STOCK_OUTBOX authid definer accessible by(package RRL_REGULATORY_API)as
 procedure declare_events(p_operation varchar2,p_event varchar2,p_profiles clob,p_resources in out nocopy json_array_t);
 function enqueue_events(p_operation varchar2,p_event varchar2,p_domain clob,p_units clob,p_profiles clob)return clob;
end;
/
create or replace package body RRL_REGULATORY_STOCK_OUTBOX as
 function event_key(p_operation varchar2,p_event varchar2,p_system varchar2)return varchar2 is
 begin
  if p_event not in('MARKED_GOODS_DISPOSED','MARKED_SUPPLIER_RETURN_DISPATCHED')then raise_application_error(-20871,'REGULATORY_STOCK_EVENT_KIND_REQUIRED');end if;
  return case p_event when 'MARKED_GOODS_DISPOSED'then 'RETURN.DISPOSAL.GOV:'else 'RETURN.SUPPLIER.GOV:'end||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation||chr(0)||p_system,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
 end;
 procedure declare_events(p_operation varchar2,p_event varchar2,p_profiles clob,p_resources in out nocopy json_array_t)is k varchar2(100);
 begin
  for x in(select distinct S from json_table(p_profiles,'$[*]'columns(S varchar2(40)path '$.system_code'))order by S)loop
   if x.S is null or lengthb(x.S)>30 then raise_application_error(-20871,'REGULATORY_TARGET_SYSTEM_BOUND');end if;
   k:=event_key(p_operation,p_event,x.S);RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE',k);
  end loop;
 end;
 function enqueue_events(p_operation varchar2,p_event varchar2,p_domain clob,p_units clob,p_profiles clob)return clob is
  frozen clob;kind_text varchar2(80);domain json_object_t;source json_object_t;gov json_object_t;code_wire clob;gov_id number;k varchar2(100);ids json_array_t:=json_array_t();units_count number;n number;
 begin
  if p_operation!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'REGULATORY_STOCK_FACT_ROOT_CONTEXT_REQUIRED');end if;
  select COMMAND_TYPE,RESOLVED_PLAN_JSON into kind_text,frozen from RRL_STOCK_OPERATION where OPERATION_ID=p_operation and STATE='IN_FLIGHT';
  domain:=json_object_t.parse(frozen).get_object('domain');
  if p_event='MARKED_GOODS_DISPOSED'and kind_text='STORE_RETURN_DISPOSE'then source:=domain;
   if dbms_lob.compare(source.get_array('disposal_units').to_clob,p_units)!=0 or dbms_lob.compare(source.get_array('disposal_profiles').to_clob,p_profiles)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: disposal regulatory source');end if;
  elsif p_event='MARKED_SUPPLIER_RETURN_DISPATCHED'and kind_text='LOAD_SHIPMENT'then source:=domain.get_object('supplier_return_source');
   if dbms_lob.compare(source.get_array('units').to_clob,p_units)!=0 or dbms_lob.compare(source.get_array('profiles').to_clob,p_profiles)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: supplier regulatory source');end if;
  else raise_application_error(-20863,'REGULATORY_STOCK_FACT_MATCHING_COMMAND_REQUIRED');end if;
  if dbms_lob.compare(source.to_clob,p_domain)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: regulatory frozen domain');end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',source.get_string('uid')));
  select count(*),count(distinct K)into units_count,n from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key'));
  if units_count<1 or units_count>10000 or units_count!=n then raise_application_error(-20881,'REGULATORY_STOCK_UNIT_BOUND');end if;
  for x in(select K from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key'))order by K)loop RRL_STOCK_LOCK_API.assert_held(60,RRL_STOCK_LOCK_API.resource_key('UNIT',x.K));end loop;
  for target in(select distinct S from json_table(p_profiles,'$[*]'columns(S varchar2(30)path '$.system_code'))order by S)loop
   select json_arrayagg(json_object('physical_unit_key'value u.PHYSICAL_UNIT_KEY,'origin_uid'value u.UID_PALLET,'unit_id'value u.UNIT_ID,'code_hash'value c.CODE_HASH,'canonical_code'value c.CANONICAL_CODE,'profiles'value c.PROFILES_JSON format json)order by u.PHYSICAL_UNIT_KEY,c.CODE_HASH returning clob)into code_wire
    from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
    where c.SYSTEM_CODE=target.S and u.PHYSICAL_UNIT_KEY in(select K from json_table(p_units,'$[*]'columns(K varchar2(64)path '$.key')));
   if code_wire is null then raise_application_error(-20886,'REGULATORY_STOCK_CANONICAL_CODES_REQUIRED');end if;
   gov:=json_object_t.parse(p_domain);gov.put('contract_version',1);gov.put('operation_id',p_operation);gov.put('operation_type',case p_event when 'MARKED_GOODS_DISPOSED'then 'DISPOSAL'else 'SUPPLIER_RETURN_DISPATCH'end);gov.put('system_code',target.S);gov.put('codes',json_array_t.parse(code_wire));gov.put('physical_disposal_recorded',p_event='MARKED_GOODS_DISPOSED');gov.put('external_ack_verified',false);
   k:=event_key(p_operation,p_event,target.S);RRL_STOCK_LOCK_API.assert_held(70,RRL_STOCK_LOCK_API.resource_key('UNIQUE',k));
   gov_id:=RRL_TRACEABILITY_API.enqueue_event(p_event,'STOCK_OPERATION',p_operation,k,gov.to_clob,target.S,p_operation);ids.append(gov_id);
  end loop;
  return ids.to_clob;
 end;
end;
/
"""
out[str(f/"001_regulatory_core.sql")]=core
s=(f/"000_before_rrl_regulatory_api.sql").read_text(encoding="utf-8");decl="""  procedure declare_stock_events(p_operation varchar2,p_event varchar2,p_profiles clob,p_resources in out nocopy json_array_t);
  function enqueue_stock_events(p_operation varchar2,p_event varchar2,p_domain clob,p_units clob,p_profiles clob)return clob;
"""
s=s.replace("end RRL_REGULATORY_API;",decl+"end RRL_REGULATORY_API;",1)
idx=s.rindex("end RRL_REGULATORY_API;");body="""  procedure declare_stock_events(p_operation varchar2,p_event varchar2,p_profiles clob,p_resources in out nocopy json_array_t)is
  begin RRL_REGULATORY_STOCK_OUTBOX.declare_events(p_operation,p_event,p_profiles,p_resources);end;
  function enqueue_stock_events(p_operation varchar2,p_event varchar2,p_domain clob,p_units clob,p_profiles clob)return clob is
  begin return RRL_REGULATORY_STOCK_OUTBOX.enqueue_events(p_operation,p_event,p_domain,p_units,p_profiles);end;
"""
s=s[:idx]+body+s[idx:];out[str(f/"002_regulatory_api.sql")]=s
s=(f/"000_before_rrl_stock_return_dispose.sql").read_text(encoding="utf-8")
a=s.index(" if v.has('disposal_profiles')then",s.index(" procedure compile_command",s.index("package body")));b=s.index(" RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'",a)
s=s[:a]+" if v.has('disposal_profiles')then RRL_REGULATORY_API.declare_stock_events(p_operation,'MARKED_GOODS_DISPOSED',v.get_array('disposal_profiles').to_clob,r);end if;\n"+s[b:]
a=s.index(" if v.has('disposal_profiles')then",s.index(" procedure execute_command",s.index("package body")));b=s.index(" payload:=json_object_t.parse(v.to_clob);",a)
s=s[:a]+""" if v.has('disposal_profiles')then
  gov_ids:=json_array_t.parse(RRL_REGULATORY_API.enqueue_stock_events(op,'MARKED_GOODS_DISPOSED',v.to_clob,v.get_array('disposal_units').to_clob,v.get_array('disposal_profiles').to_clob));
  j.put('physical_unit_count',v.get_array('disposal_units').get_size);j.put('regulatory_event_ids',gov_ids);j.put('regulatory_status','PENDING');j.put('external_regulatory_ack',false);
 end if;
"""+s[b:]
out[str(f/"003_disposal_delegate.sql")]=s
s=(f/"000_before_rrl_stock_sup_return.sql").read_text(encoding="utf-8")
s=s.replace("v_policy number;n number;","v_policy number;n number;actual number;total number;units clob;profiles clob;",1)
s=s.replace(" if n!=0 then raise_application_error(-20886,'SUP_RETURN_MARKED_UNIT_REGULATORY_FLOW_REQUIRED');end if;", """ if n!=0 then
  select count(*),sum(case when SCAN_MODE='UNIT'and lengthb(SYSTEM_CODE)<=30 then 0 else 1 end),json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
   into n,actual,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=receipt.ARTICLE;
  if n<1 or n>50 or actual!=0 then raise_application_error(-20886,'SUP_RETURN_CURRENT_UNIT_PROFILES_REQUIRED');end if;
  select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION,'origin_uid'value u.UID_PALLET,'unit_id'value u.UNIT_ID)order by u.PHYSICAL_UNIT_KEY returning clob)
   into n,total,units from RRL_STORE_RETURN_UNIT b join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=b.PHYSICAL_UNIT_KEY
   where b.APPROVAL_OPERATION_ID=receipt.APPROVAL_OPERATION_ID and u.CURRENT_UID=receipt.UID_PALLET and u.CURRENT_CELL=v_cell and u.BASE_QTY=b.BASE_QTY and u.BASE_UOM=b.BASE_UOM and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null;
  select count(*)into actual from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=receipt.UID_PALLET and CURRENT_CELL=v_cell;
  if n<1 or n>10000 or actual!=n or total!=receipt.BASE_QTY then raise_application_error(-20886,'SUP_RETURN_EXACT_APPROVED_ORIGINAL_UNITS_REQUIRED');end if;
  j.put('units',json_array_t.parse(units));j.put('profiles',json_array_t.parse(profiles));
 end if;""",1)
s=s.replace(" RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_SUP_BIND'", " if p_source.has('profiles')then RRL_REGULATORY_API.declare_stock_events(p_operation,'MARKED_SUPPLIER_RETURN_DISPATCHED',p_source.get_array('profiles').to_clob,p_resources);end if;\n RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_SUP_BIND'",1)
s=s.replace("v_event varchar2(100);\n begin","v_event varchar2(100);gov_ids clob;\n begin",1)
s=s.replace(" v_body:=payload.to_clob;"," if p_source.has('profiles')then gov_ids:=RRL_REGULATORY_API.enqueue_stock_events(op,'MARKED_SUPPLIER_RETURN_DISPATCHED',p_source.to_clob,p_source.get_array('units').to_clob,p_source.get_array('profiles').to_clob);payload.put('regulatory_event_ids',json_array_t.parse(gov_ids));payload.put('regulatory_status','PENDING');payload.put('external_regulatory_ack',false);end if;\n v_body:=payload.to_clob;",1)
out[str(f/"004_supplier.sql")]=s
out[str(f/"005_recompile.sql")]="".join("alter package "+p+" compile body;\n/\n"for p in["RRL_STOCK_SHIPPING_CORE","RRL_STOCK_EFFECT_CORE","RRL_STOCK_POSTING_API"])
out[str(f/"rollback.sql")]="@@000_before_rrl_stock_sup_return.sql\n@@000_before_rrl_stock_return_dispose.sql\n@@000_before_rrl_regulatory_api.sql\n@@005_recompile.sql\ndrop package RRL_REGULATORY_STOCK_OUTBOX;\n"
out["wiki/database/retailcase_ni062_marked_supplier_design_20261011.md"]="# NI06.2: маркированный возврат поставщику прежней СТ\n237 preserves original supplier ST preparer/QC/loading/shipping/effect/departure/handover. Exact approved current AVAILABLE keys/profile snapshot retained in original source helper. Shared canonical stock notifications extracted to private RRL_REGULATORY_STOCK_OUTBOX behind existing RRL_REGULATORY_API, preserving disposal event keys/history. Source domain/units/profiles/root kind/current TX/resource ownership verified before enqueue; no governmental status completion or new quantity writer. Both supplier dispatch and disposal actual messages remain pending until configured provider evidence.\n"
print(json.dumps(out,ensure_ascii=True))
