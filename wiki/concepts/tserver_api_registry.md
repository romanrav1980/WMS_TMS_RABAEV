# Concept: Tserver Legacy API Registry

## Meaning

`Tserver` is the legacy API gateway for handheld warehouse terminals.

It accepts a custom TCP protocol, decodes `FUNC=...|key=value|...` messages, and either:

- handles a fixed legacy command in a C# `switch`;
- executes direct SQL against Oracle or Access MDB;
- calls an Oracle stored procedure dynamically through `CALL_SPF`.

The terminal client should therefore be treated as a legacy API consumer, and `Tserver` as the first source for the future API contract.

## Protocol Shape

The protocol is a UTF-16 TCP payload with a fixed-width length prefix and a key/value body:

```text
00000000000000000123FUNC=GET_RUSER|USERID=123|
```

The same payload can contain several `FUNC` blocks. This is used for batched audit/check responses, such as a header command followed by many error lines.

Primary code points:

- [`Program.cs`](../../MINI%20WMS/Tserver/Tserver/Program.cs): `funct.split_program`, `funct.encode`, TCP listener, command dispatch.
- [`Program.cs`](../../MINI%20WMS/CS_CATClient/Program.cs): terminal-side `Client.Receive`, request encoding, and response decoding.
- [`FormMain.cs`](../../MINI%20WMS/CS_CATClient/FormMain.cs): terminal workflows that send legacy commands.

## Fixed Legacy Commands

