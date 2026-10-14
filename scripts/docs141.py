from pathlib import Path
import json
out={};page="wiki/database/nicora_ni081_operation_plan_20261010.md"
out[page]="""# NI08.1 — прежняя ARM-цепочка сохраняет факты,141

Existing TransportService.plan_operations deleted every RRL_TT_OPERATIONS row before generation, including actual FACT_START/FACT_END and prior IDs. Replaced with public native adapter/RRL_TT_OPERATION_PLAN_API.generate, same old URL/list shape and configured12 stage chain, one UOW. Unstarted existing codes updated in place; missing rows inserted, no DELETE. Real actor forwarded from old authenticated router.

Native active dispatcher/current sourceWARE/empty-trip owner and shared136 prospective vehicle rules; current vehicle before TT, operations numeric IDs. Loaded/departed physical trip, closed/billed/deleted or any recorded actual operation cannot regenerate. Old custom/duplicate chain refused for explicit review, not deleted. Norms read in one SQL snapshot; missing/invalid norm refused, explicit configured0 retained. Actual planned cargo count used, no fake minimum1. SHIPMENT_DATE+clock-part of SHIPMENT_TIME combined, no accidental date from a time-only Oracle DATE/default06:00. Native seconds rounded explicitly, Oracle NUMBER norm quantities; no goods posting.

RRL_TT_OP_EXECUTION_GUARD globally refuses deleting actual rows, clearing recorded FACT_START/END, changing actual row ID/TT/code/order/duration/planned times. Ordinary fact recording/correction/note remains available; this is preservation of current actual row, not an immutable journal of every legacy correction.

Old update_operation_fact also moved behind native write_fact: active dispatcher/current source warehouse/empty-trip owner, TT then operation lock, original TT rechecked after operation lock, no negative actual interval, one UOW/rollback savepoint. Existing legacy manual wall-date format retained; actual naive dates not certified UTC or legally authenticated driver events. API audit retains commands; direct legacy fact correction is not turned into government/physical proof by this slice.

Migration2026-10-10-141-preserve-operation-execution APPLIED6/0 and package/spec/body/guard/root liveVALID. scripts/ni081_operation_plan_existing_case.py reused136 private metadata only, original native cluster created own33530/two ST then explicit08:00. Twelve stages generated; unchanged source repeat returned identical IDs/result, LOADING2places×3min=6. Recorded first08:00–08:15 fact; regeneration409, direct deletion/clear/plan-update20886, negative finish409/fact unchanged. Own33530 cancelled/membership released/vehicle retired, execution row remains historical. No P/H/new stock.

Returned configured estimate explicitly says planning_basis=CONFIGURED_NORMS_ESTIMATE/time_window_admission=false. DRIVE/DRIVE_BACK current norm0 is not real route duration. Same current source regeneration preserves IDs, but no durable operation replay freezing past norm versions is claimed; real routing/windows/joint wave-TT/driver/tare and immutable planning decisions remain open.

SQL generate36.334ms/3, fact11.058ms/2. Decision retain short TT/source201 bounded read and existing TT_ID operation lookup/norm-code keys; do not add a duplicate index from small author sample. Source membership uses existing global TT serialization guard; no new stock lock protocol. Full NI08.1 not closed and independent acceptance remains open.
"""
out["wiki/index.updated.tmp"]="- [ARM-расчёт сохраняет фактические операции](database/nicora_ni081_operation_plan_20261010.md):141 native original12 stages/replay IDs/no DELETE/current fact scope/history guard/actual33530 no stock.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:141 original ARM generation removed destructive DELETE, native current scope/vehicle→TT→operations/shared capacity/snapshot norms/date+clock/no fake place, existing12 stages. Global actual delete-clear-key-plan guard; fact patch native current WARE/TT→operation/interval/savepoint. APPLIED6/0/liveVALID; actual own33530 original136 twoST generated/repeated identical IDs/LOADING6, fact saved/regeneration409/direct20886/negative409; cancelled metadata keeps fact/no goods. SQL36.334/11.058ms preserve bounded source/current keys. Legacy naive correction and configured zero-drive estimate not certified physical/time-window evidence; joint coordination/range recommendations next."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni08_1.md","Ticket141 preserves original ARM fact history during operation recalculation, date+clock/native shared capacity and current warehouse fact updates. See database/nicora_ni081_operation_plan_20261010.md. Current norm-based estimate is not real routing/time-window admission or durable versioned plan replay.")
]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("141 original ARM plan preserves execution/IDs/current source scopes/date+clock/native norm snapshot")
  row["evidence"]=page;row["acceptanceStatus"]="author_dev_133_141_joint_timing_ranges_independent_open"
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
m["packages"].append("RRL_TT_OPERATION_PLAN_API");m["components"].append("../2026-10-10_ni081_operation_plan/001_api.sql")
m["additional_scripts"].append("../2026-10-10_ni081_operation_plan/002_history_guard.sql")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/141_сохранение_фактов_ганты.md"]="""# Qwen —141

Read design/evidence/native package/guard/public adapters/current old URL. Own33530 cancelled, original fact history retained; do not repeat fresh stock fixture.

Unstarted operation generation uses12 configured norms in one SQL snapshot/one UOW, preserves IDs and actual history; no delete/copy. Current vehicle before TT then operations numeric, original source201 limit/current dispatcher+WARE/empty owner/shared136 capacity. Explicit shipment day+clock, no false pallet1 or missing norm0. Custom/duplicate chain refuses review, any actual/physical/billed chain cannot regenerate.

Global guard forbids deleting actual rows/clearing facts/changing actual keys or planned fields; ordinary fact corrections/note permitted. Native fact API current actor+WARE/TT→operation/TT recheck/finish>=start, no stock. Check foreign actor/source/current role loss and racing fact write versus generation; use metadata only. Negative fact update must not partially alter note/start/finish.

Configured DRIVE0 is estimate only; no time-window/route/driver legal certification. Same current source retry preserves IDs, no immutable norm-version replay claimed. Legacy manual DATE format not physical UTC. Full NI08.1/range/joint planning remains open.
"""
print(json.dumps(out,ensure_ascii=True))
