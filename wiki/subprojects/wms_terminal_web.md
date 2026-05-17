# Subproject: WMS Terminal Web/PWA

## Role

`terminal/wms_terminal_web` is the modern terminal client that begins replacing the legacy Windows CE / old terminal OS contour.

The application is designed to run in two modes:

- Android terminal or rugged scanner browser/PWA;
- ordinary desktop browser for debugging, training, and fallback operations.

## Current Implementation

Implemented on 2026-05-17:

- React + TypeScript + Vite application.
- Ant Design based operator UI.
- PWA manifest and service worker shell.
- Local IndexedDB operation journal.
- Root launcher [`../../terminal.bat`](../../terminal.bat), port `3010`.
- API base URL through `VITE_WMS_API_BASE_URL` / `REACT_APP_API_BASE_URL`, defaulting to `http://127.0.0.1:8088`.

Implemented screens:

- operator login through `GET_RUSER` parity endpoint;
- product lookup through `GET_PRODUCT_INFO` parity endpoint;
- pallet/lot lookup through `GET_LOT_ITEMS`;
- explicit lot confirmation through `LOT_CHECK_PASSED` compatibility endpoint;
- place lookup through `GET_PLACE_ITEMS`;
- explicit place confirmation through `PLACE_CHECK_PASSED` compatibility endpoint;
- production batch status lookup;
- legacy `FUNC=...|` console;
- diagnostics for API, Oracle, and local journal.

## Boundaries

- The terminal app must not connect directly to Oracle.
- The terminal app must not expose arbitrary `SPF_NAME`.
- Write operations must require explicit user confirmation in the UI.
- Scanner MVP assumes keyboard-wedge mode.
- The pallet identifier field accepts legacy WMS IDs and standard SSCC scans. GS1 AI `00` forms such as `(00)123456789012345678`, `00123456789012345678`, and `]C100123456789012345678` are normalized to the 18-digit SSCC before API calls.
- Project rule: pallet identifier fields are not SSCC-only fields. They must accept both standard SSCC values and other internal/legacy pallet identifiers.
- Hardware scanner SDK integration belongs to the future Capacitor/Android wrapper layer.

## Primary Files

- [`../../terminal/wms_terminal_web/README.md`](../../terminal/wms_terminal_web/README.md)
- [`../../terminal/wms_terminal_web/src/App.tsx`](../../terminal/wms_terminal_web/src/App.tsx)
- [`../../terminal/wms_terminal_web/src/api/wmsApi.ts`](../../terminal/wms_terminal_web/src/api/wmsApi.ts)
- [`../../terminal/wms_terminal_web/src/store/localJournal.ts`](../../terminal/wms_terminal_web/src/store/localJournal.ts)
- [`../../terminal.bat`](../../terminal.bat)

## Related Pages

- [`../requirements/modern_terminal_app_tz.md`](../requirements/modern_terminal_app_tz.md)
- [`../concepts/tserver_api_registry.md`](../concepts/tserver_api_registry.md)
- [`../runbooks/create_api_server.md`](../runbooks/create_api_server.md)
