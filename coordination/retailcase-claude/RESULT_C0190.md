# C-0190 — T06: runner for the live acceptance of the mixed tree (fail-closed)

## Why a new runner
No existing script covers the criterion from `tradecase_nested_shipping_20261023.md`:
- NS23: a whole warehouse place with one SKU;
- T07 bulk-packing: two CASEs of the same SKU;
- ni042: a weighed CASE without a tree, with an electronic capture.

## Files
- `scripts/c0190_mixed_tree_runner.py` (root runs it; Claude did not run it in live modes)
- `tests/retailcase/test_c0190_mixed_tree_runner.py` (offline, 55 tests)
- `reports/tradecase/2026-10-28/claude/C0190/plan.json` (output of `plan`)

## How it works
Modes: `plan` (default, no network or Oracle) · `preflight` (read only) · `run` · `cleanup`. `--api` is required for the live modes (the shared 8088 does not serve C0188 yet), along with `--api-ready <file>`, `--parent-tare-kg` and `--manual-net-kg`. The operator's measurements are run parameters and are never invented.

**Preflight** refuses before any write on:
- API_READY_MISSING, MANUAL_NET_ROUTE_MISSING (OpenAPI of the target API), MARKING_POLICY_WEIGHTED_KG_MISSING;
- FIXTURE_TAG_COLLISION (`MT28…` in articles/pallets/orders/waves);
- PROTECTED_WAREHOUSE, WAREHOUSE_NOT_EMPTY (the new ID 230000000+ must be absent, with no stock/CASE/waves);
- TEMPLATE_ARTICLE_MISSING;
- missing or non-positive tare/NET;
- MEASUREMENTS_CHANGED_AFTER_START (a resume must keep the original values).

**Journal:** every API write step is stored in the state file (`runtime/test-evidence/tradecase/2026-10-28/T06/mixed-tree/mixed-tree.json`) **before** sending.
- A repeat sends exactly the same bytes; a completed step is not sent again.
- A different body under the same key → STEP_CONTENT_CHANGED.
- An unknown outcome (5xx/network) blocks all later steps until the same step is repeated.
- Native StockPosting calls are also stored with a fixed operation_id (`<tag>.<key>`).

**Stages:**
1. **FIXTURE** (ni042 pattern under `RRL_STOCK_CONFIG_API.begin_change`):
   - a new warehouse and cells (source, pick cells for KG/EA, CPT), pick faces, revision;
   - a KG article: copy of the template with TYPE_W=3, UNIT_TYPE=KG, KG→KG 1:1, receipt policy without marking/serialization;
   - an EA article: copy of the template with its conversions; a weighted template stops the run.
   - Shared physical stock is not touched.
