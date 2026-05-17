# WMS Terminal Web

Modern Web/PWA terminal client for the WMS/TMS terminal contour.

The app replaces the old terminal UI gradually. It does not connect to Oracle directly. All reads and writes go through `api/wms_api_server`.

## Run

From the repository root:

```bat
terminal.bat
```

Manual run:

```powershell
cd C:\projects\TMS\terminal\wms_terminal_web
$env:VITE_WMS_API_BASE_URL="http://127.0.0.1:8088"
npm install
npm run dev
```

Default URLs:

- terminal app: `http://127.0.0.1:3010`
- WMS API: `http://127.0.0.1:8088`

## Implemented MVP Surface

- Operator login through `GET /api/terminal/users/{user_id}` (`GET_RUSER` parity).
- Product lookup through `GET /api/products/by-barcode/{barcode}` (`GET_PRODUCT_INFO` parity).
- Pallet/lot lookup through `GET /api/lots/{usscc}/items` (`GET_LOT_ITEMS` parity).
- Confirm lot check through `POST /api/terminal/lots/{usscc}/check` (`LOT_CHECK_PASSED` parity).
- Place lookup through `GET /api/places/{place_id}/items` (`GET_PLACE_ITEMS` parity).
- Confirm place audit through `POST /api/terminal/place-checks` (`PLACE_CHECK_PASSED` parity).
- Production batch status lookup through `GET /api/production-batches/{id}/status`.
- Legacy payload console through `POST /api/legacy/tserver/execute`.
- API/Oracle diagnostics and local IndexedDB journal.

## Safety

Write operations require explicit confirmation in the UI. This is intentional because the local Oracle VM may contain the only working restored test schema.

No arbitrary `SPF_NAME` is exposed by the frontend. Compatibility with dynamic legacy calls remains inside the API server allowlist.

## Scanner Mode

The MVP expects scanner keyboard-wedge mode:

1. The scan field keeps focus.
2. A barcode or DataMatrix is entered as text.
3. Enter submits the scan.

For hardware integration, wrap this app with Capacitor and connect a vendor scanner SDK or Android intent bridge.

## Pallet Identifier / SSCC

The pallet scan field accepts both legacy WMS pallet identifiers and standard SSCC forms:

- `123456789012345678`
- `(00)123456789012345678`
- `00123456789012345678`
- `]C100123456789012345678`

GS1 AI `00` is normalized away before calling the API, so the server receives the 18-digit SSCC value.
