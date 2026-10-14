from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_box_capacity")
out[str(f/"003_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-184-weight-box-volume-budget'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Existing pick-face capacity uses physical weighted box volumes; conservative prospective KG upper bound, no BOX-to-KG average',sysdate,user,
'db/migrations/2026-10-11_ni042_box_capacity/apply.sql','db/migrations/2026-10-11_ni042_box_capacity/rollback.sql','APPLIED',
'Own weighted wave417 CASE1057 actual storage19.6KG/two boxes/.06m3 -> existing full replenishment/pick-face.2m3/HARD9.8/CASE9.8/replay/native cleanup; no BOX conversion; current malformed GS1409/manual fact422/foreign403; helpers VALID; bounded200 lots/10000 units, not industrial certification');
commit;
"""
p=f/"apply.sql";out[str(p)]=p.read_text(encoding="utf-8")+"@@003_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["components"]=[x.replace("../2026-10-10_ni081_range_apply/004_capacity_contract.sql","../2026-10-11_ni042_box_capacity/002_capacity_contract.sql")for x in m["components"]];m["components"].insert(0,"../2026-10-11_ni042_box_capacity/001_weighted.sql");m["packages"].append("RRL_WEIGHT_BOX_CAPACITY");out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_box_capacity_20261011.md"]="""# NI04.2: вместимость весовых коробок без среднего BOX→KG
184 APPLIED. Original RRL_STOCK_REPL_CAPACITY signature/callers retained. Weighted SKU uses RRL_WEIGHT_BOX_CAPACITY pure read helper; no physical balance writer added.
Занятый объём — сумма BOX_VOLUME_M3 фактических единиц текущей паллеты/ячейки с проверкой sum(BASE_QTY)=P. Pending own source reservation charges full physical reserved-box volume; partial other arrival conservatively charges the entire current source volume. No average-box mass, invented UOM BOX→KG, proportional box splitting or missing dimension fallback.
Prospective KG budget = free volume / maximum actual volume-per-netKG among current physical boxes of the SKU in this warehouse. This is a conservative upper bound for the known eligible physical set, not an exact packing optimizer or a configured average mass. Sources/dimensions immutable per physical capture; execution keeps current cell/policy locks and revalidates the budget. Conservative booking may reserve more space than ultimately needed, never less for those known boxes.
Missing/invalid measured volume, NULL/nonKG quantity, or physical composition mismatch produce explicit refusal. Bounded200 positive source lots/10000 units/200 pending arrivals; historical million-unit capacity not claimed. Existing CURRENT_UID/CURRENT_CELL/STOCK_STATUS index supports per-pallet physical read; source candidates use same bounded warehouse/SKU stock set.
scripts/ni042_weight_box_capacity_case.py: QW184C863807924/own wave417 CASE1057. Two9.8KG boxes/.03m3 each born in storage, pick face MAX_VOLUME.2m3. Original launch/source reservation/full pallet replenishment moved19.6KG/.06m3 into pick face without any BOX conversion. Existing own HARD9.8/weighted scan CASE9.8/unit1/replay/changed409. Native return/tare cancel/wave finish/count cleanup; source original135 P20H20 retained.
scripts/ni042_weighted_case_error_case.py: invalid GS1 returns409 (native pre-read rejection mapped), unexpected manual fact422, current Q134 foreign warehouse403, no operation facts. New weighted request extra forbidden. Native direct generic weighted CASE without label remains rejected by182 helper.
SQL: weighted ratio6kvy612q11tca avg7.531ms/10; composition page f7t43p9rhyb0m6.061ms/1; existing wave metadata update1drbuc6zd1juh8.631ms/6. Decision: retain bounded/indexed read; inventory owns batch candidate summary/plan review before scaling beyond bounds. No additional index justified by current sample. Algorithm overreservation optimization remains backlog, not unsafe numeric conversion.
Fresh capacity source/checkpoint/paired rollback, helpers/body compile0errors. Existing unweighted algorithms unchanged. Remaining NS36 scales/stability/tolerance/last-box and pick modes; full NI04.2 stays open.
"""
for path,line in [
 ("wiki/index.md","- [Вместимость весовых коробок](database/nicora_ni042_box_capacity_20261011.md):184 actual physical volume/current bounded conservative KG budget, original replenishment19.6→CASE9.8 without BOX conversion; unknown dimensions refused."),
 ("wiki/log.md","2026-10-11:184 APPLIED: original capacity reads physical box volumes, conservative prospective budget, existing storage→replenishment→HARD→weightedCASE PASS; no BOX average. Error contract malformed409/manual422/foreign403. Slow ratio7.531ms/10 bounded lookup retained, inventory batching/plan backlog."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:184 weighted actual-volume budget/native original replenishment source19.6KG/.06m3→pick-face.2m3→CASE9.8 passed without fixed BOX→KG. Conservative prospective space bound; missing dimensions refused. Scales/stability/order tolerance/lastbox/pick modes remain open.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");plan=json.loads(p.read_text(encoding="utf-8"));plan["currentSprint"]="NI04.2";plan["currentStream"]="NI04"
for inc in plan["increments"]:
 if inc["id"]=="NI04.2":
  inc.setdefault("implementedSlices",[]).extend([
   "179 independent weighted SKU/native GS1/netKG/existing physical birth registry",
   "180 SAP weighted capture/181 existing SAP PUTAWAY identity repair",
   "182 server/native/TSD weighted CASE one physical unit/exact retry/own HARD",
   "183 exact gross/volume/raw-label and applicable QR preserved in composition",
   "184 actual-volume existing replenishment and bounded conservative space budget"])
  inc["acceptanceStatus"]="targeted_own_birth_sap_marked_case_replenishment_passed_full_sprint_independent_scales_and_modes_pending"
out[str(p)]=json.dumps(plan,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"184_weighted_box_capacity.md")]="""# Qwen:184
Run scripts/ni042_weight_box_capacity_case.py and scripts/ni042_weighted_case_error_case.py with own tags. Confirm original full replenishment19.6KG/two volumes.03→pick-face cap.2 occupied.06→HARD9.8/CASE9.8; no BOX conversion, average mass or physical unit split. Exact replay/native cleanup. Confirm null volume fails when bounded capacity configured; full physical sum must equalP. Prospective max actual V/KG ratio is deliberately conservative, not packing optimizer. Bounds200lots/10000units explicit. Invalid barcode409/unknown fact422/foreign403/no OP. Do not fabricate missing dimensions/real scale or government ACK. Inspect longest relevant SQL; inventory batching/plan owner.
"""
out[str(f/"installed_sources.json")]=json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest().upper()for p in f.glob("*.sql")},indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
