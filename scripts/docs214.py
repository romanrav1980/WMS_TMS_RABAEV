from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni052_unload_hu")
out[str(f/"011_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-214-whole-case-hu-unload'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Whole original CASE matryoshka predeparture unload with append-only restored nesting',sysdate,user,'db/migrations/2026-10-11_ni052_unload_hu/apply.sql','db/migrations/2026-10-11_ni052_unload_hu/rollback.sql','APPLIED',
'Actual CASE1116/wave470/outer+inner containers/original7 units14 codes/P7H7/new links2/old links2 retained/rollback/concurrent one winner/replay/currentWARE403/native cleanup0/protected13520/20. Dedicated unslotted cell; FULLPAL/storage-slot/tare custody extensions remain.');
commit;
"""
out[str(f/"apply.sql")]="".join("@@"+name+"\n"for name in ["001_schema.sql","002_unload.sql","003_unload_guard.sql","004_load_guard.sql","005_sample_guard.sql","006_link_guard.sql","007_tare_guard.sql","008_container_guard.sql","009_recompile.sql","010_departure_guard.sql","011_ledger.sql"])
p=f/"rollback.sql";s=p.read_text(encoding="utf-8");s=s.replace("@@000_before_container_guard.sql","@@000_before_container_guard.sql\n@@000_before_departure_guard.sql");out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=[x.replace("../2026-10-11_ni052_unload_units/002_unload.sql","../2026-10-11_ni052_unload_hu/002_unload.sql")for x in m["components"]]
for name in ["003_unload_guard.sql","004_load_guard.sql","005_sample_guard.sql","006_link_guard.sql","007_tare_guard.sql","008_container_guard.sql","010_departure_guard.sql"]:
 names=re.findall(r"create\s+or\s+replace\s+trigger\s+(\w+)",(f/name).read_text(encoding="utf-8"),re.I)
 for trigger in names:
  matches=[x for x in m["additional_scripts"]if re.search(r"create\s+or\s+replace\s+trigger\s+"+trigger+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
  m["additional_scripts"]=[x for x in m["additional_scripts"]if x not in matches]
 m["additional_scripts"].append("../2026-10-11_ni052_unload_hu/"+name)
m["startup_scripts"].append("../2026-10-11_ni052_unload_hu/001_schema.sql");m["required_columns"]["RRL_TT_UNLOAD_FACT"].append("ROOT_UID")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni052_unload_hu_20261011.md"]="""# NI05.2: восстановлена двухуровневая матрёшка до выезда
214 APPLIED RABAEV/orcl; [[retailcase_ni052_unload_hu_design_20261011]]; [[retailcase_ni052_unload_units_20261011]].
Same UNLOAD_SHIPMENT/private inventory owner generalizes original standalone CASE and whole CASE-only HU_SHIP. Original frozen tree/all ST/all leaf quantity and original units required; per-child partial unload unavailable. Every CASE/wave/current owner and container original monotonic epoch/old shipped operation verified. All ST/CASE/HU/old+new link/stock/unit/tare-book/balance owners declared in global closure. New recovery links append, old inactive shipped links never reactivate. Containers original+2/current original cell/no shipped operation; each CASE WAIT_CONTROL/epoch+2, FF PICKED/ST fresh scan and weight QC required.

RRL_TT_UNLOAD_FACT now exclusive ROOT_CASE_TASK_ID-equivalent CASE_PICK_TASK_ID or real ROOT_UID; original standalone facts preserved. Native exact source plan guards protect load/unload fact, new links, original booked CASE tare, container metadata/departure and sample flags. Existing held tare is retained, accepted driver transfer still explicitly refused. Slotted storage currently requires existing placement-owner integration, unslotted expedition/system cell slice only; FULLPAL needs separate current FF projection. No orphan/fake storage claim is created.

Actual tagc62c896a/CASE1116/wave470/WARE42987529/TT33537/outer SMALL214.OUTER:c62c896a + inner SMALL214.HU:c62c896a: source original HU_SHIP -7/14codes, native unload+7/P7H7, new links2/old shipped links2 retained. Late rollback/concurrent200/409/exact replay/current nonadmin wrongWARE403 passed. Own source5 already native-cleaned before resume; same actual load resumed, not recreated. Final native detach outer→inner→CASE/return original cell/release/tare0/wave deferred/fresh count0/protected13520/20; own actor retired.

Initial author proof assertion inserted before tree helper caused NameError before load; own stock native-cleaned. Initial source SQL variable LINK_VERSION collided with column, fixed expected_link_version; current HU_DEPARTURE_GUARD discovered and fresh-captured before narrow reverse branch, no guard bypass. Syntax errors in first guard definitions corrected before successful runtime; explicit member trigger recompile after additive DDL. Final changed objects valid/errors empty required. Checkpoint includes late discovered departure guard and actual UI sources. Rollback only without actual ROOT_UID unload; otherwise forward repair.

Existing load page shows whole loaded CONTAINER as well as standalone CASE, scan outer identifier and original cell; durable uncertain retry unchanged. UI no client quantity/per-child selection. Native link history SQL2wcwywtkn04yr1.192ms/14, insert58jpqa25p9fac13.779ms/4 (guard cost), second insertd7af4hwmp0byb2.992ms/4: retain link PK/active-child constraints/200legs and16-depth/10000units bounds. Inventory owner batch at measured production scale only if threshold exceeded. TEST/synthetic codes/author proof do not close physical or independent acceptance.
"""
for path,line in [
("wiki/index.md","- [Выгрузка двухуровневой матрёшки](database/retailcase_ni052_unload_hu_20261011.md):214 outer+inner+CASE7/14 codes/P7H7, new links2/old links2 retained/native rollback/concurrency; slots/FULLPAL/tare custody next."),
("wiki/log.md","2026-10-11:214 same original unload restored two-container matryoshka/CASE1116/wave470/original7 goods14 codes/new links2, retained old inactive2. Actual rollback/concurrent/replay/currentWARE403/native final cleanup0/protected13520/20. Column-variable collision and discovered departure guard fixed with fresh paired source; API UI whole-place selection. SQL1.192/13.779/2.992ms retain bounded PK/constraints. Slot/FULLPAL/transferred tare extension pending."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni05_2.md","11.10.2026:214 whole original two-level CASE matryoshka unload applied; all source ST/CASE/container epochs and original units, new immutable nesting2/old links2/history retained. Actual7/14codes/P7H7/rollback/concurrency/replay/currentWARE403/native cleanup. Unslotted expedition slice; storage placement/FULLPAL and transferred tare next."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_1.md","11.10.2026:214 reverse departure before trip leaves restores actual outer+inner+CASE nesting with new links while original load links/history stay immutable; marked7/14codes/P7H7, native rollback/concurrent/replay/currentWARE. Existing storage-slot placement remains mandatory extension.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI05.2").setdefault("implementedSlices",[]).append("214 whole original CASE matryoshka predeparture unload restores all owner P/H/units and new nesting atomically; actual outer+inner+CASE7/14codes/new links2/old links2 retained, unslotted expedition slice")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI05.2"/"214_matryoshka_unload.md")]="""# Qwen:214
Fresh scripts/ni052_whole_hu_unload_case.py dedicated dev. Two real containers/CASE7/14codes, whole root scan before depart. Native source allST/CASE/wave/versions/old inactive link proof and exact units; no partial child unload. Rollback must restore original shipped state/no new active links/no positive journal. Actual concurrent one winner/replay/currentWARE403; restore2 new links, preserve2 old inactive links, P7H7/FF PICKED/QC revoked. Direct old link activation and metadata bypass rejected. Native outer detach then inner CASE detach before goods return/release/tare/wave/count; protected13520/20/history remain. Slotted storage/current accepted tare and FULLPAL unsupported explicitly; do not call full sprint accepted.
"""
print(json.dumps(out,ensure_ascii=True))
