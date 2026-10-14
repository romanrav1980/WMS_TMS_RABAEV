from pathlib import Path
import json
out={};old=Path("db/migrations/2026-10-11_ni061_partial_receiving");base=Path("db/migrations/2026-10-11_ni061_marked_partial")
spec=(old/"000_before_rrl_stock_unit_core_spec.sql").read_text(encoding="utf-8");body=(old/"000_before_rrl_stock_unit_core_body.sql").read_text(encoding="utf-8")
needle=" procedure receive_return("
assert needle in spec;spec=spec.replace(needle," procedure receive_partial_issued(p_old_uid varchar2,p_source_cell varchar2,p_uid varchar2,p_target_cell varchar2,p_qty number,p_units clob);\n"+needle,1)
start=body.index(" procedure receive_return(");end=body.index("\nend;",start)
method=body[start:end].replace("procedure receive_return(","procedure receive_partial_issued(",1)
method=method.replace("$.original_lot_uid","$.original_root_uid").replace("$.return_source_cell","$.source_cell").replace("$.return_unit_proof.units","$.source_units").replace("o.COMMAND_TYPE='STORE_RETURN_RECEIVE'","o.COMMAND_TYPE='INTERWARE_RECEIVE'and json_value(o.RESOLVED_PLAN_JSON,'$.domain.partial_receipt')='true'")
method=method.replace("STORE_RETURN_","INTERWARE_PARTIAL_").replace("original return","partial interware").replace("original returned","partial received")
body=body[:end]+method+body[end:]
out[(base/"001_unit_core.sql").as_posix()]=spec+body
p=old/"002_partial_helper.sql";s=p.read_text(encoding="utf-8")
needle=" procedure create_pallet("
specneedle=" procedure describe_selected_units(p_metadata json_object_t,p_domain in out json_object_t);\n"
s=s.replace(needle,specneedle+needle,1)
# Only source with a configured unit identity profile is admitted.
s=s.replace("if n!=0 or RRL_INTERWARE_MARK_SCAN.required_for_article(p_article)=1 then raise_application_error(-20886,'INTERWARE_PARTIAL_EXACT_SERIALIZED_SELECTION_REQUIRED');end if;","if RRL_INTERWARE_MARK_SCAN.required_for_article(p_article)=1 and n=0 then raise_application_error(-20886,'INTERWARE_PARTIAL_EXACT_SERIALIZED_SELECTION_REQUIRED');end if;\n  if n>0 and RRL_INTERWARE_MARK_SCAN.required_for_article(p_article)=0 then raise_application_error(-20886,'INTERWARE_PARTIAL_SERIALIZED_PROFILE_REQUIRED');end if;")
start=s.index(" procedure create_pallet(",s.index("create or replace package body"))
new="""
 procedure describe_selected_units(p_metadata json_object_t,p_domain in out json_object_t)is
  requested clob;original clob;selected clob;n number;distinct_count number;found number;qty number;total number;
 begin
  if not p_domain.has('source_units')then
   if p_metadata.has('unit_keys')and p_metadata.get_array('unit_keys').get_size>0 then raise_application_error(-20886,'INTERWARE_PARTIAL_UNEXPECTED_UNIT_SELECTION');end if;
   return;
  end if;
  if not p_metadata.has('unit_keys')then raise_application_error(-20886,'INTERWARE_PARTIAL_EXACT_UNIT_SELECTION_REQUIRED');end if;
  requested:=p_metadata.get_array('unit_keys').to_clob;original:=p_domain.get_array('source_units').to_clob;
  select count(*),count(distinct K)into n,distinct_count from json_table(requested,'$[*]'columns(K varchar2(64)path '$'));
  if n<1 or n>10000 or n!=distinct_count then raise_application_error(-20886,'INTERWARE_PARTIAL_UNIQUE_UNIT_SELECTION_REQUIRED');end if;
  select count(*),sum(RRL_STOCK_MATH.quantity(o.Q)),
   json_arrayagg(json_object('key'value o.K,'version'value o.V,'quantity'value o.Q,'base_uom'value o.B)order by o.K returning clob)
   into found,total,selected
   from json_table(original,'$[*]'columns(K varchar2(64)path '$.key',V number path '$.version',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))o
   join json_table(requested,'$[*]'columns(K varchar2(64)path '$'))r on r.K=o.K;
  qty:=RRL_STOCK_MATH.quantity(p_domain.get_string('quantity'));
  if found!=n or total!=qty then raise_application_error(-20886,'INTERWARE_PARTIAL_SELECTED_BASE_QUANTITY_CONFLICT');end if;
  p_domain.put('original_source_units',p_domain.get_array('source_units'));
  p_domain.put('source_units',json_array_t.parse(selected));p_domain.put('selected_unit_keys',p_metadata.get_array('unit_keys'));
 end;
"""
s=s[:start]+new+s[start:]
out[(base/"002_partial_helper.sql").as_posix()]=s
s=(old/"003_receiving_body.sql").read_text(encoding="utf-8")
needle="  v_qty:=RRL_STOCK_MATH.quantity(p_domain.get_string('quantity'));"
assert needle in s;s=s.replace(needle,needle+"\n  RRL_STOCK_INTERWARE_PART.describe_selected_units(m,p_domain);",1)
# Scan the original source binding and only the exact selected set.
needle="   scan_legs:=json_array_t();"
assert needle in s;s=s.replace(needle,"""   if p_domain.has('partial_receipt')then
    scan_leg.put('uid',plan.ROOT_UID);scan_leg.put('selected_unit_keys',p_domain.get_array('selected_unit_keys'));
   end if;
"""+needle,1)
needle="   RRL_STOCK_UNIT_CORE.receive_issued(v_uid,v.get_string('source_cell'),v_cell,v_qty,v.get_array('source_units').to_clob);"
assert needle in s;s=s.replace(needle,"""   if v.has('partial_receipt')then
    RRL_STOCK_UNIT_CORE.receive_partial_issued(v.get_string('original_root_uid'),v.get_string('source_cell'),v_uid,v_cell,v_qty,v.get_array('source_units').to_clob);
   else
"""+needle+"\n   end if;",1)
out[(base/"003_receiving_body.sql").as_posix()]=s
s=(old/"004_put_body.sql").read_text(encoding="utf-8")
needle="  select MANIFEST_JSON into unit_wire from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=receipt.PLAN_OPERATION_ID;"
assert needle in s;s=s.replace(needle,"""  if receipt.ORIGINAL_ROOT_UID is not null then
   select json_query(RESOLVED_PLAN_JSON,'$.domain.source_units' returning clob)into unit_wire from RRL_STOCK_OPERATION where OPERATION_ID=receipt.OPERATION_ID and STATE='APPLIED';
   declare envelope json_object_t:=json_object_t();a json_array_t:=json_array_t.parse(unit_wire);begin
    envelope.put('units',a);envelope.put('physical_unit_count',a.get_size);unit_wire:=envelope.to_clob;
   end;
  else
"""+needle+"\n  end if;",1)
out[(base/"005_put_body.sql").as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
