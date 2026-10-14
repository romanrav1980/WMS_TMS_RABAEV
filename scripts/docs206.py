from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni042_small_hu")
out[str(f/"010_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-206-small-case-hu-control'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Measured small CASE cargo proof retained through existing HU layout',sysdate,user,
'db/migrations/2026-10-11_ni042_small_hu/apply.sql','db/migrations/2026-10-11_ni042_small_hu/rollback.sql','APPLIED',
'Own QPB206C05567F9/type14/CASE1102/v3/SSCC090000000000000148/gross.400/tare.100/net.300: unweighed child blocked under exempt parent, measured control retained pack/whole move/unpack, operational version advances, actual7then6 correction revokes. Native cleanup13520/20; ordinary v2 policy unchanged.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@009_recompile.sql\n@@010_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name,new in[("RRL_STOCK_QC_GATE","002_gate.sql"),("RRL_WH_FINAL_SCALE_ADMISSION","003_admission.sql"),("RRL_STOCK_HU_CMD","004_hu.sql"),("RRL_STOCK_PALLET_QC_CMD","005_qc.sql"),("RRL_WH_SCALE_API","006_archive.sql")]:
 matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+name+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
 assert matches,name
 m["components"]=[("../2026-10-11_ni042_small_hu/"+new)if x==matches[-1]else x for x in m["components"]if x not in matches[:-1]]
m["startup_scripts"].append("../2026-10-11_ni042_small_hu/001_schema.sql")
m["additional_scripts"]=[x.replace("../2026-10-11_ni042_final_qc/003_guard.sql","../2026-10-11_ni042_small_hu/007_guard.sql")for x in m["additional_scripts"]]
m["required_columns"]["RRL_WH_FINAL_SCALE_USE"].append("SIGNATURE_VERSION")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_small_hu_20261011.md"]="""# NI04.2: собственный контроль коробки при упаковке
206 APPLIED; [[retailcase_ni042_small_hu_design_20261011]]. Existing CASE operational CONTENT_VERSION continues increasing for attach/detach/whole move. Only requiredsmall CONTAINER gets cargo QC signature v3: same document/order/WARE/item quantities/physical epochs/codes/policies plus current CASE SSCC/type; ancestor placement links omitted. Ordinary v2 and its prior revocation preserved. Signature kind now stored in immutable scale-use row, default2 for priorfacts/current3 forsmall. One type lookup per signature, outside leaf loop.
Existing HU command retains own current full QC gate for v3small only; missing/stale own proof takes original revoke path. Declared/locked legacyST/CASE/stock already reused, no new stock writer/P/H rows/codebirth. Accepted final use permits later operational-version increase only with same v3 signature; initial QC still requires fresh current CASE command version. Real correction/restoration changes physical epoch and revokes.
Own QPB206C05567F9/type14/CASE1102/SSCC090000000000000148, source20/CASE6/source14. Unweighed attach+detach underWARENONE remains notready; fresh GROSS .400/TARE.100/current v3 then original QC .300 passes, concurrency/rollback/replay/currentrole invariants205 repeated. Accepted GROSS A7AB0BDCA9C1B644911DA56947427B7C90EBE95A3CBE262115AE07E21DA2D098/use3 retains full ready+same signature through existing HU_ATTACH→HU_MOVE tostorage→HU_DETACH, CASE operational versions advance. Native own count7then6 revokes old signature and WAIT_CONTROL despite restored quantity. Native return/count/tarezero/actorretire cleanup13520/20 preserved.
First fixture used scan_from_cell/scan_to_cell instead of existing scanned_from_cell/scanned_to_cell; Native HU_MOVE_FROM_TO_SCAN_REQUIRED refused, own cleanup passed, author fixed keys. Spec changes invalidated HU_SHIP/LOADING_READ/SINGLE_LOAD bodies; explicitly recompiled those three. Current errorsclear/VALID. No physical pilot or government aggregation ACK claimed.
Slow: existing proof insert21a9thn21944929.8ms4 (initial58ms/2 cold), final list50nt4sufyvyq87.302ms1/b1v9qxts88rk76.723ms2; retained keys and51-row bound. Inventory owner profile whole QC signature/archive guard JSON at production volume, no speculative newindex.
207 will expose proven CASE mass/identity in existing HU/transport/store manifest and use existing loadbox machinery. Source/read/loadbox fresh checkpoints captured but not changed by206. Mixed marked small-box/load/pilot remains.
"""
for path,line in[
("wiki/index.md","- [Контроль коробки внутри матрёшки](database/retailcase_ni042_small_hu_20261011.md):206 own v3 cargo proof retained through pack/move/unpack; unweighed child blocked and real7→6 restoration revokes; ordinaryv2 preserved."),
("wiki/log.md","2026-10-11:206 current small v3 cargo signature/immutableuse version/existing HU retained-own-control applied. Own QPB206C05567F9/type14/CASE1102/090000000000000148/.400−.100=.300, unweighed child under exempt parent blocked; accepted samecargo control survives pack/fullmove/unpack, actual7then6 revokes old proof. First author wrongscan keys refused/cleanup, corrected; HUship/loading/singleload invalidations recompiled. Existingproof29.8ms4 retained keys/51 bound/inventory JSON profile owner.207 actual mass manifest next."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:206 NS40 measuredsmall owncargo v3 proof retained through original HU attach/wholemove/detach, ordinaryv2 retained. ActualCASE6/gross.400/tare.100/net.300; unweighed under parentNONE remainsblocked, physical7→6 correction revokes old proof.207 provenmass in existing HU/load/store manifest next; markedsmall/physicalpilot stillopen.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");plan=json.loads(p.read_text(encoding="utf-8"));entry=next(x for x in plan["increments"]if x["id"]=="NI04.2")
entry.setdefault("implementedSlices",[]).append("206 measured small CASE v3 cargo control preserved across existing HU packing/whole move/unpacking; unweighed child not approved; real correction/restoration revokes")
out[str(p)]=json.dumps(plan,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"206_small_hu_control.md")]="""# Qwen:206
Run scripts/ni042_small_hu_control_case.py dedicated dev. Existing mandatoryscale/SSCC/onceuse/rollback/concurrency/currentWARE preserved. Source smallBOX v3 excludes position but includes actual quantity/epochs/UID/codes/policy/SSCC/type/document. Unweighed attach under exempt parent remainsblocked. Measured current full owncontrol remainsvalid across attach/wholemove/detach with operational version increases; no P/H changes for attach/detach, fullmove conserves. Real count7→6 restoration revokes old proof. Ordinaryv2 revocation not relaxed. Immutable use storesversion3; rollback blocked afterfacts. Marked child later requires exact same unitcodes/fullcontrol without inferred legalaggregation. Source mass tostore207 still pending. Original scan keys required; explicit tarebook retained. Check source/order signatures current, no recheck old freshness on accepted historical physicalfact.
"""
print(json.dumps(out,ensure_ascii=True))
