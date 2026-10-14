from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_marked_consolidation");out={}
old=Path("db/migrations/2026-10-12_ni061_nested_onward/009_store_mark.sql").read_text(encoding="utf-8")
start=old.index(" function source_proof(");end=old.index(" function preview(",start)
new=old[:start]+""" function stock_leaves(p_tree json_object_t)return json_array_t is
 nodes json_array_t:=p_tree.get_array('nodes');result json_array_t:=json_array_t();candidate json_object_t;
 begin
 if nodes.get_size<1 or nodes.get_size>200 or p_tree.get_number('leaf_count')<1 or p_tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'STORE_MARK_FROZEN_STOCK_SCOPE_REQUIRED');end if;
 for i in 0..nodes.get_size-1 loop candidate:=treat(nodes.get(i)as json_object_t);
 if candidate.get_string('kind')='STOCK'then result.append(candidate);
 elsif candidate.get_string('kind')!='CONTAINER'then raise_application_error(-20886,'STORE_MARK_NESTED_STOCK_ONLY_REQUIRED');end if;end loop;
 if result.get_size!=p_tree.get_number('leaf_count')then raise_application_error(-20886,'STORE_MARK_EXACT_STOCK_LEAVES_REQUIRED');end if;return result;
 end;
 function source_proof(p_domain json_object_t)return json_object_t is
 tree json_object_t:=p_domain.get_object('snapshot');leaves json_array_t;node json_object_t;proof json_object_t:=json_object_t();leafproof json_object_t;
 allunits json_array_t:=json_array_t();signatures json_array_t:=json_array_t();units json_array_t;unit_value json_object_t;signature_entry json_object_t;
 profiles clob;first_profiles clob;n number;bad number;article varchar2(160);wire clob;
 type keys_map is table of number index by varchar2(64);seen keys_map;k varchar2(64);
 begin
 leaves:=stock_leaves(tree);
 for z in 0..leaves.get_size-1 loop
 node:=treat(leaves.get(z)as json_object_t);article:=node.get_string('article');
 wire:=RRL_INTERWARE_UNIT_SOURCE.issued_manifest(p_domain.get_string('load_operation_id'),node.get_string('uid'),tree.to_clob);leafproof:=json_object_t.parse(wire);
 select count(*),sum(case when SCAN_MODE in('UNIT','UNIT_OR_AGGREGATION')then 0 else 1 end),
 json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
 into n,bad,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=article;
 if n<1 or n>50 or bad!=0 or leafproof.get_number('physical_unit_count')<1 then raise_application_error(-20886,'STORE_MARK_CURRENT_UNIT_PROFILES_REQUIRED');end if;
 if z=0 then first_profiles:=profiles;else if dbms_lob.compare(first_profiles,profiles)!=0 then raise_application_error(-20886,'STORE_MARK_CONSOLIDATED_PROFILE_MATRIX_REQUIRED');end if;end if;
 units:=leafproof.get_array('units');
 for i in 0..units.get_size-1 loop unit_value:=treat(units.get(i)as json_object_t);k:=unit_value.get_string('key');
 if seen.exists(k)then raise_application_error(-20886,'STORE_MARK_DUPLICATE_PHYSICAL_UNIT');end if;seen(k):=1;
 unit_value.put('lot_uid',node.get_string('uid'));unit_value.put('article',article);allunits.append(unit_value);end loop;
 signature_entry:=json_object_t();signature_entry.put('uid',node.get_string('uid'));signature_entry.put('signature',leafproof.get_string('unit_signature'));signatures.append(signature_entry);
 if allunits.get_size>10000 or n*allunits.get_size>20000 then raise_application_error(-20881,'STORE_MARK_SCAN_BOUND');end if;
 end loop;
 if allunits.get_size!=tree.get_number('physical_unit_count')then raise_application_error(-20884,'STORE_MARK_EXACT_TREE_PHYSICAL_UNIT_COUNT');end if;
 proof.put('units',allunits);proof.put('profiles',json_array_t.parse(first_profiles));proof.put('supported',true);proof.put('physical_unit_count',allunits.get_size);proof.put('expected_scan_count',n*allunits.get_size);
 if leaves.get_size=1 then proof.put('unit_signature',leafproof.get_string('unit_signature'));else proof.put('unit_signature',rawtohex(sys.dbms_crypto.hash(signatures.to_clob,sys.dbms_crypto.hash_sh256)));end if;
 return proof;
 end;
"""+old[end:]
new=new.replace("profile_count number:=profiles.get_size;","profile_count number:=profiles.get_size;lot_key varchar2(200);line_lot varchar2(200);\n type qty_map is table of number index by varchar2(200);accepted_lots qty_map;missing_lots qty_map;refused_lots qty_map;damaged_lots qty_map;declared_lots qty_map;")
new=new.replace("p_lines.get_size!=1","p_lines.get_size<1 or p_lines.get_size>200")
new=new.replace("coverage(unit_key):=0;states(unit_key):='MISSING';","coverage(unit_key):=0;states(unit_key):='MISSING';lot_key:=unit_value.get_string('lot_uid');if lot_key is null then raise_application_error(-20886,'STORE_MARK_UNIT_LOT_REQUIRED');end if;\n   if not accepted_lots.exists(lot_key)then accepted_lots(lot_key):=0;missing_lots(lot_key):=0;refused_lots(lot_key):=0;damaged_lots(lot_key):=0;end if;")
needle="   if disposition='ACCEPTED'then accepted:=accepted+qty;elsif disposition='MISSING'then missing:=missing+qty;elsif disposition='REFUSED'then refused:=refused+qty;else damaged:=damaged+qty;end if;"
replacement="""   lot_key:=unit_value.get_string('lot_uid');
   if disposition='ACCEPTED'then accepted_lots(lot_key):=accepted_lots(lot_key)+qty;elsif disposition='MISSING'then missing_lots(lot_key):=missing_lots(lot_key)+qty;elsif disposition='REFUSED'then refused_lots(lot_key):=refused_lots(lot_key)+qty;else damaged_lots(lot_key):=damaged_lots(lot_key)+qty;end if;"""
