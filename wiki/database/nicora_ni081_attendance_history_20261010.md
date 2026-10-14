# NI08.1 — история планового выхода,151

Resources read model reuses immutable RRL_WORKLOAD_ATTENDANCE/OPERATION/CANCEL. Backward replacement edge is relational unique CANCEL_OPERATION_ID=newer PLAN_OPERATION_ID with newer action REPLACE_ATTENDANCE. Original person/site/resource/interval/reason/approver and cancellation actor/time retained. UTC formats only aware source columns, no legacy naive reinterpretation or actual presence claim.

GET /api/resources/workload/warehouses/{ware}/attendance/{plan}/history, current resource_shift_view and current active warehouse actor. READ ONLY snapshot per page, limit1..50 plus one; recursion depth itself bounded, not just output. next_plan_operation_id continues older immutable chain. Cycle/missing link refused; no foreign warehouse row quietly treated as correct lineage. Current starting row state is at read time, not frozen daily report across requests.

Author ni081_attendance_history_existing_case.py original150 metadata-only chain tag646cf96a33: two rows, limit1 correct continuation, original source cancelled by exact replacement, replacement cancelled by own cleanup, original planned_by/admin/aware times, wrong warehouse plan404. Operation count unchanged/no new fixture. Current role deactivation/foreign nonadmin view independently verify.

Raw workload UI history button and previous-change continuation, original intervals/reasons/actors/cancellation, stale owner/warehouse/site response suppressed; planned versus actual explicit. Node syntax PASS. ArchitecturePASS502files0cycles79legacydebt, baseline unchanged.

SQL history9.850/10.000ms per4 executions, first13.382ms; decision retain source/cancel PK/unique relational traversal and depth cap<=51, no new index or full-tree scan. No load benchmark. Full NS33 subwarehouse/approved recommendation and joint schedule integration remain open.
