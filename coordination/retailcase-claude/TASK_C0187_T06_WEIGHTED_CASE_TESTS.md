# C0187 — T06 weighted-case write-path coverage

## Evidence / objective

`api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py` exposes `POST .../weigh-line` and `POST .../weighted-box`; the implementation in `weighted_case_pick.py` validates an archived NET capture or a serialized weighted box, then uses the existing `StockPosting` command. Search of `tests/` found no tests covering either write path. Add focused tests for the real route/service contracts and fix only a defect proven by those tests.

## Ownership

Reserve:
- `tests/retailcase/test_weighted_case_pick.py` (or a tightly scoped `tests/tradecase/` file if the scenario belongs there; do not duplicate both)
- production code only if a regression test proves a defect: `api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py`, `contracts_weighted_case.py`, `api/weighted_case_routes.py`
- `reports/tradecase/2026-10-27/claude/C0187/**`
- `coordination/retailcase-claude/RESULT_C0187.md`

Do not change Oracle SQL, schemas/migrations, API wire fields, existing fixture data, Codex-owned resource-timeline files, shared dist, or API processes. No live database writes. No GitHub push.

## Required coverage

1. Accepted NET capture belongs to the exact CASE task/line and actor scope; another line, missing capture, wrong basis, and access denial do not post stock.
2. Exact same `operation_id`/body returns the original result once; changed capture, actor, task, line, or payload conflicts and cannot post again.
3. Weighted-box path rejects a box reserved to another SKU/line, wrong KG amount, missing/duplicate product or marking scans, stale policy/profile, duplicate barcode, and malformed measurement. A valid mocked prepared item reaches the existing posting port exactly once.
4. Verify the route requires `case_pick_execute` and returns actionable confirmed refusal codes. Do not call a mocked scale reading “hardware” or “live weight evidence.”
5. Independently review whether the two child sources can be combined in one parent HU tree using current HU attach contracts. Report the exact allowed shape and what is still missing for the owner's mixed tree (manual weighed assembly + box/each shelf pick). Do not modify or weaken HU guards.
6. Run focused tests, `python scripts/retailcase_quality_gate.py`, encoding and architecture checks. Report exact commands/results. No broader test suite unless the implementation changes.

If safe behavior cannot be tested without a live write or unclear source, stop before the write and state the precise blocker. ACK paths and test approach before editing, then RESULT and RELEASE.
