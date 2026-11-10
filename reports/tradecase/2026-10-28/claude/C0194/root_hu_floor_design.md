# C0194: physical pallet type for a root HU (strategic analysis)

Analysis only. Nothing here is implemented, accepted or run against live Oracle. All statements below come from repository sources, with file and line references, as of 28.10.

## 1. Conclusion

**Do not extend the pallet-floor endpoint to CONTAINER roots.** The supported fact that the physical pallet type exists for a CONTAINER root is already in place: a `HELD` row in `RRL_TARE_BOOK` with `PLACE_KIND='HU'`, `PLACE_ID=<root uid>`. Loading already reads exactly that row.

The smallest design is to make the existing `TARE_BOOK` (place_kind `HU`) the operator's "confirm the physical pallet type" step. It needs three additive optional checks: a root version, a root scan and a cell scan. It also needs one read hint, so that the pallet-floor screen sends a CONTAINER root to this step instead of failing.

- No DDL.
- No new table.
- No change to loading, QC or the STOCK pallet-floor path.

## 2. Current contracts (facts)

| Area | STOCK carrier (works today) | CONTAINER root (the live mixed root) |
|---|---|---|
| Type fact | `RRL_PALLET_FLOOR_TYPE(UID_PALLET, PALLET_TYPE_ID, TYPE_VERSION, LAST_OPERATION_ID, DECLARED_WARE_ID)` (`db/migrations/2026-10-14_ni022_stock_floor_type/001_schema.sql`) | `RRL_TARE_BOOK` HELD, `PLACE_KIND='HU'` |
| Write command | `PALLET_FLOOR_TYPE_CONFIRM` → `RRL_STOCK_PALLET_TYPE_CMD` (`003_command.sql`) | `TARE_BOOK` → `RRL_STOCK_TARE_BOOK_CMD` (`db/releases/2026-10-14/53_package_bodies.sql:24686-24800`) |
| API | `GET/POST /api/inventory/pallet-floor-types` (`modules/inventory/api/pallet_floor_routes.py`), login + native scope | `POST /api/inventory/tare/book` (`modules/inventory/api/tare_assembly_routes.py:43`), `require_permission("tare_plan")`; the model already requires `pallet_type_id` for `HU` ("Container requires actual pallet type") |
| How loading reads it | `RRL_STOCK_LOAD_FLOOR.compile_load`, STOCK branch → `TYPE_ORIGIN='ROOT_STOCK_TYPE'` | the same `compile_load`, CONTAINER branch: exactly one HELD `RRL_TARE_BOOK` for `PLACE_KIND='HU' and PLACE_ID=root and OWNER_WARE_ID=ware`, else `LOAD_FLOOR_SINGLE_HELD_HU_TARE_REQUIRED` → `TYPE_ORIGIN='HELD_HU_TARE_BOOK'` (`db/migrations/2026-10-26_carton_trip_bounds/004_body.sql:29-34`) |

**Why the floor endpoint refuses the root.** `RRL_PALLET_FLOOR_READ.describe_type` requires `HU_KIND='STOCK'` (`PALLET_FLOOR_STOCK_CARRIER_REQUIRED`). It derives the warehouse from `RRL_REMAINS` of the uid, which a CONTAINER does not have (`db/migrations/2026-10-22_pallet_floor_scopes/001_read.sql`). This rule is correct. If the root were written into `RRL_PALLET_FLOOR_TYPE`, loading would still ignore the row, because the CONTAINER branch reads the tare book. That would create a second, unread source of truth.

The C0191 runner (Codex-owned, `scripts/c0191_mixed_tree_transport.py:313-331`) already calls both `pallet-floor-types` (which fails for CONTAINER) and `tare/book place_kind=HU` (the step loading needs). For a CONTAINER root the floor call is redundant.

## 3. Proposed design (smallest supported)

### 3.1 Where warehouse and cell come from
These are already in `TARE_BOOK` describe for `HU`/CONTAINER:
- the root row is read from `RRL_PALLETS`, and its kind must be `HU_KIND='CONTAINER'`;
- `HU_TYPE in ('PALLET','ROLL_CAGE')` and `HU_CURRENT_CELL is not null`, else `TARE_RETURNABLE_CURRENT_CONTAINER_REQUIRED`;
- the cell is `HU_CURRENT_CELL`, and the warehouse is `RRL_CELLS.WARE_ID` of that cell;
- the actor's warehouse right is checked by `RRL_TARE_PARTICIPANT.warehouse_actor(actor, ware)` plus `tare_plan`;
- the optional `expected_warehouse_id` must match, else `TARE_PLACE_SELECTED_WAREHOUSE_CONFLICT`.

