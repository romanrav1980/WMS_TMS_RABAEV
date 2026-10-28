# C0197 — UI: bind an intact root HU to one prepared ST

## Scope

Implement only the operator action already supported by `POST /api/warehouse-hus/bind-shipment` in the raw WMS workspace. Do not implement multi-order shipping, QC slices, loading, Oracle, backend, tests, API calls, screenshots, or GitHub publication.

## Owned files

- `wiki-raw/wms_admin_ui_reference/warehouse-hus.html`
- `wiki-raw/wms_admin_ui_reference/warehouse-hus.js`
- `docs/help/public/warehouse-hus.html`
- `reports/tradecase/2026-10-28/claude/C0197/README.md`
- `coordination/retailcase-claude/RESULT_C0197.md`

Do not edit other files.

## Required behavior

1. After a root composition is read, show a compact section **«Привязать корень к СТ»** only for a top-level `CONTAINER` containing at least one CASE and only while the composition is current.
2. Ask for the prepared ST identifier. Reuse the existing HU command-intent storage and retry semantics. Save one exact request before POST: `operation_id`, `shipment_identifier`, `scanned_root`, `expected_root_version`.
3. POST only to `/api/warehouse-hus/bind-shipment`. Do not send a CASE endpoint or detach/re-attach a child CASE.
4. On success show the returned CASE count and re-read the root composition. On a confirmed refusal show the server response. On uncertain outcome keep the saved request and offer only the existing exact retry/re-read flow.
5. Each new visible button must have `title` and `data-help-id`. Add concise help text that says one root is bound to one ST and one recipient; it must not promise that several orders or electronic final-scale captures are supported.
6. Keep the page usable at 390 px. Reuse existing classes and controls; no visual redesign.

## Acceptance material

Return an ACK first through `CLAUDE_TO_CODEX.md`. When finished, save a short RESULT with changed files, exact user flow, limitations, and local commit hash. Do not run or claim tests; Codex performs acceptance.
