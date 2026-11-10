# C0178 — T08: block top-up when pallet-place or stacking data is unknown

Owner asks us to finish the original sprints jointly and says Claude is waiting. C0177 T10 is delivered. The full local scenario 660→640 is complete; its synthetic test data does not establish the production package/palletization rules.

## Source-backed gap

The original revision27 scenario «Товар не подходит для добивки» requires exclusion and a reason when mass, pallet places, dimensions, quality, owner, minimum batch, available stock, expiry or delivery date fail. Current `capacity_preview` explicitly returns `floor_places_checked=false` and `stacking_rules_checked=false`. C0177 read-only inspection found `RRL_VEHICLE_PROFILE_API.check_floor_capacity`, but planned `TRIP` lines lack pallet type/place counts; active `RRL_CUSTOMER_PRODUCT_RULE` rows inspected had no `PALLET_TYPE`, and the meaning of `ALLOW_TOP_STACKING` is not established in runtime code.

## Required result

Use only confirmed data and the existing vehicle profile check. If a candidate lacks an authoritative pallet type/place count or stacking rule, fail closed: return a clear blocking reason, do not present it as fitting/approved, do not save or confirm a top-up proposal, and do not create a reservation or order. Keep `approval_available=false`. Do not infer pallet places from cubic volume, `COUNT_IN_ROW × ROWS_IN_PAL`, or an undocumented meaning of `ALLOW_TOP_STACKING`.

If a valid current package/pallet mapping exists in Oracle, demonstrate both the fitting and exceeded boundary on an isolated own fixture. If no such mapping exists, demonstrate the exact refusal against a real read-only/API preview and preserve that finding as a configuration/data blocker. Do not invent a positive case.

## Ownership and verification

- Own `api/wms_api_server/app/modules/integrations/infrastructure/{trade_capacity.py,trade_topup.py}` and focused `tests/tradecase/test_trade_floor_capacity.py`; reserve other paths in `CLAUDE_TO_CODEX.md` before editing.
- Do not alter Oracle schema/packages, `TopupProposals.tsx`, the shared frontend build, or Codex fixtures. No native migration is expected.
- Verify that a blocked preview cannot be persisted, confirmed, or leave HARD stock; verify exact replay and actor/warehouse scope where those commands are exercised. Keep the original formula for weight/volume/dimensions unless a test proves a defect.
- Run the focused suite, `retailcase_quality_gate.py`, encoding check, and a real read-only Oracle/API check. Record the slowest HTTP and `RRL_SQL_SLOW_LOG` entry; do not add an index based only on transaction timing.
- Return `RESULT_C0178.md` with paths, actual data found, exact refusal or positive boundary, cleanup, tests, timing, and remaining source requirements. No GitHub publication.

This task does not close all of T08. Any missing product-to-pallet mapping remains an explicit master-data requirement and blocks acceptance until supplied.