Nothing new is needed here.

### 3.2 Root version and scan checks (the only command change)
Add optional metadata to `TARE_BOOK`, accepted only when `place_kind='HU'`. When a field is present, `RRL_STOCK_TARE_BOOK_CMD.describe_command` checks it:

| Field | Check | New refusal |
|---|---|---|
| `expected_root_version` (int ≥0) | `= RRL_PALLETS.HU_CONTENT_VERSION` | `TARE_ROOT_VERSION_CHANGED` |
| `scan_place` | `= root uid` or `= RRL_PALLETS.SSCC` | `TARE_ROOT_SCAN_REQUIRED` |
| `scan_cell` | `= HU_CURRENT_CELL` | `TARE_ROOT_CELL_SCAN_REQUIRED` |

**Same pattern as the floor command.** These are the checks `RRL_STOCK_PALLET_TYPE_CMD.snapshot` makes for STOCK (scan uid/SSCC, scan cell, version).

**Why additive and optional:**
- Old canonical retries keep their request hash, as in `warehouse_hu_routes.py:79-82` ("New optional fields must not alter canonical retries").
- The screen always sends all three fields.
- Root may later make them mandatory for new operations with a cutoff, which is a separate decision.

**Race protection after the check already exists.** describe output includes `content_version`, and `execute_command` locks `RRL_PALLETS FOR UPDATE`, re-describes and compares (`CLOSURE_CHANGED: tare assembly`).

### 3.3 Idempotency
No change:
- The standard posting-root operation journal applies: `OP` anchor on `operation_id` and the `STOCK.OUTBOX` unique anchor, as in `compile_command`.
- An exact repeat returns the stored result.
- The same `operation_id` with a different body gives `OPERATION_CONFLICT`. The API reports `outcome_confirmed=false` with the original `operation_id` kept, the existing tradecase floor/bind/load rule (`wiki/database/tradecase_pallet_floor_scope_20261022.md`).
- `TARE_PLACE_ALREADY_BOOKED` stops a second, different booking for the same root.

### 3.4 How the type is stored
The existing `RRL_TARE_BOOK(OPERATION_ID, BALANCE_KEY, OWNER_WARE_ID, PALLET_TYPE_ID, PLACE_KIND='HU', PLACE_ID=root, CREATED_BY, STATUS='HELD')`, plus one unit fewer available on the GOOD balance of that warehouse and type.

**Physical meaning:** one returnable pallet asset of this type is now under this root. That is the fact loading and tare custody need.

**Type/class guard already in place:**
- `HU_TYPE='PALLET'` requires `LOAD_UNIT_CLASS='PALLET'`;
- `ROLL_CAGE` requires `TROLLEY`;
- otherwise `TARE_CONTAINER_PHYSICAL_TYPE_CONFLICT`.

### 3.5 How loading reads it
No change. `compile_load` CONTAINER branch → one HELD HU book → `pallet_type_id`, `TYPE_ORIGIN='HELD_HU_TARE_BOOK'`, `source_reference=<booking operation>`. `assert_load` re-derives this at load time and refuses a changed book (`CLOSURE_CHANGED: load top type/profile`). The floor check runs only when the vehicle has a READY floor profile (`current_matrix` not null).

### 3.6 Read hint for the screen (optional, read-only)
Change `RRL_PALLET_FLOOR_READ.describe_type` so that a CONTAINER root does not raise `PALLET_FLOOR_STOCK_CARRIER_REQUIRED` but returns:

`{kind:'CONTAINER', status:'USE_HU_TARE_BOOK', uid, sscc, cell:HU_CURRENT_CELL, version:HU_CONTENT_VERSION, warehouse, hu_type, tare_booking:{operation_id, pallet_type_id}|null}`

The same scope check still runs: warehouse from the cell, not `RRL_REMAINS`. One "Physical pallet type" screen then serves both kinds and posts to the right command. If root prefers not to touch the read package, the UI can read `GET /api/warehouse-hus/composition` and route by `kind` instead, so this step can be dropped.

