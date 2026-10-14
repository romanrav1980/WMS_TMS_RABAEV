from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_marked_consolidation");out={}
old=Path("db/migrations/2026-10-12_ni061_ordinary_consolidation/002_shipping.sql").read_text(encoding="utf-8")
new=old.replace("loading_domain json_object_t;","loading_domain json_object_t;v_profiles clob;v_first_profiles clob;v_profile_count number;",1)
start=new.index("      select count(*)into leg_count from dual where")
stop=new.index("     end if;",start)
new=new[:start]+"""      select count(*),json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)into v_profile_count,v_profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=t.ARTICLE_VALUE;
      select count(*)into leg_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=t.UID_VALUE;
      if leg_count>0 and v_profile_count=0 then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_SERIALIZED_PROFILE_REQUIRED');end if;
      if v_profile_count>0 then
       select count(*)into leg_count from RRL_SKU_RECEIPT_PROFILE where ARTICUL=t.ARTICLE_VALUE and SCAN_MODE not in('UNIT','UNIT_OR_AGGREGATION');
       if leg_count>0 then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_UNIT_SCAN_MODE_REQUIRED');end if;
      else v_profiles:=json_array_t().to_clob;end if;
      if v_first_profiles is null then v_first_profiles:=v_profiles;elsif dbms_lob.compare(v_first_profiles,v_profiles)!=0 then raise_application_error(-20886,'INTERWARE_CONSOLIDATED_PROFILE_MATRIX_REQUIRED');end if;
"""+new[stop:]
out[(d/"000_before_ship.sql").as_posix()]=old;out[(d/"003_ship.sql").as_posix()]=new
out[(d/"apply.sql").as_posix()]="@@001_units.sql\n@@002_store.sql\n@@003_ship.sql\n@@004_recompile.sql\n@@005_ledger.sql\n"
out[(d/"004_recompile.sql").as_posix()]=Path("db/migrations/2026-10-12_ni061_nested_receiving/009_recompile.sql").read_text(encoding="utf-8")
out[(d/"005_ledger.sql").as_posix()]="merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-333-marked-consolidation-matrix' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Whole marked STOCK leaves with identical current profile matrix retain per-leaf unit fingerprints and per-lot recipient dispositions',sysdate,user,'apply.sql','rollback.sql','APPLIED');\ncommit;\n"
out[(d/"rollback.sql").as_posix()]="declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='STORE_RECEIPT'and STATE='APPLIED'and json_value(RESOLVED_PLAN_JSON,'$.domain.snapshot.leaf_count'returning number)>1 and json_value(RESOLVED_PLAN_JSON,'$.domain.requires_marked_recipient_flow')='true';if n>0 then raise_application_error(-20899,'MARKED_CONSOLIDATED_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;\n/\n@@000_before_units.sql\n@@000_before_store.sql\n@@000_before_ship.sql\n@@004_recompile.sql\n"
out[(d/"verify.sql").as_posix()]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_INTERWARE_UNIT_SOURCE','RRL_STORE_MARK_CORE','RRL_STOCK_HU_SHIP_CMD');\n"
old=Path("scripts/source311_marked_case.py").read_text(encoding="utf-8")
for num in ["334","335"]:
 src=old.replace("311",num)
 if num=="335":
  start=src.index("  target=ware+50000000;");end=src.index("  now=datetime.now",start)
  src=src[:start]+"""  common=json.loads(Path("tmp/context334.json").read_text(encoding="utf-8"))
  target=common["target_warehouse"];inbound=common["inbound"];outbound=common["outbound"];target_trip=common["target_trip"]
"""+src[end:]
 out["scripts/source"+num+"_marked_case.py"]=src
print(json.dumps(out))
