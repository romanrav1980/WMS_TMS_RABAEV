from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_per_sku_mark_matrix");out={}
old=Path("db/migrations/2026-10-12_ni061_marked_consolidation/002_store.sql").read_text(encoding="utf-8")
new=old.replace("profiles clob;first_profiles clob;n number;bad number;","profiles clob;first_profiles clob;n number;bad number;matched number;scan_total number:=0;profile_union json_array_t:=json_array_t();current_profiles json_array_t;profile_item json_object_t;profile_key varchar2(500);")
new=new.replace("seen keys_map;k varchar2(64);","seen keys_map;seen_profiles keys_map;k varchar2(64);")
needle=" if z=0 then first_profiles:=profiles;else if dbms_lob.compare(first_profiles,profiles)!=0 then raise_application_error(-20886,'STORE_MARK_CONSOLIDATED_PROFILE_MATRIX_REQUIRED');end if;end if;"
repl=""" current_profiles:=json_array_t.parse(profiles);
 for pi in 0..current_profiles.get_size-1 loop profile_item:=treat(current_profiles.get(pi)as json_object_t);
 profile_key:=rawtohex(sys.dbms_crypto.hash(profile_item.to_clob,sys.dbms_crypto.hash_sh256));
 if not seen_profiles.exists(profile_key)then seen_profiles(profile_key):=1;profile_union.append(profile_item);end if;end loop;
 if profile_union.get_size>50 then raise_application_error(-20881,'STORE_MARK_PROFILE_UNION_BOUND_50');end if;
 select count(distinct u.PHYSICAL_UNIT_KEY||':'||c.SYSTEM_CODE||':'||pr.PROFILE_CODE)into matched
 from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
 cross apply json_table(c.PROFILES_JSON,'$[*]'columns(PROFILE_CODE varchar2(80)path '$.profile',PROFILE_VERSION varchar2(40)path '$.version'))pr
 join RRL_SKU_RECEIPT_PROFILE profile on profile.ARTICUL=article and profile.SYSTEM_CODE=c.SYSTEM_CODE and profile.PROFILE_CODE=pr.PROFILE_CODE and profile.PROFILE_VERSION=pr.PROFILE_VERSION
 where u.CURRENT_UID=node.get_string('uid')and u.STOCK_STATUS='ISSUED';
 if matched!=n*leafproof.get_number('physical_unit_count')then raise_application_error(-20886,'STORE_MARK_CURRENT_SAVED_CODE_PROFILE_VERSION_REQUIRED');end if;"""
# JSON method excluded from SQL
repl=repl.replace("u.CURRENT_UID=node.get_string('uid')","u.CURRENT_UID=v_lot_uid")
new=new.replace("article varchar2(160);wire clob;","article varchar2(160);wire clob;v_lot_uid varchar2(200);",1)
new=new.replace("node:=treat(leaves.get(z)as json_object_t);article:=node.get_string('article');","node:=treat(leaves.get(z)as json_object_t);article:=node.get_string('article');v_lot_uid:=node.get_string('uid');",1)
assert needle in new;new=new.replace(needle,repl)
new=new.replace("unit_value.put('article',article);allunits.append(unit_value);","unit_value.put('article',article);unit_value.put('profiles',current_profiles);allunits.append(unit_value);")
new=new.replace("if allunits.get_size>10000 or n*allunits.get_size>20000 then","scan_total:=scan_total+n*units.get_size;\n if allunits.get_size>10000 or scan_total>20000 then")
new=new.replace("json_array_t.parse(first_profiles)","profile_union").replace("n*allunits.get_size);","scan_total);")
new=new.replace("declared_lots qty_map;","declared_lots qty_map;unit_profile_counts keys_per_unit;")if False else new
# Define profile-count map by unit separately
new=new.replace("states state_map;","states state_map;type count_map is table of number index by varchar2(64);unit_profile_counts count_map;")
new=new.replace("   for j in 0..profiles.get_size-1 loop","   profiles:=unit_value.get_array('profiles');unit_profile_counts(unit_key):=profiles.get_size;\n   for j in 0..profiles.get_size-1 loop",1)
new=new.replace("coverage(unit_key)!=profile_count","coverage(unit_key)!=unit_profile_counts(unit_key)")
out[(d/"000_before_store.sql").as_posix()]=old;out[(d/"001_store.sql").as_posix()]=new
old=Path("db/migrations/2026-10-12_ni061_marked_consolidation/003_ship.sql").read_text(encoding="utf-8")
new=old.replace("elsif dbms_lob.compare(v_first_profiles,v_profiles)!=0 then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_PROFILE_MATRIX_REQUIRED');","elsif (json_array_t.parse(v_first_profiles).get_size=0 and v_profile_count>0)or(json_array_t.parse(v_first_profiles).get_size>0 and v_profile_count=0)then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_MIXED_MARKED_FLOW_REQUIRED');")
assert new!=old
out[(d/"000_before_ship.sql").as_posix()]=old;out[(d/"002_ship.sql").as_posix()]=new
out[(d/"003_recompile.sql").as_posix()]=Path("db/migrations/2026-10-12_ni061_nested_receiving/009_recompile.sql").read_text(encoding="utf-8")
out[(d/"004_ledger.sql").as_posix()]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-339-per-sku-mark-matrix' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Per-SKU per-unit recipient profile matrix with current saved code version admission and per-lot quantities',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"
out[(d/"apply.sql").as_posix()]="@@001_store.sql\n@@002_ship.sql\n@@003_recompile.sql\n@@004_ledger.sql\n"
out[(d/"rollback.sql").as_posix()]="@@000_before_store.sql\n@@000_before_ship.sql\n@@003_recompile.sql\n"
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STORE_MARK_CORE','RRL_STOCK_HU_SHIP_CMD');\n"
print(json.dumps(out))
