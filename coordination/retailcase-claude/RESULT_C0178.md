# C-0178 — T08: top-up is refused when pallet places or stacking are unconfirmed

Source criterion: revision27 «Товар не подходит для добивки». A product is excluded, with a reason, by mass, pallet places, dimensions and other criteria. Weight, volume and dimensions are already checked; this task closes the check of pallet places and stacking in fail-closed form.

## Data found (Oracle, read-only)
- Vehicle profile `floor_capacity.variants[].limits{pallet_type_id,max_places}` and the existing check `RRL_VEHICLE_PROFILE_API.check_floor_capacity(vehicle, counts, unknown)`, which returns `TARE_TYPE_UNCONFIRMED` when unknown>0.
- TRIP/ORDER (`TradeTrip`, `TradeTripLine`) carry no pallet type and no place count; only capacity_kg/m3.
- `RRL_CUSTOMER_PRODUCT_RULE`: 64 active rules, 0 with `PALLET_TYPE`, `PALLET_CASE_QTY` in 32. `ALLOW_TOP_STACKING` is not read by runtime or native code, so its meaning is not established.
- `RRL_ARTICULS.COUNT_IN_ROW×ROWS_IN_PAL`: no pallet type and no documented meaning. Not used, as the task requires.
- Conclusion: there is no authoritative product → pallet type / place count mapping and no vehicle stacking rule. There is no positive case, and none was invented.

## Change
- `api/wms_api_server/app/modules/integrations/infrastructure/trade_capacity.py`:
  - `floor_admission(cur, vehicle)` calls the existing profile check with the top-up places as type-unconfirmed (`[]`, 1), returns `floor_profile_status`, and always returns `TOPUP_PALLET_PLACE_MAPPING_REQUIRED`;
  - `capacity_context` returns `vehicle`;
  - `capacity_preview`: `maximum/fitting/remaining_boxes=null` with that reason. The weight/volume ceilings (`box_limit_*`) are shown unchanged. The reasons for after-load and `MIXED_PACKAGE_LAYOUT_REQUIRED` keep priority.
- `.../trade_topup.py`: `allocate` passes all the existing gates (horizon, forecast, recipient, expiry), then refuses with 409 `TOPUP_PALLET_PLACE_MAPPING_REQUIRED`. Because of that, `save` never reaches `RRL_TRADE_TOPUP_API.save`: no proposal, no hold, no order. Confirm is possible only for a saved proposal.
- Weight/volume/dimension formulas are unchanged. No native code, schema or UI changed.

## Checks
- **Offline** `tests/tradecase/test_trade_floor_capacity.py`, 9 passed:
  - call arguments of the profile check;
  - NOT_CONFIGURED/TARE_TYPE_UNCONFIRMED;
  - lower/upper boundaries (free 1000 kg/10 m³; 10 kg exactly 1 box; requested 5 of 1; zero capacity) are all refused;
  - the mixed layout keeps its reason;
  - top-up preview 409 after the gates;
  - save does not call save/HOLD.
- **Existing** capacity/topup tests: 82 passed.
- **Full** tests/tradecase: 381 passed, 1 environment error (PermissionError on `%TEMP%\pytest-of-roma` in test_api_audit_concurrency; tmp_path, unrelated).
- Quality gate PASS, encoding PASS, architecture PASS (cycles 0).
- **Live**, ASGI current code + real Oracle, warehouse 226192056 trip T1 (not protected); `tests/tradecase/live_trade_floor_capacity.py`:

| Call | Floor check bypassed (pre-C0178, comparison) | Real code |
|---|---|---|
| capacity sku A, 1 box | 200, reason null | 200, `TOPUP_PALLET_PLACE_MAPPING_REQUIRED`, fitting null, profile `TARE_TYPE_UNCONFIRMED` |
| capacity sku A, 100000 boxes | 200, reason null | 200, same reason |
| topup-preview N1 | 200, proposed_boxes 0 | 409 `TOPUP_PALLET_PLACE_MAPPING_REQUIRED` |
| topup-proposals save, new operation_id | — | 409, outcome_confirmed=true, retry_same_operation_id=false |
| other warehouse 999999001 | — | 409 `TRADE_CAPACITY_SOURCE_MISSING` |
| wrong password | — | 401 |

The bypass column is only an emulation for comparison: on T1 the box limits by weight/volume were already 0 (the trip is full).

Proposals/holds/active holds of the warehouse before = after: 1/3/0. Nothing was created, so no cleanup was needed.

## Timing
- Max HTTP 378 ms (first capacity call, cold); the rest ≤302 ms.
- `RRL_SQL_SLOW_LOG` since the run started: 0 entries. No indexes needed.

## Remaining (blocks T08 acceptance)
- Master data that must be agreed (values must not be invented):
  - product → pallet type (`pallet_type_id`) and boxes per place for that type;
  - whether places may be stacked in the vehicle (an explicit rule, not `ALLOW_TOP_STACKING` without a meaning);
  - places and types of the already planned TRIP lines.
- Once these exist, `floor_admission` passes counts by type to the same `check_floor_capacity`, and the positive and over-limit boundaries can be checked on an own fixture.
- The Codex 660→640 runner (210069361) will now get 409 on top-up preview/save; that is the intended fail-closed result. It was not run.
- Proposals saved before this change can still be confirmed by the native StockPosting (not changed; native code is outside the scope).
- Exact replay: a refused save stores nothing, so a repeat with the same operation_id gives the same 409. That was not run as a separate live call.
