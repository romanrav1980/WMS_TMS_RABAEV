# NI08.1 — история планового выхода,151

Existing immutable attendance and operation/cancellation facts are source. Read backward replacement lineage from unique CANCEL_OPERATION_ID = newer PLAN_OPERATION_ID and action REPLACE_ATTENDANCE. Do not derive person identity from a new registry or treat planned rows as physical attendance.

Same READ ONLY snapshot and current warehouse scope per page; bounded1..50 rows with next older plan ID. Ancestor edges/old cancellation facts are immutable after newer plan birth; current starting-row cancellation is state at read time. No frozen multi-page daily closing report claimed. Cycle/broken lineage refused, original aware created/plan/cancel times normalized UTC without reinterpretation of legacy naive fields.

Existing resource workload page opens history for selected plan, shows original intervals/person/site/approver/cancellation and continuation. Author uses150 original metadata-only chain2 already cleaned; no new stock or roster writes.
