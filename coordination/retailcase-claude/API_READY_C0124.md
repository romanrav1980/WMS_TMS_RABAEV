# API_READY C0124 — PICKER_KPI_V2

Backend live on8088 (root serv session66819), formula PICKER_KPI_V2. Root updated `kpi/contracts.ts` and owns it. Actual native/API example with full DTO: `reports/retailcase/2026-10-17/kpi-v2/api-live-v2.json`, response field; warehouse20266481, own retired CASE1152 history,1line/1wholeBOX/1looseEA/1related-return25EA. Use live GET only; do not reactivate its users.

Endpoint remains GET `/api/resources/picker-kpis?warehouse_id=...&start_at=<aware>&finish_at=<aware>&operator_id=...` (operator_id optional). Same scope/31day/500operators/5000facts, current role/revoke behavior. Strict parser expects V2 now; do not use V1 fixtures. Four rates unchanged. Null is unknown.

Per operator additions: `pieces:string|null`; `shortage_completed_lines:number`; `shortage_quantities:QualityQuantity[]`; `return_events:number`; `returned_quantities:QualityQuantity[]`; `line_completions:LineCompletion[]`; `observed_pick_coverage:{total,covered_work,covered_shift:number,complete_for_observed_picks:boolean}`. Pick facts add pieces:string|null and optional box_size_base; all prior fields remain.

QualityQuantity `{article,base_uom,quantity:string}`. LineCompletion `{operation_id,task_id,line_id,actor,at,approved_at:string|null,kind:FULL|ACCEPTED_SHORT,quantity,shortage_quantity}`. `at` is the actual immutable final-pick clock, not approving manager's time. `approved_at` records aware independent approval for short; null for FULL. Credit is back to final physical pick period only after approved proof exists at as_of. No zero-picked short credit, no second line for repeated confirmation.

Related return quantities are for the operator's picked lines (possibly shared lines), observed by as_of, may occur after the pick period; not quantities proved to be that employee's fault, not a subtraction from work, not additive employee blame totals. Group by article+UOM. Historical records without native aware proof remain unavailable, not invented. `work_coverage_certified:false` remains correct globally; new observed coverage only states whether observed picks are within registered intervals. Do not label it a payroll certificate.

Proceed with KPI UI now. Whole BOX count excludes the fractional remainder, loose EA separately; do not show obsolete policy-pending/full-planned-only copy. Include approved-short line and related-return quality examples as UI fixtures; root independently creates fresh native short/return/time proof. API_READY is not proof that fresh acceptance is already complete. Final RESULT/RELEASE as one package.
