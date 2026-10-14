# NI08.1 — текущий склад пользователя задания,144

Resources owns assignment/execution policy; inventory owns root posting/UOW. Before edits selected existing RRL_TASK_RESOURCE_POLICY and task_completion as integration points; current policy preserved including released-wave fence and started-step shift completion. Native RRL_WAREHOUSE_TASK_ACCESS is sole active-user/warehouse rule: RUSERS.ID/DELETED/WARE_ID and GLOBAL_ADMIN, access to either actual FROM_WARE_ID or TO_WARE_ID. Unknown warehouse denied except active global administrator. No second resource registry.

Actual actor and optional assignee checked after task/domain metadata locks for assign/start/cancel; existing metadata permission remains action-specific. Existing resource context checks scope before document-only early return. Physical TASK_COMPLETE/HU_TASK_COMPLETE checks current permission and scope before immutable replay and again after original root locks. Document-only MES requires current mes_raw_transfer_confirm and actual MES_RAW_SUPPLY source; other completion current warehouse_task_execute. No task state/expired shift revalidation on committed replay, preserving saved effect. Oracle 20882 maps HTTP403.

Migration2026-10-10_ni081_task_scope6 statements; package/spec/body live VALID. First compile found WARE instead actual WARE_ID; corrected, reapplied, live USER_ERRORS clear. Generated current manifest includes scope before policy and current root; full ACTIVE bundle was generated only, not applied. No stock table or compatibility setting changed.

Author script ni081_task_scope_existing_case.py reuses135 user and original120 task829. Own warehouse allowed, foreign actor and assignee refused; temporarily deactivated user refused and changed current warehouse respected, both changes rolled back. Original saved DONE829 replay returns same native result through existing HTTP status/result wrapper, original journal1/qty3 unchanged. Test initially compared wrapper to inner result and fixed assertion; no business discrepancy. No real assignment/session/hardware acceptance claimed.

SQL scope call mean1.035/5.674ms, one initial13.409ms cursor. Decision retain PK task/user reads and no additional lock/query scan. Not load capacity proof. Permissions administration and foreign read-list policy remain existing separate functions.

Full NI08.1 still has physical range/approval/drain, joint schedule validation and warehouse calendar/independent acceptance open.