2. **WAVE:**
   - lots via INVENTORY_REGISTER_LOT on the new warehouse;
   - one recipient, two orders (KG = the operator's NET; EA = 4) → plans → one wave → launch → TASK_COMPLETE → WAVE_PICK_RELEASE;
   - requires **exactly two different CASE tasks** (KG and EA), otherwise a stop;
   - tare: count + book for each, claim/start.
3. **PICK_KG_MANUAL_NET:**
   - `marking-policy.weighted_kg=true` is required;
   - POST `/weigh-line-manual` with the C0188 body: no fact_qty, no capture;
   - exact repeat: same result, events unchanged;
   - check the canonical metadata `measurement.origin=MANUAL_OPERATOR_ENTRY` without a capture, and PICKED_QTY = NET.
4. **PICK_EA:** the line is not weighted_kg and not marked → the regular `/confirm` with fact_qty → exact repeat.
5. **TREE:**
   - both carriers must be in one cell (a move is not invented, otherwise a stop);
   - `create` PALLET with the measured tare → `attach-case` KG → exact repeat;
   - refusals (403/409) with the parent composition unchanged: stale parent version, someone else's carrier scan, a changed body under the same operation, another cell (a second pallet in the source cell);
   - `attach-case` EA;
   - `tree_findings`: each CASE and STOCK leaf once, quantities = the picks, no quantity on containers, SSCC unchanged, one cell.
6. **TRANSPORT:** an explicit stop `TRANSPORT_NOT_WIRED`. Control/LOAD/DEPART and the store receipt need the trip/vehicle/document fixture of `live_nested_shipping.py`; per review item 3 the runner stops after the verified tree instead of expanding the fixture.

**Cleanup** (`cleanup`, ordered native reversals of what was created):
- `detach-case` → `CASE_CARRIER_RETURN` → `RESERVATION_RELEASE` → `tare/book-cancel` + zero count → `WAVE_EXECUTION_FINISH`/`WAVE_CANCEL` → `INVENTORY_COUNT` to zero;
- then a check that the warehouse has P=0/H=0, otherwise a stop `CLEANUP_LEFT_STOCK`.
- The empty tagged HU containers and history stay.

## Checks (commands)
- `python -m pytest -q -p no:cacheprovider tests/retailcase/test_c0190_mixed_tree_runner.py` → 32 passed:
  - preflight refusals (14 kinds);
  - the manual NET body only per the C0188 contract;
  - journal byte identity, blocking after unknown, repeat of the same step;
  - tree defects (6 kinds);
  - cleanup order;
  - send with an unknown outcome → retry with the same bytes;
  - unexpected status → stop; an expected 403/409 in negatives;
  - `plan` with no network; live modes without `--api` → refusal.
- `python scripts/c0190_mixed_tree_runner.py plan` → `plan.json`; `run` without `--api` → refusal
- `python scripts/retailcase_quality_gate.py` → PASS; `scripts/check-encoding.ps1` → PASS; `python scripts/check_architecture.py` → PASS

## Limitations
- **The runner has not been run against a live Oracle/API.** The live stages are built from proven patterns (ni042, bulk_case_pack, HU contracts, the real composition fields of the 22.10 run), but they are not verified on the target runtime. Every deviation stops with the exact code.
  - Unconfirmed assumptions: two orders give two separate CASEs; the EA unit code from the template's rows; attach-case of a picked CASE without a prior close/bind-shipment; tare availability fields.
- **Open:** TRANSPORT (control/LOAD/DEPART), the store receipt by the root SSCC, and the separately confirmed gross weight of the parent (`Measurements MANUAL_CONFIRMED` on HU move).
- **General confirm gap (root-owned, not changed):** `/confirm` accepts a client fact_qty for KG without provenance. The runner does not use it for KG; it uses it only for the EA line.

## Rework K-0217 (the same task; the three blockers fixed)
1. **Cleanup only for this run's state.**
   - Before `INVENTORY_COUNT`, `cleanup_scope_findings` checks the warehouse:
     - only UIDs from the fixture (the two registered lots) and the carrier lots of this run's CASEs (`RRL_CASE_CARRIER_LOT`, saved to the state before the return);
     - only the two run articles;
     - the remainder per article exactly equals what was registered (KG = 2×NET, EA = 8), counted only for lots actually posted in the journal;
     - 0 active reservations; no other CASEs on the warehouse and no open warehouse tasks.
   - Any deviation → `CLEANUP_SCOPE_REFUSED:<findings>`, and nothing is counted.
2. **Native StockPosting through the same journal.**
   - `post()` stores the full serialized command `{operation_id, command_type, actor, source, metadata}` under the key `native.<key>` **before** the call, and calls StockPosting with exactly the stored content.
   - Outcome: 200 posted; 409 confirmed refusal (code and reason recorded); 0 unknown (`RESULT_UNCERTAIN`/`REQUEST_DEADLINE`/… or oracle 20891–20893, or any exception without a code). An unknown outcome blocks every later step until the same command is repeated.
   - Content recomputed after re-reading the quantities under the same key → `STEP_CONTENT_CHANGED` before posting. Cleanup never reuses an operation_id with different content.
3. **Exact refusals and the composition after each one.**
   - Negative steps accept only 409 and check the expected rule in `detail.code` or `detail.reason`:
     - stale parent version → `HU_CONTENT_VERSION_CONFLICT`;
     - someone else's carrier scan → `HU_CASE_CARRIER_SCAN_REQUIRED`;
     - another cell → `HU_PACK_SAME_LOCATION_REQUIRED`;
     - changed body with the same operation → `OPERATION_CONTENT_CONFLICT`.
   - After **each** refusal the parent composition is re-read and must equal the composition before the refusals. An unrelated denial (ACCESS_DENIED, 403 Permission required, HU_CHILD_ALREADY_HAS_PARENT) → `UNEXPECTED_REFUSAL`.
- **New tests (+23):**
  - cleanup: accepts the run's lots and refuses another UID, another article, a remainder mismatch, an active reservation and other tasks;
  - native outcome classification;
  - the command is in the journal before posting; an unknown outcome blocks later steps; a retry is identical; a completed one is not repeated; changed content is refused before posting; a confirmed refusal is final;
  - each refusal by its expected code plus an unchanged composition; unrelated denials do not pass;
  - the TREE stage checks every negative by name.
- **Checks:** 55 passed; gate, encoding and architecture PASS. Store receipt and TRANSPORT unchanged (outside the runner, reported explicitly). Live modes not run; no Oracle writes.
