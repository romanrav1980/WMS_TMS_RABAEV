# C-0193 — binding one root HU to one mixed ST

## Problem (root's live run)
`POST /api/case-pick/tasks/{id}/bind-shipment` binds one CASE carrier to one ST and checks one carrier's composition against all of the ST's rows. For an ST with an aggregate KG+EA composition the second CASE is refused, while splitting the children across STs is forbidden by the owner's rule (one root, one recipient).

## Solution (inventory module, public contract)
- `contracts_root_shipment.py`:
  - `RootShipmentBindRequest {operation_id(≤80), shipment_identifier, scanned_root, expected_root_version}` (extra=forbid);
  - `RootShipmentPort`, `root_shipment_service`;
  - `RootShipmentError` re-exported from the domain.
- `domain/root_shipment.py` (pure rules):
  - `request_hash`;
  - `root_children`: the root is a top-level PALLET/BOX of the expected version, ≥1 CASE, no duplicates, only CONTAINER/CASE/STOCK nodes;
  - `check_tasks`: each CASE is present, same warehouse, the same SSCC, closed (WAIT_CONTROL/CONTROL_IN_PROGRESS/CONTROLLED/READY_TO_SHIP), version = the node's version, not bound to an ST, one CASE per order;
  - `check_fulfillments`: the ST's fulfillment orders equal the root's orders, exactly one PLANNED per order, one recipient address;
  - `assert_tree_matches_carriers`: the root's STOCK leaves equal the sum of the CASE carriers.
- `infrastructure/root_shipment_binding.py`: one supported metadata transaction `receipt_task_metadata` (RRL_STOCK_METADATA_TX).
  1. **Locks and checks:**
     - ST FOR UPDATE, then the operation journal (exact repeat or conflict);
     - the ST must not be bound to another physical root (any CASE with this ST);
     - the root composition from the native `RRL_STOCK_HU_READ.snapshot_json` (read only);
     - CASE tasks FOR UPDATE, fulfillments FOR UPDATE, all checks;
     - the aggregated carrier lots vs the ST rows in base units through the existing `assert_matching_composition`.
  2. **Writes, only after all checks:**
     - every CASE gets `LEGACY_SBORKA_PALLET_ID` = **the same** ST (with `is null` and rowcount=1);
     - every fulfillment becomes `PICKED` with **its own** CASE composition and version (`physical_composition`, with `STATUS='PLANNED'` and rowcount=1);
     - a `ROOT_SHIPMENT_BOUND` event per CASE.
  3. **The HU tree is not changed** (no detach/repack), and stock is not written.
- **Idempotency without DDL:**
  - `OFFLINE_EVENT_ID = <operation_id>:<task>` (the global unique index `RRL_CASE_PICK_EVENT_U1`); the payload holds `request_hash` (body + actor) and the full result;
  - exact repeat → the stored result (`idempotent=true`) with no new effects;
  - a different body or actor under the same operation → `OPERATION_CONTENT_CONFLICT` (409, `operation_id_conflict=true`).
- `api/root_shipment_routes.py`: `POST /api/warehouse-hus/bind-shipment`, `case_pick_execute`; refusals are 409/404 with a code and `outcome_confirmed=true` (a conflict gives false).
- **Registration:**
  - `inventory/public.py`: exports + `build_root_shipment_binding`;
  - `app/main.py`: 2 lines (include_router + dependency override, with the `OracleGateway` import).
- The existing single-CASE binding is not changed.

## Refusals (codes)
| Situation | Code |
|---|---|
| CASE bound to another ST | `ROOT_CASE_ALREADY_BOUND_TO_ANOTHER_ST` |
| missing or foreign CASE | `ROOT_CASE_MISSING_OR_FOREIGN` / `ROOT_CASE_FOREIGN_WAREHOUSE` |
| CASE not closed | `ROOT_CASE_NOT_CLOSED` |
| changed CASE version | `ROOT_CASE_VERSION_CHANGED` |
| two CASEs of one order | `ROOT_CASE_ORDER_NOT_UNIQUE` |
| different recipient | `ST_RECIPIENT_NOT_SINGLE` |
| ST fulfillments for another order, or not one PLANNED | `ST_FULFILLMENT_ORDERS_DIFFER_FROM_ROOT` / `ST_FULFILLMENT_NOT_SINGLE_PLANNED` |
| changed root version | `ROOT_VERSION_CHANGED` |
| changed composition (tree ≠ carriers) | `ROOT_COMPOSITION_CHANGED` |
| ST ≠ root composition | `ST_COMPOSITION_DIFFERS_FROM_ROOT` |
| ST bound to another root | `ST_ALREADY_BOUND_TO_ANOTHER_PHYSICAL_ROOT` |
| not PALLET/BOX, not top-level, ST warehouse/state | `ROOT_PALLET_OR_BOX_REQUIRED` / `ROOT_MUST_BE_TOP_LEVEL` / `ST_WAREHOUSE_OR_STATE_MISMATCH` |
| unknown root / ST | `ROOT_NOT_FOUND` / `ST_NOT_FOUND` (404) |

## Checks (commands)
- `python -m pytest -q -p no:cacheprovider tests/retailcase/test_root_hu_shipment_bind.py` → **26 passed**:
  - KG+EA two-CASE root → one ST, one recipient: both CASEs on ST 900, each fulfillment with its own composition, 2 events;
  - exact repeat with no new effects;
  - a changed body (version, root) or another actor → conflict with no effects;
  - 16 refusals, each checked to write nothing (no updates or events);
  - unknown root/ST → 404;
  - source check: one ST id for all children; no `/detach`, `HU_DETACH`, `RRL_WMS_HU_LINK`, stock writes, StockPosting or ST creation; locks and `receipt_task_metadata` present;
  - operation_id ≤80;
  - the route needs `case_pick_execute` (403 without it), 409 mapping and conflict, extra field 422;
  - `app.main` registers the route, and the factory builds the service.
- `python scripts/retailcase_quality_gate.py` → PASS; `scripts/check-encoding.ps1` → PASS; `python scripts/check_architecture.py` → PASS (cycles 0; the domain does not import the contract).

## Limitations
- **Not run against a live Oracle/API.** On the target runtime the following are unconfirmed:
  - the fields of `RRL_STOCK_HU_READ.snapshot_json` for a CASE node (`case_task_id`, `version`, `sscc`; taken from the real 22.10 composition and the C0190 code);
  - the behaviour of the `RRL_CASE_*_GUARD` triggers on `LEGACY_SBORKA_PALLET_ID` (the existing single binding updates the same column).
- The new route is available in the shared API only after root restarts it.
- C0191 SHIPMENT can then switch from per-CASE `bind-shipment` (detach/bind/reattach) to this route; that is integration in Codex-owned C0191 and is not done here.
