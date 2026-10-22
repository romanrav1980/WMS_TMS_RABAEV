# C-0152 → root: candidate for RRL_TRADE_STOCK_GUARD (not applied, not part of the yard/quality migration)

Purpose: an active quality hold (existing `RRL_QUALITY_HOLD`, created by `RRL_TRADE_QUALITY_CASE_API` on OPEN and released on decision RELEASED) blocks every standard stock path for the pallet natively, not only in the exceptions screen.

## What already blocks natively (read live, `C0152/scripts/hold_shape_live.py`)
Stock in a quarantine cell (`RRL_CELLS.BLOCKED_FOR_REMAINS=1`) is excluded from allocation and execution by the existing owners: RRL_STOCK_ELIGIBILITY, RRL_STOCK_WAVE_CMD (1014, 1070), RRL_PICKING_API (320), RRL_PICK_RANGE_APPLY_CORE, RRL_STOCK_SHIPPING_CORE (108, 168), RRL_STOCK_MES_SUPPLY_CMD, RRL_STOCK_FULLPAL_BIND_CMD, RRL_STOCK_HU_SLOT (`LOCATION_BLOCKED`), RRL_ST_DEFER_WAIT_CORE.

## Gap
Moving the pallet **out** of the quarantine cell while a case is OPEN / DEFECT / WAITING_POSTING: `MOVE_QUARANTINE` (and `INTERNAL_MOVE` / `MANUAL_MOVE` / `COMPAT_MANUAL_MOVE` / `HU_*` from a blocked source) only check the cell flags. The exceptions screen checks `assert_release` in a separate READ ONLY transaction before posting — that is an interface pre-check, not a native block.

## Exact insertion
`RRL_TRADE_STOCK_GUARD.assert_command_stock(p_uid, p_request, p_actor)` — immediately after the `bulk_box_scan` block and **before** `for w in(select distinct c.WARE_ID ...)`:

```sql
  -- C-0152: an active quality hold blocks every stock command on the pallet except counting it.
  if command_kind not in('INVENTORY_COUNT','INVENTORY_REGISTER_LOT')then
   select count(*)into n from RRL_QUALITY_HOLD where ENTITY_TYPE='PALLET'and ENTITY_ID=p_uid and HOLD_STATUS='ACTIVE';
   if n>0 then fail('QUALITY_HOLD_ACTIVE');end if;
  end if;
```

(`n` and `fail` already exist in the procedure; `fail` raises -20911, a confirmed refusal.)

## Application points to verify
`assert_command_stock` is reached from RRL_STOCK_POSTING_API compile for each affected pallet; please confirm on the current body that it runs for: MOVE_QUARANTINE, INTERNAL_MOVE, MANUAL_MOVE, COMPAT_MANUAL_MOVE, HU_ATTACH/HU_DETACH/HU_MOVE/HU_PLAN_MOVE/HU_RELOCATE_SLOT/HU_REPACK_SLOT/HU_UNPACK, RESERVATION_*, WAVE_LAUNCH/WAVE_RESERVE_SOURCES/WAVE_PICK_RELEASE, CASE_PICK_CONFIRM, PICK_PALLET_BIND_SHIPMENT, OUTGOING_PALLET_CHECK, LOAD_SHIPMENT/SHIP_PALLET/SHIP_DOCUMENT/HU_SHIP, TRADE_TOPUP_CONFIRM. Commands that do not pass through it are not covered by this insertion.

## Native write-off
There is no goods write-off command in RRL_STOCK_POSTING_API (only TARE_WRITE_OFF). An approved case therefore stays `WAITING_POSTING` with `posting_status=WAITING_NATIVE_POSTING`; the posting owner (new posting kind writing off the frozen unit keys + outgoing document in the same transaction) is a stock-core change for root.