### 3.7 Refusals (operator-visible)
Existing `TARE_BOOK` codes that apply:
- `TARE_RETURNABLE_CURRENT_CONTAINER_REQUIRED`: not PALLET/ROLL_CAGE, or no current cell;
- `TARE_BOOK_TOP_PLACE_REQUIRED`: the root is itself nested;
- `TARE_BOOK_PLACE_ALREADY_ON_VEHICLE`: there is a LOADED/DEPARTED load fact;
- `TARE_NESTED_PLACE_ALREADY_BOOKED`: a HELD book on any nested HU or CASE child;
- `TARE_PLACE_ALREADY_BOOKED`;
- `TARE_GOOD_WAREHOUSE_AVAILABILITY_REQUIRED`;
- `TARE_CONTAINER_PHYSICAL_TYPE_CONFLICT`;
- `TARE_ACTIVE_EXISTING_PALLET_TYPE_REQUIRED`;
- `TARE_PLACE_SELECTED_WAREHOUSE_CONFLICT`;
- `TARE_ASSEMBLY_PLANNING_PERMISSION_REQUIRED` (403);
- `TARE_EXISTING_PLACE_OR_GOOD_COUNT_REQUIRED`.

New codes: the three in 3.2.

### 3.8 Compatibility
- **Unchanged:**
  - STOCK pallet-floor path, `RRL_PALLET_FLOOR_TYPE`, CASE_TYPE origin;
  - loading/departure (`RRL_STOCK_LOAD_FLOOR`), `TARE_BOOK_CANCEL`;
  - the `HU_ATTACH` retained-book flow;
  - existing callers of `/tare/book`, because the new fields are optional.
- **No DDL:** the `RRL_TT_LOAD_FLOOR_FACT.TYPE_ORIGIN` constraint already includes `HELD_HU_TARE_BOOK`.
- **API change:**
  - `Book` model gets three optional fields;
  - a validator rejects them when `place_kind='CASE'`;
  - existing error mapping applies.

### 3.9 Packages and routes to extend
1. `RRL_STOCK_TARE_BOOK_CMD.describe_command`: the three optional checks for `HU`. The fields must also be placed into `p_domain`, so that `execute_command`'s re-describe compares them.
2. `modules/inventory/api/tare_assembly_routes.py` `Book`: optional `expected_root_version`, `scan_place`, `scan_cell`.
3. Optional: `RRL_PALLET_FLOOR_READ.describe_type`, the CONTAINER read hint (3.6).
4. UI: the existing "Physical pallet type" form in СНС/BLC routes a CONTAINER root to `/tare/book` with the scans.

Not to extend: `RRL_STOCK_PALLET_TYPE_CMD`, `RRL_PALLET_FLOOR_TYPE`, `RRL_STOCK_LOAD_FLOOR`.

## 4. Preconditions and risks for the live mixed root (verify read-only before use)
1. **The root's `HU_TYPE` must be `PALLET` or `ROLL_CAGE`.** A `BOX` root has no returnable tare, so the type cannot be booked. Loading then refuses with `LOAD_FLOOR_SINGLE_HELD_HU_TARE_REQUIRED` whenever the vehicle has a floor profile. That case needs an owner rule and is out of this smallest design.
2. **CASE children holding their own HELD `CASE` tare books** (the C0190 runner books tare per CASE: `scripts/c0190_mixed_tree_runner.py:709`; `HU_ATTACH` can retain them) block the root book with `TARE_NESTED_PLACE_ALREADY_BOOKED`. The operator or flow must first cancel the children's books where the cartons carry no returnable pallet; that cancel is allowed only while a CASE is physically unused. Otherwise this is a genuine double booking, so the refusal is correct. Root should decide the order of steps; this design does not auto-cancel.
3. **Correcting a wrong type after the root is built:** `TARE_BOOK_CANCEL` for `HU` requires an empty container (`TARE_BOOK_EMPTY_PLACE_REQUIRED` while active child links exist). A wrong confirmation therefore needs unpacking. The scans and catalog choice reduce the risk. An atomic "retype HU book" command would be a separate, later decision.
4. **Rights:** the step needs `tare_plan` plus a tare warehouse participant. The floor screen used shipping scope (`stock_posting_shipping` / `RRL_ACCESS_API`). Root should confirm that the floor operator role has `tare_plan` on the warehouse, or decide whether the HU-book scope should also accept the floor scope (a separate access change).
5. **Availability:** the warehouse GOOD balance of the chosen type must be ≥1. C0191 inflated it with a synthetic `TARE_COUNT`. Live operations need a real count.

## 5. Not claimed
No code, test, Oracle or API change was made. The design and the new refusal codes are proposals for root/Codex to decide on and implement.
