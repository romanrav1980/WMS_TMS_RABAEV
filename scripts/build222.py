raise SystemExit("Retired authoring generator: use final222 SQL/fresh captured owner, never overwrite checkpoint")
from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni052_unload_all_slots");out={}
out["wiki/database/nicora_ni052_unload_all_slots_design_20261011.md"]="""# NI05.2: текущие места хранения для всех выгружаемых корней
222 same native unloader requires scanned physical slot for CASE, CONTAINER or STOCK when current latest PUBLISHED topology has storage slots. Historical topology never determines current admission. Limited legacy cell (weight/height) also requires a configured measured physical slot; otherwise explicit refusal instead of unmeasured restoration. Selected slot must belong to latest published topology/current warehouse/cell. Existing target_json/placement_core checks under CONFIG/CELL/SLOT locks after quantity/tree restoration; late refusal rolls back whole goods/reserve/units/FF/history/claim. Original measurements reused, current restored epoch captured; same HARD coverage projected to actual slot. No new placement/capacity or quantity engine.
"""
s=(f/"000_before_rrl_stock_unload_cmd.sql").read_text(encoding="utf-8")
start=s.index("  if kind_name='HU_SHIP'then\n   select count(*)into n from RRL_TOPOLOGY_CELL_SLOT");end=s.index("   a:=tree.get_array('nodes');",start)
old=s[start:end]
new="""  select count(*)into n from RRL_TOPOLOGY_CELL_SLOT sl join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=sl.TOPOLOGY_CELL_ID
   where tc.LEGACY_CELL_CODE=cell_text and tc.WARE_ID=p_lf.WARE_ID and tc.ACTIVE=1 and sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT'
    and tc.TOPOLOGY_ID=(select max(TOPOLOGY_ID)from RRL_WAREHOUSE_TOPOLOGY where WARE_ID=p_lf.WARE_ID and STATUS='PUBLISHED');
  if n=0 then select count(*)into n from RRL_CELLS where CELL=cell_text and(nvl(LIMIT_WEIGHT,0)>0 or nvl(LIMIT_HEIGHT,0)>0);end if;
  if n>0 and p_metadata.get_number('target_slot_id')is null then raise_application_error(-20886,'UNLOAD_STORAGE_SLOT_PLACEMENT_REQUIRED');end if;
  if kind_name='HU_SHIP'then
"""
s=s[:start]+new+s[end:]
anchor="where sl.CELL_SLOT_ID=target_slot and sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT'and tc.ACTIVE=1 and tc.LEGACY_CELL_CODE=cell_text and tc.WARE_ID=lf.WARE_ID;"
assert anchor in s;s=s.replace(anchor,"where sl.CELL_SLOT_ID=target_slot and sl.ACTIVE=1 and sl.SLOT_KIND='STORAGE_SLOT'and tc.ACTIVE=1 and tc.LEGACY_CELL_CODE=cell_text and tc.WARE_ID=lf.WARE_ID and tc.TOPOLOGY_ID=(select max(TOPOLOGY_ID)from RRL_WAREHOUSE_TOPOLOGY where WARE_ID=lf.WARE_ID and STATUS='PUBLISHED');",1)
out[str(f/"001_unload.sql")]=s
out[str(f/"002_recompile.sql")]="alter package RRL_STOCK_POSTING_API compile body;\n"
out[str(f/"apply.sql")]="@@001_unload.sql\n@@002_recompile.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin
 select count(*)into n from RRL_TT_UNLOAD_FACT u join RRL_STOCK_OPERATION o on o.OPERATION_ID=u.OPERATION_ID where u.ROOT_UID is not null and json_value(o.RESOLVED_PLAN_JSON,'$.domain.placement_slot')is not null and json_exists(o.RESOLVED_PLAN_JSON,'$.domain.members[*]?(@.physical_uid != null)');
 if n>0 then raise_application_error(-20863,'FULLPAL_SLOT_UNLOAD_HISTORY_FORWARD_REPAIR_REQUIRED');end if;
end;
/
@@000_before_rrl_stock_unload_cmd.sql
@@002_recompile.sql
"""
out[str(f/"verify.sql")]="select name,type,line,position,text from user_errors where name not like 'BIN$%';\nselect object_name,object_type from user_objects where status='INVALID';\n"
print(json.dumps(out,ensure_ascii=True))
