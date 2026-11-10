# C-0185 — T10: live UI proof that a blocked dock refuses a new plan

C0184 is accepted (K-0204). Close the remaining live criterion from C0182 with a safe, owned QA visit. A read-only preflight on 8093 at 22:25 Moscow showed warehouse 220793322 docks B22D1161 and N22DA1168 both open/unambiguous and no active visits. Recheck immediately before writing; if the state changed, choose another own QA dock or abort without writing.

Use only an owned temporary inbound visit on warehouse 220793322 and dock B22D1161, reusing the established fixture pattern from `tests/tradecase/live_yard_dock_plan.py`. Do not use a production/real shipment, trip, or visit. Record the starting dock state, active visit count, active plans, inventory quantities, and slow-SQL max LOG_ID. Do not insert or change stock. Any synthetic supply/document metadata must be clearly tagged to this run; no physical receipt is claimed.

At 1440 and 390 px on your own Vite, use the real UI/API (no mocked requests):
1. Create and identify the owned QA visit.
2. Mark B22D1161 blocked with a unique operation_id and reason through the existing dock-status API.
3. In the UI, attempt to plan the owned visit into that dock. Assert HTTP 409 `YARD_DOCK_BLOCKED`, UI shows the operator text from C0182, and the plan list contains no new plan for the visit.
4. In `finally`, unblock the dock with a distinct operation_id. Cancel only your visit after plan refusal.
5. Verify GET shows dock open/unambiguous, your visit CANCELLED, no active/new plan from this run, original active visits/plans unchanged, stock quantities equal, and your temporary user revoked. If an action outcome is unknown, preserve/retry the same saved command and do not proceed with a second operation.

Before any write, read the exact route schemas and use only API commands for yard facts/status/plans. Never update native tables directly. Do not restart API 8088/8093 or alter shared dist. If cleanup cannot be proven, stop and report the exact remaining state; do not hide it. Save screenshots and a compact JSON/MD report under `reports/tradecase/2026-10-27/claude/C0185/**`, then RESULT/RELEASE. No GitHub push.

Allowed code changes only if a defect is reproduced: `admin/wms_admin_frontend/src/features/platform/workspaces/shift/YardDockPlan.tsx`, `yardModel.ts`, and an isolated test under C0185. Do not edit dock-status UI/backend/SQL/Oracle code or Codex performance files. Run focused tests, TypeScript, RETAILCASE quality gate, encoding and architecture if code changes. No wiki edits; Codex will integrate evidence into the living checklist.
