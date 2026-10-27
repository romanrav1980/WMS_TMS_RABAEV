# C-0182 — T10: dock plan refused on a broken dock

## Initial state (real GET, 127.0.0.1:8093, read-only, 27.10 18:51–18:52 UTC)
- `GET /api/tradecase/warehouses/226192056/yard/docks` → 200: `TR27D226192056 blocked=false, ambiguous=false` (reason "C-0180 QA: отремонтировано, проверено").
- `GET …/yard/visits?active=true` → 200: `visits: []`.
- `GET …/yard/dock-plans?from=2026-10-26T19:00Z&to=2026-11-02T18:00Z` → 200: `plans: []`. A wider 8-day range returns 409, which is the server's range limit.

## Live part: stopped (blocker)
- The QA warehouse 226192056 has no active visits, so there is no QA visit without a plan to plan.
- Per the task I created no visits/facts, touched no one else's data, and did not block the dock.
- So there was no live sequence BLOCK → plan attempt → 409 `YARD_DOCK_BLOCKED` → UNBLOCK.
- The dock state did not change (it stays open, `blocked=false`). No new plans/visits; nothing was written.
- **To unblock:** Codex needs to provide an active QA visit (EXPECTED/ARRIVED without dock and without a plan) on 226192056, or allow the use of a specific existing one.

## Confirmed UI defect and fix
- `YARD_DOCK_BLOCKED` was explained only as "Ворота заблокированы." It didn't say why, that the plan was not created, what to do next, or that current work is unaffected.
- `admin/wms_admin_frontend/src/features/platform/workspaces/shift/yardModel.ts`: "Ворота отмечены неисправными (раздел «Состояние ворот»). План или назначение не создано; выберите другие ворота или откройте эти после ремонта. Текущие визиты и планы не менялись."
- The same text is used for the plan (`planRefusalText` → `refusalText`) and for dock assignment on a visit.
- Checked in code read-only: `yard_plan_routes.py` returns `{code, outcome_confirmed}`. A 409 with `outcome_confirmed=true` in `sendPlanPending` is a confirmed refusal: the saved command is cleared and the text is shown. That matches "план не появляется".
- `YardDockPlan.tsx` is unchanged.

## Focused UI test
`scripts/c0182_refusal_text.cjs`: transpiles the real `yardModel.ts`, no network. Result in `c0182-refusal-text.json`, PASS:
- YARD_DOCK_BLOCKED gives the new text, the same for plan and visit;
- PLAN_CONFLICT keeps its text;
- an unknown code is shown with the code itself, never as success.

## Checks
tsc --noEmit OK; RETAILCASE quality gate PASS; encoding PASS; architecture PASS (cycles 0).

## Remaining
- The live 409 `YARD_DOCK_BLOCKED` in the UI at 1440/390 and the "no side plan" check need a safe QA visit (blocker above). I'll run the scenario in the same request once one is provided: read-only check of the state → BLOCK → plan attempt → 409 → UNBLOCK in finally → final GET.
