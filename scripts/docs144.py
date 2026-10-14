from pathlib import Path
import json
page="wiki/database/nicora_ni081_task_scope_20261010.md";out={}
out[page]="""# NI08.1 — текущий склад пользователя задания,144

Resources owns assignment/execution policy; inventory owns root posting/UOW. Before edits selected existing RRL_TASK_RESOURCE_POLICY and task_completion as integration points; current policy preserved including released-wave fence and started-step shift completion. Native RRL_WAREHOUSE_TASK_ACCESS is sole active-user/warehouse rule: RUSERS.ID/DELETED/WARE_ID and GLOBAL_ADMIN, access to either actual FROM_WARE_ID or TO_WARE_ID. Unknown warehouse denied except active global administrator. No second resource registry.

Actual actor and optional assignee checked after task/domain metadata locks for assign/start/cancel; existing metadata permission remains action-specific. Existing resource context checks scope before document-only early return. Physical TASK_COMPLETE/HU_TASK_COMPLETE checks current permission and scope before immutable replay and again after original root locks. Document-only MES requires current mes_raw_transfer_confirm and actual MES_RAW_SUPPLY source; other completion current warehouse_task_execute. No task state/expired shift revalidation on committed replay, preserving saved effect. Oracle 20882 maps HTTP403.

Migration2026-10-10_ni081_task_scope6 statements; package/spec/body live VALID. First compile found WARE instead actual WARE_ID; corrected, reapplied, live USER_ERRORS clear. Generated current manifest includes scope before policy and current root; full ACTIVE bundle was generated only, not applied. No stock table or compatibility setting changed.

Author script ni081_task_scope_existing_case.py reuses135 user and original120 task829. Own warehouse allowed, foreign actor and assignee refused; temporarily deactivated user refused and changed current warehouse respected, both changes rolled back. Original saved DONE829 replay returns same native result through existing HTTP status/result wrapper, original journal1/qty3 unchanged. Test initially compared wrapper to inner result and fixed assertion; no business discrepancy. No real assignment/session/hardware acceptance claimed.

SQL scope call mean1.035/5.674ms, one initial13.409ms cursor. Decision retain PK task/user reads and no additional lock/query scan. Not load capacity proof. Permissions administration and foreign read-list policy remain existing separate functions.

Full NI08.1 still has physical range/approval/drain, joint schedule validation and warehouse calendar/independent acceptance open.
"""
out["wiki/index.updated.tmp"]="- [Склад пользователя складского задания](database/nicora_ni081_task_scope_20261010.md):144 current active actor/assignee WARE, root replay authorization, old829 replay exact/no new quantity.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for p,line in [
("wiki/log.md","2026-10-10:144 native current task scope RUSERS active/WARE_ID/either endpoint/GLOBAL_ADMIN reused in original resource policy, assign/start/cancel and physical root before replay+after locks. Six statements/live VALID after WARE_ID compile correction. Existing135 actor/assignee foreign and inactive/current changed ware refusals; user changes rolled back; original DONE829 HTTP inner result exact/journal1 qty3 unchanged. Scope1.035/5.674ms/initial13.409 kept keyed reads; no load claim. Full sprint still open."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni08_1.md","Ticket144 current warehouse task actor/assignee scope and completion replay rights implemented; see database/nicora_ni081_task_scope_20261010.md. No new assignment engine.")
]:
 out[p]=Path(p).read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("144 current actor/assignee warehouse task scope and authorized immutable replay")
  row["evidence"]=page;row["acceptanceStatus"]="author_dev_133_144_physical_ranges_calendar_joint_timing_independent_open"
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/144_склад_исполнителя_задания.md"]="""# Qwen —144

Read live scope source/current manifest/resource policy/root/task_completion. Existing135 person and original120 task829 only; no fresh goods. Own current warehouse accepted, foreign actor and assignee/DELETED/missing warehouse denied; current GLOBAL_ADMIN only. Restore any temporary RUSERS edits by rollback, never leave authorization changes committed.

Assign/start/cancel scope after metadata/task lock; physical TASK_COMPLETE/HU_TASK_COMPLETE current rights/scope before replay and after root locks. MES document-only source/permission, started-step shift rule and wave release retained. Completed replay must not re-run current task state/session rule, must return original native result and no extra event. HTTP wrapper is status/result, compare inner saved result. Check20882 maps403. No independent acceptance or real assignment session claimed.
"""
print(json.dumps(out,ensure_ascii=True))