| Legacy `FUNC` | Current role | Main request fields | Response blocks | Database work | Candidate modern endpoint |
| --- | --- | --- | --- | --- | --- |
| `PLACE_CHECK_PASSED` | Confirms cell/pallet-place audit result. | `PALLETID`; child blocks `ERROR_PALLET_CHECK_LINE`, `INVENTORY_LINE_PALLET_AUDIT`. | `END_PALLET_CHECK_PASSED`, `FAULT`. | Deletes/inserts `RABAEV.PLACE_AUDIT`, `RABAEV.PLACE_AUDIT_ERROR_LINES`, `RABAEV.INVENTORY_LINE_PALLET_AUDIT`. | `POST /api/terminal/place-checks` |
| `ORDER_CHECK_PASSED` | Confirms order/invoice checking result. | `ORDER`; child blocks `ERROR_LOT_LINE`. | `END_ORDER_CHECK_PASSED`, `FAULT`. | Deletes/inserts `RABAEV.ORDER_AUDIT`, `RABAEV.ORDER_AUDIT_ERROR_LINES`; updates Access route/order status. | `POST /api/terminal/order-checks` |
| `VP` | Child detail block with checked item time. | `PALLET_UID`, `УИД`, `TIME`. | No standalone response. | Used inside `LOT_CHECK_PASSED` to update `RABAEV.RRL_SBORKA_PALLET_ROWS.TIME_OF_CHECKING`. | Child record in `POST /api/terminal/lots/{usscc}/check` |
| `LOT_CHECK_PASSED` | Confirms lot/pallet assembly check. | `USSCC`, `USER_ID`, `error_count`; child blocks `ERROR_LOT_LINE`, `VP`. | `END_LOT_CHECK_PASSED`, `FAULT`. | Deletes/inserts `LOT_AUDIT`; updates `RABAEV.RRL_SBORKA_PALLET_ROWS`; calls `RABAEV.RRL_SET_SCAN_PROOVE2` when no errors. | `POST /api/terminal/lots/{usscc}/check` |
| `GET_PRODUCT_INFO` | Finds product and package info by barcode. | `ШТРИХКОД`. | `END_GET_PRODUCT_INFO`, `FAULT`. | Reads `refstock.TB_LCUMS`, `refstock.TB_EUMS`, `refstock.TB_ART`, `RABAEV.SFERA_EAN`. | `GET /api/products/by-barcode/{barcode}` |
| `UPDATE_PRODUCT_INFO` | Updates product packaging/barcode facts. | `ШТВБЛ`, `БЛВКОР`, `ШК_ШТУКИ`, `ШК_БЛОКА`, `ШК_КОРОБ`, `УИД`. | `FAULT` only on error; success response is implicit/empty. | Updates `RABAEV.RRL_ARTICULS`. Commented code suggests older intended updates to `RABAEV.SFERA_EAN`. | `PATCH /api/products/{uid}/packaging` |
| `GET_LOT_ITEMS` | Returns lines for a WMS assembly pallet/lot. | `USSCC`. | `LOT_LINES`, many `LOT_LINE`, many `ALT_SHT`, `END`, `FAULT`. | Reads `RRL_SBORKA_PALLETS`, `RRL_SBORKA_PALLET_ROWS`, `RRL_ARTICULS`, `RRL_ARTICUL_MODS`. | `GET /api/lots/{usscc}/items` |
| `GET_ORDER_ITEMS` | Resolves order by lot and returns order lines. | `USSCC`. | `LOT_LINES`, many `LOT_LINE`, many `ALT_SHT`, `END`, `FAULT`. | Reads `refstock.tb_ecde`, `refstock.TB_LPREP`, `refstock.TB_LCDE`, `refstock.tb_art`, `RABAEV.SFERA_EAN`; calls `RABAEV.RRL_sfera_ean_EAN_*` functions in SQL. | `GET /api/orders/by-lot/{usscc}/items` |
| `GET_PLACE_ITEMS` | Returns stock lines in a warehouse cell/place. | `PLACEID`. | `PLACE_LINES`, many `PL`, many `ALT_SHT`, `END`, `FAULT`. | Reads current stock from `refstock.*` plus barcode/package data from `RABAEV.SFERA_EAN`. | `GET /api/places/{placeId}/items` |
| `GET_PROLET_ITEMS` | Returns stock by rack span and rack number. | `PROLET`, `STELLAJ`. | `PROLET_LINES`, many `PRLL`, `END`, `FAULT`. | Reads `refstock.*` stock, rack, article, and expiry data. | `GET /api/racks/{stellaj}/spans/{prolet}/items` |
| `GET_ORDER_INFO2` | Resolves order info by lot/USSCC. | `USSCC`. | `ORDER_POSITION_INFO`, `FAULT`. | Resolves order in Oracle `refstock.*`, then reads route/order facts from Access MDB. | `GET /api/orders/by-lot/{usscc}` |
| `SET_RUSER` | Assigns picker/user to order or lot. | `USSCC`, `USERID`, `ORDER_UID`. | `FAULT` only on error. | Reads `RABAEV.RUSERS`; updates `REFSTOCK.TB_LPREP.LP_CODPRE`; updates Access order row when `ORDER_UID` is present. | `PUT /api/orders/{orderUid}/picker` and `PUT /api/lots/{usscc}/picker` |
| `SET_TZONE` | Sets actual shipping/transport zone for an order. | `USSCC`, `USERID`, `ORDER_UID`, `TZONE`. | `FAULT` only on error. | Reads `RABAEV.RUSERS`; inserts `RABAEV.ORDER_MOV_HIST`; updates Access actual zone and user. | `PUT /api/orders/{orderUid}/zone` |
| `GET_ORDER_INFO1` | Returns order route/status info by order UID. | `ORDER_UID`. | `ORDER_POSITION_INFO`, `FAULT`. | Reads Access MDB route/order tables. | `GET /api/orders/{orderUid}` |
| `GET_RUSER` | Returns terminal user and permissions. | `USERID`. | `USER_INFO`, `FAULT`. | Reads `RABAEV.RUSERS`. | `GET /api/users/{userId}` |
| `CALL_SPF` | Generic dynamic Oracle stored procedure call. | `SPF_NAME`; arbitrary parameters. | `CALL_SP_INFO`, `FAULT`. | Executes the supplied stored procedure name as `CommandType.StoredProcedure`; every request key except `SPF_NAME` becomes a string parameter; return value is `ok`. | Replace with explicit endpoints. Temporary compatibility only: `POST /api/legacy/call-spf/{operation}` with allowlist. |

