from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_mixed_consolidation");out={}
old=Path("db/migrations/2026-10-12_ni061_per_sku_mark_matrix/001_store.sql").read_text(encoding="utf-8")
new=old.replace("profile_union json_array_t:=json_array_t();","profile_union json_array_t:=json_array_t();ordinary_lots json_array_t:=json_array_t();",1)
start=new.index(" if n<1 or n>50");end=new.index(" signature_entry:=",start)
body=new[start:end]
body=body.replace("n<1 or n>50","n>50",1)
new=new[:start]+""" units:=leafproof.get_array('units');
 if n=0 and units.get_size=0 then ordinary_lots.append(node.get_string('uid'));
 else
 if n=0 or units.get_size=0 then raise_application_error(-20886,'STORE_MARK_UNIT_PROFILE_MATRIX_REQUIRED');end if;
"""+body+" end if;\n"+new[end:]
new=new.replace("proof.put('units',allunits);","proof.put('ordinary_lots',ordinary_lots);proof.put('units',allunits);",1)
new=new.replace("unit_profile_counts count_map;","unit_profile_counts count_map;ordinary_keys qty_map;")if False else new
# qty_map declared before body
new=new.replace("damaged_lots qty_map;declared_lots qty_map;","damaged_lots qty_map;declared_lots qty_map;ordinary_keys qty_map;ordinary_array json_array_t;")
new=new.replace(" begin \n  if p_metadata.has('unit_scans')", """ begin
  if p_proof.has('ordinary_lots')then ordinary_array:=p_proof.get_array('ordinary_lots');for i in 0..ordinary_array.get_size-1 loop ordinary_keys(ordinary_array.get_string(i)):=1;end loop;end if;
  if p_metadata.has('unit_scans')""",1)
oldline="   if line_lot is null or not accepted_lots.exists(line_lot)or declared_lots.exists(line_lot)then raise_application_error(-20886,'STORE_MARK_EXACT_LOT_LINES_REQUIRED');end if;declared_lots(line_lot):=1;"
new=new.replace(oldline,"""   if line_lot is null or declared_lots.exists(line_lot)or(not accepted_lots.exists(line_lot)and not ordinary_keys.exists(line_lot))then raise_application_error(-20886,'STORE_MARK_EXACT_LOT_LINES_REQUIRED');end if;declared_lots(line_lot):=1;
   if accepted_lots.exists(line_lot)then""",1)
needle="then raise_application_error(-20886,'STORE_MARK_EXACT_UNIT_DISPOSITION_QUANTITY_REQUIRED');end if;\n  end loop;"
new=new.replace(needle,"then raise_application_error(-20886,'STORE_MARK_EXACT_UNIT_DISPOSITION_QUANTITY_REQUIRED');end if;\n   end if;\n  end loop;",1)
new=new.replace("declared_lots.count!=accepted_lots.count","declared_lots.count!=accepted_lots.count+ordinary_keys.count",1)
assert new!=old
out[(d/"000_before_store.sql").as_posix()]=old;out[(d/"001_store.sql").as_posix()]=new
old=Path("db/migrations/2026-10-12_ni061_per_sku_mark_matrix/002_ship.sql").read_text(encoding="utf-8")
needle="      if v_first_profiles is null then v_first_profiles:=v_profiles;elsif (json_array_t.parse(v_first_profiles).get_size=0 and v_profile_count>0)or(json_array_t.parse(v_first_profiles).get_size>0 and v_profile_count=0)then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_MIXED_MARKED_FLOW_REQUIRED');end if;"
assert needle in old;new=old.replace(needle,"")
out[(d/"000_before_ship.sql").as_posix()]=old;out[(d/"002_ship.sql").as_posix()]=new
out[(d/"003_recompile.sql").as_posix()]=Path("db/migrations/2026-10-12_ni061_nested_receiving/009_recompile.sql").read_text(encoding="utf-8")
out[(d/"004_ledger.sql").as_posix()]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-345-mixed-marked-ordinary-HU' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Shared physical top keeps ordinary frozen quantity lines and exact marked per-SKU unit matrix without fabricated codes',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"
out[(d/"apply.sql").as_posix()]="@@001_store.sql\n@@002_ship.sql\n@@003_recompile.sql\n@@004_ledger.sql\n"
out[(d/"rollback.sql").as_posix()]="@@000_before_store.sql\n@@000_before_ship.sql\n@@003_recompile.sql\n"
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STORE_MARK_CORE','RRL_STOCK_HU_SHIP_CMD');\n"
print(json.dumps(out))
