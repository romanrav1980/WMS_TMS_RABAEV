from pathlib import Path
import json
out={};page="wiki/database/retailcase_ni081_wave_time_20261010.md"
out[page]="""# NI08.1 — утверждённое окно прежней волны,140

NS33 existing RRL_PICK_WAVE is the plan owner. New immutable RRL_WAVE_TIME_PLAN stores only approved version/operation/actor/hash/current WARE-route-dock/aware window/explicit region/reason/legacy planned wall dates/result. Native RRL_WAVE_TIME_API.context/approve uses existing pick_wave_view/pick_wave_launch, active RUSERS/current WARE. No new wave, task assignment, stock or reservation writer. Migration2026-10-10-140-approved-existing-wave-time APPLIED7/0; package/body/guard/root liveVALID.

External UOW obtains original metadata CFG6 fence before wave row. SAVEPOINT after fence acquisition, not before: pre-lock/savepoint violates native clean-transaction contract. Approval validates expected version/source token under wave lock, refuses closed/cancelled or CASE IN_PROGRESS/PARTIAL and active warehouse tasks. Period aware/positive/max24hours, explicit UTC/Europe-Moscow/Asia-Tbilisi, reason required. Repeat sameID/body returns original result after current rights/WARE check; changed/stale request409, naive timestamp422. No internal commit; failure rolls back own effects and clears metadata context.

Original legacy PLANNED_START_AT/FINISH_AT updated to explicit local planned wall date for the selected region in same transaction as immutable aware plan. No old actual DATE backfill/UTC reinterpretation. Current region expression in Oracle requires AT TIME ZONE (v_zone): unparenthesized compiled VALID but returned runtime ORA00905, corrected and native rolled-back diagnostic succeeded.

WorkloadMonitor reads approved aware plan within same READ ONLY snapshot as current CASE work/norm/attendance. Accepts approved times only while original legacy dates/WARE/route/dock still match. Legacy change yields LEGACY_PLAN_CHANGED and unscheduled demand; no silent UTC assumption. Explicit preview override remains unapplied; wave/window source displayed in API. Approval does not certify staffing capacity or trip timing; monitor recalculates current deficit.

Author scripts/ni081_wave_time_existing_case.py reused135 private wave395/CASE1031+1032, no new goods. Initial approved14:52:16–16:52:16UTC/replay/stale409. Own QA134 norm20EA/5=4 person-hours, original one-person2hours roster. Approved shift+1h changed first interval required2→0 and showed remaining work outside view. Legacy minute edit on this private unstarted wave invalidated the window; explicit reconfirmationv3 restored approved15:52:16–17:52:16UTC/Tbilisi wall19:52:16–21:52:16. Naive rejected422/P20H20/tasksNEW preserved. Fixture intentionally remains active for next functional coordination.

Existing raw resource-workload page has separate explicit approval section and original durable pending action with ID/body scoped by API+actor. View/approval rights separate; no hidden hash in operator prose. Read current wave/version, choose window/zone/reason, approve, then recalculate workload. Network/5xx/auth loss retains original pending operation; node syntax check PASS, no independent rendered UI acceptance claimed.

SQL Oracle cursor averages context9.368ms/approval39.296ms/approved-window read52.031ms. Decision: retain latest-version wave PK plus at-most1001 active-wave reader with explicit bound failure. Owner resources: if active wave population makes lookup slow, add/current verify warehouse-status-wave index or bounded current-work-driven join; no broad index duplication now. Metadata fence low-volume only, no claim of high-volume goods throughput.

General quality gate fails before typechecks:477files/0cycles/135 debt items; no baseline enlargement. Separate changed transport UI TypeScript typecheck passed139. Full timing/approved joint wave-TT change/NS59 range recommendations and independent/external acceptance remain open.
"""
out["wiki/index.updated.tmp"]="- [Утверждённое окно прежней волны](database/retailcase_ni081_wave_time_20261010.md):140 aware version/replay/stale refusal/monitor reads actual approval/shift effect/P20H20 unchanged.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:140 original wave time approval aware immutable version/private guard/current rightsWARE/CFG6→wave/source optimistic token/max24h/no started task transfer. APPLIED7/0/liveVALID; native savepoint after clean metadata acquisition; dynamic AT TIME ZONE (region) avoids runtime00905. Own wave395 native approvals/replay/stale409/naive422/shift first2→0/outside workload; legacy edit invalidated/reconfirmedv3, P20H20/tasksNEW unchanged. Current aware monitor+separate durable UI approval, node syntax PASS. SQL context9.368/approve39.296/read52.031ms bounded1001/latestPK keep; current population index/join backlog resources. General gate still FAIL/0cycles/135debt, no baseline enlargement. Next joint TT linkage/plan validator and dynamic ranges."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Tickets138/139/140 delivered atomic idempotent existing cluster and explicit aware existing-wave approval/current monitor reallocation. See database/retailcase_ni081_cluster_retry_20261010.md and retailcase_ni081_wave_time_20261010.md. Joint wave-TT/driver/time/tare validator and NS59 range approval/drain remain open.")
]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("140 approved aware original wave window/current workload/legacy drift/source version/replay")
  row["evidence"]=page;row["acceptanceStatus"]="author_dev_133_140_joint_transport_timing_ranges_independent_open"
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
m["packages"].append("RRL_WAVE_TIME_API");m["components"].append("../2026-10-10_ni081_wave_time/002_api.sql")
m["additional_scripts"].extend(["../2026-10-10_ni081_wave_time/001_schema.sql","../2026-10-10_ni081_wave_time/003_guard.sql"])
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/140_утверждение_окна_волны.md"]="""# Qwen —140

Read design+wiki evidence; use own wave395 current version3/CASE1031+1032/P20H20 only, do not rerun script from version0 or create new goods.

Native CFG6 before wave, savepoint after clean fence acquisition, current active RUSERS/WARE/pick-wave roles, expected source token/version, fixed explicit regions/aware max24h, reason and no already started task transfer. SameID/body saved replay, changed/stale deny, direct version mutation deny. No internal commit/P/H/reservation/assignment writes; failure clears metadata context.

Monitor same read-only snapshot uses aware approved version only if original legacy WARE/route/dock/dates match. Legacy plan drift must become unscheduled; never reinterpret actual legacy dates as UTC. Explicit preview override remains unapplied, staffing deficit not certified by approval. Current case norm20/5=4h; one original person2h; shift+1 moves workload/outside without physical effects.

UI operator load current wave/version/WARE, explicit approval/reason/zone, durable pending before network. Auth scope change clears stale context; same pending persists after network/5xx/401/403, confirmed business/input failure may be corrected. Syntax checks are not independent rendered acceptance. Joint TT coordination, time/driver/tare and NS59 ranges not covered140.
"""
print(json.dumps(out,ensure_ascii=True))
