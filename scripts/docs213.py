from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni052_unload_units")
out[str(f/"004_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-213-unload-original-units'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Native unload restores exact original issued physical units and owner HARD',sysdate,user,'db/migrations/2026-10-11_ni052_unload_units/apply.sql','db/migrations/2026-10-11_ni052_unload_units/rollback.sql','APPLIED',
'Actual QPB213DF2C8044/7 original units/14 CRPT+EGAIS codes restored/P7H7/original-7/new+7/late rollback/concurrent one winner/replay/currentWARE403/native cleanup0/protected13520/20. Original composition fingerprint and UNIT60 locks; immutable identities/codes; no government ACK.');
commit;
"""
out[str(f/"apply.sql")]="@@001_unit.sql\n@@002_unload.sql\n@@003_recompile.sql\n@@004_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name,sql in [("RRL_STOCK_UNIT_CORE","001_unit.sql"),("RRL_STOCK_UNLOAD_CMD","002_unload.sql")]:
 matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+name+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)];assert matches
 m["components"]=[("../2026-10-11_ni052_unload_units/"+sql)if x==matches[-1]else x for x in m["components"]if x not in matches[:-1]]
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("scripts/ni052_marked_case_unload_case.py");out[str(p)]=p.read_text(encoding="utf-8").replace("standaloneCASE6","standaloneCASE7").replace("P6H6","P7H7").replace("journal-6","journal-7").replace("journal+6","journal+7")
out["wiki/database/retailcase_ni052_unload_units_20261011.md"]="""# NI05.2: выгрузка тех же маркированных единиц
213 APPLIED RABAEV/orcl. [[retailcase_ni052_unload_units_design_20261011]]; [[retailcase_ni052_unload_20261011]].
Same UNLOAD_SHIPMENT/private owner extends212; existing RRL_STOCK_UNIT_CORE.restore_issued restores retained identity with original owner HARD. No DDL/new registry/second quantity writer. Reconstruct issued key/quantity/base-UOM canonical hash at exact original UID/cell and compare original LOAD physical_before.unit_signature; whole sum original journal quantity. Current unit versions frozen and all UNIT60 locks declared. Under sorted closure recheck exact fingerprint/version/state/null HARD then restore AVAILABLE/new original-owner reserve and increment unit versions. Original CRPT/EGAIS code links never rewritten or recreated. Missing/changed/moved unit or changed current marking requirement without original capture refuses.

Actual QPB213DF2C8044/load SMALL213.LOAD:df2c8044: original7 physical/14 two-profile codes restored to same CASE, P7H7/one original-owner HARD. Original -7 unchanged/new +7; late rollback, distinct concurrent200/409, exact replay, current nonadmin foreignWARE403, native return/release/count0 and protected13520/20 passed. Source5/codes10 and restored7/codes14 cleaned natively; history retained. Prior once-only QR/full weight gates reused, new quality cycle required. TEST scale/synthetic codes do not prove physical device/government legal reversal.

Initial native unit row lock over JSON_TABLE join compiled ORA01786, corrected to ordered per-key real row FOR UPDATE after UNIT60 ownership; not skipped. Eighteen invalidated owner dependencies explicitly recompiled/final INVALID0. Query28r5r1q5ycjmy1.236ms/5 and exact restorea06tcbtjwzsvv6.734ms/2: retain CURRENT_UID index/10000 unit bound, no global scan. Owner inventory must batch only if production-size workload exceeds threshold; no performance-million-operations claim. SQL/apply/rollback/checkpoint source and current manifest mirror actual installed version.
"""
for path,line in [
("wiki/index.md","- [Возврат исходных кодов при выгрузке](database/retailcase_ni052_unload_units_20261011.md):213 exact original7 units/14 codes/P7H7, UNIT locks and fingerprint, native cleanup; whole HU next."),
("wiki/log.md","2026-10-11:213 original native unload/UNIT owner restored exact7 issued units and14 CRPT+EGAIS links/current versions under sorted UNIT60 closure. Actual df2c8044 rollback/concurrent/replay/currentWARE403/cleanup0/protected13520/20. JSON_TABLE join FOR UPDATE replaced with per-key physical row lock;18 owner dependencies compiled/INVALID0. SQL1.236/6.734ms retain currentUID index/10000bound."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni05_2.md","11.10.2026:213 same unload restores exact original marked/serialized physical-unit set by original fingerprint; CRPT+EGAIS7 goods/14 codes/HARD same owner/P7H7/rollback/concurrency/currentWARE/replay passed. No new identities or legal ACK; full nested HU and accepted tare reverse custody remain."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_3.md","11.10.2026:213 predeparture unload restores original7 physical units/14 two-profile code identities under UNIT locks and original shipment fingerprint, same native P/H transaction. Original journal/codes preserved; new QC required. No government lifecycle reversal inferred.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI05.2").setdefault("implementedSlices",[]).append("213 predeparture marked/serialized same original unit fingerprint/UNIT60 locks restores exact original identities and owner HARD atomically; CRPT+EGAIS7 physical/14codes/native rollback/concurrency/replay/current scope")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI05.2"/"213_marked_unload.md")]="""# Qwen:213
Run scripts/ni052_marked_case_unload_case.py dedicated dev. Original7 physical units/14 CRPT+EGAIS code identities restore exactly to same CASE/new HARD original wave owner. No duplicate physical quantity, source5/codes10 unaffected before owned cleanup. Inspect original physical_before hash/current captured set and declared UNIT60 mutexes; modified/moved/missing unit must reject atomically. Rollback restores issued status/null HARD/P0H0/load LOADED/no recovery fact, actual concurrency1winner and exact replay/wrong currentWARE403. New QR+weight control required; original signed journal -7 remains and new+7 once/outbox once. Native cleanup preserves protected13520/20/history. Actual physical device and legal provider reversal require separate evidence.
"""
print(json.dumps(out,ensure_ascii=True))