assert needle in new;new=new.replace(needle,replacement)
start=new.index("  line_value:=treat(p_lines.get(0)");end=new.index(" end; \n procedure persist",start)
new=new[:start]+"""  for i in 0..p_lines.get_size-1 loop
   line_value:=treat(p_lines.get(i)as json_object_t);line_lot:=line_value.get_string('lot_uid');
   if line_lot is null or not accepted_lots.exists(line_lot)or declared_lots.exists(line_lot)then raise_application_error(-20886,'STORE_MARK_EXACT_LOT_LINES_REQUIRED');end if;declared_lots(line_lot):=1;
   if nonnegative(line_value.get_string('accepted'))!=accepted_lots(line_lot)or nonnegative(line_value.get_string('missing'))!=missing_lots(line_lot)or nonnegative(line_value.get_string('refused'))!=refused_lots(line_lot)or nonnegative(line_value.get_string('damaged'))!=damaged_lots(line_lot)or nonnegative(line_value.get_string('extra'))!=0 then raise_application_error(-20886,'STORE_MARK_EXACT_UNIT_DISPOSITION_QUANTITY_REQUIRED');end if;
  end loop;
  if declared_lots.count!=accepted_lots.count then raise_application_error(-20886,'STORE_MARK_ALL_LOT_LINES_REQUIRED');end if;
"""+new[end:]
start=new.index(" procedure declare_rows(")
new=new[:start]+""" procedure declare_rows(p_domain json_object_t,p_policies in out nocopy json_array_t,p_resources in out nocopy json_array_t)is node json_object_t;leaves json_array_t:=stock_leaves(p_domain.get_object('snapshot'));
 begin
 for i in 0..leaves.get_size-1 loop node:=treat(leaves.get(i)as json_object_t);
 RRL_STOCK_PLAN_HELPER.stock_closure(p_policies,p_resources,node.get_string('uid'),node.get_string('article'),p_domain.get_object('snapshot').get_string('cell'),null);
 end loop;
 end;
end;
/
"""
out[(d/"000_before_store.sql").as_posix()]=old;out[(d/"002_store.sql").as_posix()]=new
print(json.dumps(out))
