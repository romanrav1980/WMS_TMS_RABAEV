from pathlib import Path
import json
out={};page="wiki/database/retailcase_task_single_writer_cleanup_20261010.md"
out[page]="""# Единственное завершение задания и SAP metadata scope,146

Removed unused WarehouseTaskService._complete_task_locked PREPARED completion branch and exclusively-used Python scan/quantity/resource fallback. No other source caller found. Live complete_task still enters inventory public/native root; live assign/start/cancel sync preserved. Sole physical writer remains RRL_STOCK_POSTING_API. Three cutover-boundary cases PASS, old handlers never invoked in inactive release states.

Receiving SAP cancel takes its own original metadata UOW before ordinary wrapper, so144 wrapper scope alone did not cover this route. Corrected source and earlier completeness implication: native144 access adapter now checks current actor in Receiving.cancel and replan before document lookup/replay and again after task lock. Original document/claim/outbox cancellation is unchanged; no nested UOW introduced. Native20882 converted PermissionError and old replan API/SAP-cancel legacy facade403. Permission and receiving document state remain existing rules.

ReplanPutaway scanned pallet max150 and exact saved internal ID comparison first; optional SSCC normalization only for nonmatching alternative representation. Internal42-character example accepted in DTO unchanged. Not a claim of real replan execution for a new receipt.

Author ni081_receipt_scope_existing_case.py executes adapter actual admin/task829 permitted, actual135 foreign actor refused PermissionError; no writes. No active SAP placement fixture present and no suitable nonadmin metadata rights actor found; did not create new physical receipt just for checking. Actual full SAP cancel/replan acceptance remains Qwen task. Existing cutover tests3 PASS.

Architecture after removal489files/0cycles; remaining code debt not accepted/threshold not raised. Native144 keyed scope timing applies, no new Oracle SQL budget rule or migration. NS59 physical ranges/calendar/joint schedule validation remain open.
"""
out["wiki/index.updated.tmp"]="- [Удалён старый путь завершения задания](database/retailcase_task_single_writer_cleanup_20261010.md):146 native root only/SAP cancel-replan current scope/internal pallet ID;3 cutover cases PASS.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for p,line in [
("wiki/log.md","2026-10-10:146 removed unreachable PREPARED Python task completion/scans/resource fallback; live native complete and metadata sync retained. Corrected144 coverage gap: SAP cancel bypasses ordinary wrapper, now native scope in original Receiving cancel/replan UOW before replay+after lock, PermissionError403. Internal saved replan ID150/exact-first; DTO42 unchanged. Actual scope helper foreign refusal/no writes;3 cutover casesPASS; no new SAP stock fixture/independent acceptance."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Ticket146 removes obsolete PREPARED completion and extends144 scope to original SAP cancel/replan; original internal IDs retained. See database/retailcase_task_single_writer_cleanup_20261010.md.")
]:out[p]=Path(p).read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("146 obsolete physical completion removed/SAP metadata task scope/internal replan identifiers")
  row["evidence"]=page
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/146_единственное_завершение_и_SAP_отмена.md"]="""# Qwen —146

Read144/146 current policy/facade/Receiving. No callable PREPARED physical completion, all live completion native. Existing assign/start/cancel sync intact.

SAP cancellation branches before ordinary wrapper: existing Receiving UOW itself current scope before lookup/replay and after task lock. Actual nonadmin own/foreign/current deactivation with proper rights,403 and no config/claims/outbox/stock change on failure. Original receipt must be author-owned; do not recreate production stock. Completed/cancelled state rules unchanged. Cancellation releases reserved placement only, no physical P effect; replan original reservations/outbox atomic.

Saved internal identifier42 accepted exactly, max150; unmatched true SSCC alternate normalized only. Full actual SAP cancel/replan not author exercised because no active own fixture; report independent result honestly. Three cutover tests authorPASS, scope helper real foreign denied.
"""
print(json.dumps(out,ensure_ascii=True))
