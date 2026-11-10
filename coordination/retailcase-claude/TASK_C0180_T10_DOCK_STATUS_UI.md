# C0180 — T10: operator UI for blocked dock status

The current yard API refuses a blocked dock, but staff cannot set or clear its blocked status in the application. Codex is implementing a native command with this contract:

- `GET /api/tradecase/warehouses/{warehouse}/yard/docks` → `{ warehouse_id, docks: [{ dock, blocked: boolean | null, ambiguous, status_error?, reason?, updated_by?, updated_at? }] }`; requires `tradecase_view`. If the legacy dictionary contains a duplicate dock name, `blocked=null, ambiguous=true`; for an invalid legacy status value, `blocked=null, status_error` is set. Disable commands for either row; do not show an invented state.
- `POST /api/tradecase/warehouses/{warehouse}/yard/docks/{dock}/status` with `{ operation_id, action: "BLOCK" | "UNBLOCK", reason }` → `{ operation_id, warehouse_id, dock, blocked, reason, updated_at }`; requires `tradecase_yard_operate`.
- `BLOCK` records the stated fault and prevents future dock assignments/plans. `UNBLOCK` records the repair/reopen reason. Neither action alters an active visit, plan, load, or shipment.
- Duplicate/ambiguous dock names fail closed; unknown command outcomes are retried with the exact same operation ID and body. Unknown dock is `YARD_DOCK_NOT_FOUND`, duplicate is `YARD_DOCK_AMBIGUOUS`, and invalid status is `YARD_DOCK_STATUS_INVALID`.

## UI scope

Implement a compact dock-status section in the existing yard/dock workspace. Show each dock's state and latest reason. Let a user with write access block or reopen a dock with a required reason and an operation ID. Explain in plain Russian what each action changes; keep active yard facts visible and do not imply that blocking cancels current work or plans. Handle 403, 409, 503 and exact retry without hiding an unknown outcome. Preserve the existing help link and narrow-screen layout.

## Ownership and checks

- Own only the UI files under `admin/wms_admin_frontend/src/features/platform/workspaces/shift/` needed for this section, plus focused UI evidence under `reports/tradecase/2026-10-27/claude/C0180/` and `RESULT_C0180.md`.
- Do not implement/mock the API, edit SQL, change shared `dist`, restart the shared API, or touch Codex fixtures.
- Start with ACK and exact paths. You may implement against the stated contract; defer live UI acceptance until Codex provides `API_READY_C0180.md`.
- Run focused checks, TypeScript, quality gate and encoding check. On API_READY, test real API/Oracle response at 1440/390; no stub for final evidence. Commit and RELEASE through the file channel. No GitHub push.
