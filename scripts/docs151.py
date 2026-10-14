from pathlib import Path
import json
out={};page="wiki/database/retailcase_ni081_attendance_history_20261010.md"
out[page]="""# NI08.1 — история планового выхода,151

Resources read model reuses immutable RRL_WORKLOAD_ATTENDANCE/OPERATION/CANCEL. Backward replacement edge is relational unique CANCEL_OPERATION_ID=newer PLAN_OPERATION_ID with newer action REPLACE_ATTENDANCE. Original person/site/resource/interval/reason/approver and cancellation actor/time retained. UTC formats only aware source columns, no legacy naive reinterpretation or actual presence claim.

GET /api/resources/workload/warehouses/{ware}/attendance/{plan}/history, current resource_shift_view and current active warehouse actor. READ ONLY snapshot per page, limit1..50 plus one; recursion depth itself bounded, not just output. next_plan_operation_id continues older immutable chain. Cycle/missing link refused; no foreign warehouse row quietly treated as correct lineage. Current starting row state is at read time, not frozen daily report across requests.

Author ni081_attendance_history_existing_case.py original150 metadata-only chain tag646cf96a33: two rows, limit1 correct continuation, original source cancelled by exact replacement, replacement cancelled by own cleanup, original planned_by/admin/aware times, wrong warehouse plan404. Operation count unchanged/no new fixture. Current role deactivation/foreign nonadmin view independently verify.

Raw workload UI history button and previous-change continuation, original intervals/reasons/actors/cancellation, stale owner/warehouse/site response suppressed; planned versus actual explicit. Node syntax PASS. ArchitecturePASS502files0cycles79legacydebt, baseline unchanged.

SQL history9.850/10.000ms per4 executions, first13.382ms; decision retain source/cancel PK/unique relational traversal and depth cap<=51, no new index or full-tree scan. No load benchmark. Full NS33 subwarehouse/approved recommendation and joint schedule integration remain open.
"""
out["wiki/index.updated.tmp"]="- [История планового выхода](database/retailcase_ni081_attendance_history_20261010.md):151 original aware records/approver/cancellation/relational chain/paginated depth bound/current warehouse/read-only.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for p,line in [
("wiki/log.md","2026-10-10:151 planned attendance history from immutable original rows/operation/cancellation, unique relational replacement edge/current warehouse/view rights/read-only snapshot perpage/depth<=limit+1/cycle or missing link refusal. Original150 cleaned chain2/limit1 continuation/old and new cancels/foreign plan404/count unchanged. Raw history+continuation/stale scope/nodePASS; architecture502files0cycles79debtPASS. SQL9.850/10.000/first13.382ms keyedbounded traversal retained. Planned not actual/frozen dailyreport, independent nonadmin and rendered acceptance open."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Ticket151 operator-visible original attendance history/relational replacement/cancel chain/read-only current scope and bounded continuation; see database/retailcase_ni081_attendance_history_20261010.md.")
]:out[p]=Path(p).read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("151 original planned attendance history/aware actors-cancellation/source lineage/bounded operator view")
  row["evidence"]=page
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/151_история_планового_выхода.md"]="""# Qwen —151
Original immutable planned/cancellation rows/operation created times, no actual attendance inferred. Relational backward edge CANCEL_OPERATION_ID=newerPLAN, newer REPLACE action; source identity and actor/reason preserved. Scope current active warehouse and resource_shift_view; foreign source404/nonadmin foreign warehouse403/deactivated denied.

Limit1..50/one continuation row and recursion depth bounded, source chain/cycle/broken link refusal. Ancestor edges immutable; starting-row cancellation state at read, no frozen dailyreport claim. Original150 cleaned chain2 tag646cf96a33; no new roster/stock fixture. UI history/continuation/stale scope and error retains continuation. Author existingchain/node/architecturePASS, independent rendering/rights cases remain.
"""
print(json.dumps(out,ensure_ascii=True))
