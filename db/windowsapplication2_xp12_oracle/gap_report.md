# WindowsApplication2 xp12 vs Oracle schema gap report

## Scope
Static check of desktop app `MINI WMS\WindowsApplication2\WindowsApplication2` against:
- `create_schema.sql`
- `01_tables.sql`
- `02_sequences.sql`
- `03_functions.sql`
- `04_procedures.sql`
- `05_gap_patch.sql`
- `06_transport_task_missing_impl.sql`

## Closed by schema patches
These app dependencies are now covered by the schema bundle:
- `RRL_CONSTANTS` table with columns used by the app: `NAME`, `VALUE`
- `RRL_OBJECT` table with columns used by the app: `OBJECT_NAME`, `BUSINESS_FIELD`, `PARENT_OBJECT`, `COMMENT1`, `TYPE1`, `ARTICLE1`
- `RRL_WARE_MASKS` table with columns used by the app: `WARE_MASK`, `ORD_ID`
- `RRL_TRANPORT_TASK_HISTORY_ADD`
- `RRL_AUTH3`
- package `pk_pivot` with `PivotSQL`
- package `REVIZION` with members used by the desktop app
- package `TRANSPORT_TASK` with members used by the desktop app, including:
  - `PRINT_PALLET_WEIGHT`
  - `CAN_PRINT`
  - `PALLET_COUNT`
  - `TT_WARES`
  - `STOIM_TT`
  - `TT_UNREADY_COUNT`
  - `TT_UNREADY_WARES`
  - `TT_VODITEL_TEL`
  - `TT_REORDER_ADR`
  - `RRL_PALLETS_STR`
  - `RRL_TT_PALLETS_STR`
  - `TT_TIME_OF_OTG`
  - `SERVICE_LEVEL_OTG`
  - `VODITEL_GET_INN`
  - `VODITEL_GET_TABEL_NUMB`
  - `VODITEL_SET_TABEL_NUMB`
- route history storage: `RRL_TRANSPORT_TASK_HISTORY`, `RRL_TRANSPORT_TASK_HISTORY_SQ`
- driver extension storage: `RRL_TR_VODITEL_EXT`
- trigger `RRL_OBJECT_TRG`

## Residual gap in RABAEV
No unresolved function/procedure/table gaps remain from the reviewed desktop-app contract for the selected `RABAEV` schema line.

## External dependency not covered by create_schema.sql
The desktop app still directly uses the external schema `SUPERMAG` in many places. `create_schema.sql` does not create it and does not grant cross-schema access. This remains the main runtime dependency outside `RABAEV`.

Examples:
- `Form1.cs`: `SUPERMAG.SMCARD`, `SUPERMAG.SMSPEC`, `SUPERMAG.SMDOCUMENTS`, `SUPERMAG.SMCLIENTINFO`, `SUPERMAG.SMSTOREUNITS`, `SUPERMAG.SMCOMMONBASES`, `SUPERMAG.MON_WMS_STBYPALL`, `SUPERMAG.FILL_MON_WMS_STBYPALL`
- `СверкаЦен.cs`: `SUPERMAG.SMDOCUMENTS`, `SUPERMAG.SMSPEC`, `SUPERMAG.SMCARD`, `SUPERMAG.SMCLIENTINFO`

## Result
For the reviewed desktop-side contract, the schema bundle now covers the previously missing `RABAEV` objects and transport-task APIs. Remaining risk is concentrated in:
- runtime semantics of the new implementations until they are exercised on a real Oracle instance with production-like data
- the external `SUPERMAG` schema and its privileges/data

## Live Oracle VM re-check (2026-03-26)
The schema bundle was applied to the Oracle VM and the desktop-app contract was re-checked against the live `RABAEV` schema.

Covered on the live app surface:
- package `ARTICULS`: `EI`, `UPDATE_MOD`, `EVENT_ON_CHANGE_PICKING_CELL`, `EANS`
- package `COMPL`: `SHOW_SQ`, `SHOW_SQ_GR`, `PATH`, `RRL_GIVE_PALLET_UID`, `RRL_COPY_PALLET_ROW3`, `SET_SBORSHIK`, `RRL_SBORKA_PAL_REMOVE_EMPTY`, `PALLET_COMPL_DATE`, `CREATE_ORDER_FROM_SPALLETS`, `ORDERS_START_PLAN`, `TRUNCATE_ORDER_BY_REMAINS`, `ORDERS_CREATE_VYCHERK`, `ORDERS_CHECK`, `RESET_2_FIRST_STATUS`, `ORDER_VYCHERK_COUNT`, `ORDER_ROWS_COUNT`, `DEBUG_TRUNCATE_REM`, `DEBUG_TRUNCATE_RESERV`, `DEBUG_TRUNCATE_ORDERS`, `TIME_SHIFT_START`, `TIME_SHIFT_END`
- package `ORDERS`: `DELETE_PALLETS`, `CLEANUP_ORDER2`, `CREATE_ORDER`, `ADD_ORDER_ROW`, `CONTAINS_INVALID_LOGO`, `WARES_OF_ORDER`, `COUNT_OF_SQ_GR`, `GET_UNFINISHED_QUANTITY`, `GET_UNFINISHED_QUANTITYO`
- package `CROSS_DOCKING`: `SYNC_SBORKA_PALL`, `SYNC_ARTICUL`, `SYNC_MOD`, `SYNC_SBOR_PALL_ROW`
- standalone function `RRL_DELETE_OP2`
- direct tables used by the desktop app: `RRL_TT_GLOBAL_MESS`, `RRL_TYPE_PALL`, `RRL_TOVARO_NOSITEL`, `RRL_COMPL_RESERVE`
- structural gaps closed in live tables:
  - `RRL_ORDERS`: `COND`, `ORD1`
  - `RRL_ORDER_ROWS`: `MOD_ID`, `QUANTITY_PLANNED`, `PARTIONPLANNED`
  - `RRL_ARTICUL_MODS`: `SHK_SHT`, `SHK_KOR`, `DIMK_X`, `DIMK_Y`, `DIMK_Z`, `BRT_WEIGHT_OF_KOR`
  - `RRL_ARTICULS`: `UUZ`

Live result:
- targeted app-surface invalid objects: `0`
- the reviewed desktop-side Oracle contract is now covered on the live VM for the checked `RABAEV` surface

Residual risks after the live re-check:
- the VM still has unrelated invalid legacy objects outside the reviewed desktop-app surface
- `SUPERMAG` remains an external runtime dependency and still requires realistic data and privileges
- semantic correctness of planning/reserve flows should still be exercised from the desktop UI with test data
