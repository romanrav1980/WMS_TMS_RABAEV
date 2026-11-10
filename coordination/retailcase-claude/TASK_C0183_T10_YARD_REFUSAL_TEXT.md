# C-0183 — T10: clear messages for yard and dock-plan refusals

The yard screen has a specific message for `YARD_DOCK_BLOCKED` after C0182, but several errors from the current visit and dock-plan APIs still fall through to the generic code display. Audit actual refusal codes from `yard_plan_routes.py`, yard routes, `2026-10-23_yard_dock_plan/003_visit_body.sql`, `004_plan_api.sql`, and `2026-10-23_yard_inbound/002_supply_api.sql` against `yardModel.ts`.

Add short, actionable Russian text only for confirmed codes that lack an entry. Keep fallback behavior for unknown future codes. Do not claim that data is unchanged unless the native refusal guarantees no effect. Do not map unrelated infrastructure or success states as business errors. Focus on errors actually returned to a yard or dock-plan operator, including ambiguous dock, unsupported inbound action, invalid time window, and boundary errors where an operator can act.

## Ownership and verification

Own only `admin/wms_admin_frontend/src/features/platform/workspaces/shift/yardModel.ts`, a focused test for this model, and `reports/tradecase/2026-10-27/claude/C0183/**` plus `coordination/retailcase-claude/RESULT_C0183.md`. Do not change API, SQL/Oracle, shared dist, fixtures, wiki, `YardDockPlan.tsx`, or `YardDockStatus.tsx`.

Build a checked list mapping each native/API refusal code to its UI text or to the retained unknown-code fallback. Add focused tests for every newly mapped code, existing `YARD_DOCK_BLOCKED`, and one unknown code. No live write is needed or allowed. Run TypeScript, RETAILCASE quality gate, architecture and encoding; commit locally, then RELEASE through the file channel. No GitHub push.