## Dynamic `CALL_SPF` Procedures Observed In Terminal Client

These are the concrete procedure calls currently emitted by `CS_CATClient`.

| Stored procedure | Terminal context | Parameters observed | Candidate modern endpoint |
| --- | --- | --- | --- |
| `RABAEV.RRL_GIVE_DESTINATION_CELL2` | Forklift/pallet placement: find destination cell for pallet. | `pallet_uid`, `ware_id1`. | `GET /api/forklift/pallets/{palletUid}/destination?warehouseId=...` |
| `RABAEV.RRL_GIVE_POPOLNENIE2` | Forklift/replenishment: what to place into a picking cell. | `PIKING_CELL`, `ware_id1`. | `GET /api/forklift/cells/{cell}/replenishment?warehouseId=...` |
| `RABAEV.RRL_GET_PAL_INFOTEXT` | Shipping: get text info for scanned pallet. | `PALLET_UID1`. | `GET /api/pallets/{palletUid}/info-text` |
| `RABAEV.RRL_INTERNAL_MOVE3` | Internal pallet movement. | `pallet_id`, `cell_to`, `count1`, `user_id1`. | `POST /api/internal-moves` |
| `RABAEV.RRL_INV_CREATE_LINE4` | Initial inventory: create inventory line. | `cell1`, `shk_art`, `articul_part`, `count1`, `UID_DOC`, `expiury_date`. | `POST /api/inventory/documents/{uidDoc}/lines` |
| `RABAEV.RRL_GIVE_NEXT_CELL` | Inventory navigation: next cell. | `cell1`. | `GET /api/cells/{cell}/next` |
| `RABAEV.RRL_GIVE_PREVIOUS_CELL` | Inventory navigation: previous cell. | `cell1`. | `GET /api/cells/{cell}/previous` |
| `RABAEV.RRL_SET_SBORKA_ZONE` | Set assembly/shipping zone for pallet. | `PALLET_UID1`, `ZONE1`, `user_id1`. | `PUT /api/pallets/{palletUid}/assembly-zone` |
| `RABAEV.RRL_GIVE_KARSH_STAT_INFO` | Forklift operator statistics/info. | `user_ud1`. | `GET /api/forklift/users/{userId}/stats` |
| `RABAEV.RRL_REVIZION_CELL_KOR` | Cell revision by carton count. | `CELL1`, `count_kor2`, `user_id1`. | `POST /api/inventory/cell-revisions` |
| `compl.sborka_full_pall_pick3` | Full-pallet picking. | `sb_pall_uid_coded`, `hran_pall_uid1`, `cell1`, `user_id1`, `pall_weight`. | `POST /api/picking/full-pallet` |

## Risk Notes

- `CALL_SPF` is the highest-risk part because the client supplies the stored procedure name.
- Direct SQL is built through string concatenation in several write paths.
- Some API commands mutate both Oracle and Access MDB, so the future API must define clear transaction and recovery behavior.
- Success responses are inconsistent: some commands return explicit `END_*`, while some write commands return nothing unless an error occurs.
- Several fields use Russian names in the wire protocol; the modern API should use stable English JSON names while retaining a legacy adapter.

## Migration Rule

Do not expose a generic public API endpoint that accepts arbitrary procedure names.

During migration, keep `CALL_SPF` only behind an allowlisted compatibility adapter. Every procedure listed above should become an explicit domain operation with typed input, validation, logging, and idempotency.

## Primary Sources

- [`../../MINI WMS/Tserver/Tserver/Program.cs`](../../MINI%20WMS/Tserver/Tserver/Program.cs)
- [`../../MINI WMS/CS_CATClient/Program.cs`](../../MINI%20WMS/CS_CATClient/Program.cs)
- [`../../MINI WMS/CS_CATClient/FormMain.cs`](../../MINI%20WMS/CS_CATClient/FormMain.cs)
- [`../../MINI WMS/CS_CATClient/FormMain.Designer.cs`](../../MINI%20WMS/CS_CATClient/FormMain.Designer.cs)
