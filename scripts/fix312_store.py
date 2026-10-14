from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_nested_onward");out={}
s=(d/"000_before_unit_source.sql").read_text(encoding="utf-8")
a=s.index(" function issued_manifest");b=s.index(" procedure capture_plan",a);part=s[a:b]
part=part.replace("required_count number;proof_count number;","required_count number;proof_count number;nodes json_array_t;candidate json_object_t;stock_nodes number:=0;archive_wire clob;archive_tree json_object_t;root_id varchar2(200);",1)
old="  if tree.get_array('nodes').get_size!=1 or tree.get_number('leaf_count')!=1 or tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'INTERWARE_SINGLE_PHYSICAL_ROOT_REQUIRED');end if; \n  node:=treat(tree.get_array('nodes').get(0)as json_object_t);"
assert old in part
replacement="""  nodes:=tree.get_array('nodes');
  if nodes.get_size<1 or nodes.get_size>200 or tree.get_number('leaf_count')!=1 or tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'INTERWARE_SINGLE_PHYSICAL_ROOT_REQUIRED');end if;
  if nodes.get_size=1 then node:=treat(nodes.get(0)as json_object_t);
  else
   select lf.COMPOSITION_JSON,lf.ROOT_UID into archive_wire,root_id from RRL_TT_HU_LOAD_FACT lf
   join RRL_STOCK_OPERATION root_op on root_op.OPERATION_ID=lf.LOAD_OPERATION_ID and root_op.STATE='APPLIED'and root_op.COMMAND_TYPE='HU_SHIP'
   where lf.LOAD_OPERATION_ID=p_load and lf.STATUS in('LOADED','DEPARTED');
   archive_tree:=json_object_t.parse(archive_wire);
   if dbms_lob.compare(archive_tree.to_clob,tree.to_clob)!=0 or root_id!=tree.get_string('root')then raise_application_error(-20884,'INTERWARE_NESTED_FROZEN_LOAD_ARCHIVE_REQUIRED');end if;
   for i in 0..nodes.get_size-1 loop
    candidate:=treat(nodes.get(i)as json_object_t);
    if candidate.get_string('kind')='STOCK'then node:=candidate;stock_nodes:=stock_nodes+1;
    elsif candidate.get_string('kind')!='CONTAINER'then raise_application_error(-20886,'INTERWARE_NESTED_STOCK_ONLY_REQUIRED');end if;
   end loop;
   if stock_nodes!=1 then raise_application_error(-20886,'INTERWARE_NESTED_ONE_STOCK_LEAF_REQUIRED');end if;
  end if;
"""
part=part.replace(old,replacement,1);out[(d/"008_unit_source.sql").as_posix()]=s[:a]+part+s[b:]
s=(d/"000_before_store_mark.sql").read_text(encoding="utf-8")
header=""" function stock_leaf(p_tree json_object_t)return json_object_t is
 nodes json_array_t:=p_tree.get_array('nodes');node json_object_t;candidate json_object_t;n number:=0;
 begin
 if nodes.get_size<1 or nodes.get_size>200 or p_tree.get_number('leaf_count')!=1 or p_tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'STORE_MARK_SINGLE_STOCK_SCOPE_REQUIRED');end if;
 for i in 0..nodes.get_size-1 loop
 candidate:=treat(nodes.get(i)as json_object_t);
 if candidate.get_string('kind')='STOCK'then node:=candidate;n:=n+1;
 elsif candidate.get_string('kind')!='CONTAINER'then raise_application_error(-20886,'STORE_MARK_NESTED_STOCK_ONLY_REQUIRED');end if;
 end loop;
 if n!=1 then raise_application_error(-20886,'STORE_MARK_SINGLE_STOCK_SCOPE_REQUIRED');end if;
 return node;
 end;
"""
s=s.replace(" function source_proof(",header+" function source_proof(",1)
old="  if tree.get_array('nodes').get_size!=1 or tree.get_number('leaf_count')!=1 or tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'STORE_MARK_SINGLE_STOCK_SCOPE_REQUIRED');end if; \n  node:=treat(tree.get_array('nodes').get(0)as json_object_t);"
assert old in s;s=s.replace(old,"  node:=stock_leaf(tree);",1)
s=s.replace("sum(case when SCAN_MODE='UNIT'then 0 else 1 end)","sum(case when SCAN_MODE in('UNIT','UNIT_OR_AGGREGATION')then 0 else 1 end)",1)
s=s.replace("node:=treat(p_domain.get_object('snapshot').get_array('nodes').get(0)as json_object_t);","node:=stock_leaf(p_domain.get_object('snapshot'));",1)
out[(d/"009_store_mark.sql").as_posix()]=s
p=d/"apply.sql";out[p.as_posix()]=p.read_text(encoding="utf-8").replace("@@006_ledger.sql","@@008_unit_source.sql\n@@009_store_mark.sql\n@@006_ledger.sql")
p=d/"rollback.sql";out[p.as_posix()]=p.read_text(encoding="utf-8")+"@@000_before_unit_source.sql\n@@000_before_store_mark.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["additional_scripts"]+=["../2026-10-12_ni061_nested_onward/008_unit_source.sql","../2026-10-12_ni061_nested_onward/009_store_mark.sql"];out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out))
