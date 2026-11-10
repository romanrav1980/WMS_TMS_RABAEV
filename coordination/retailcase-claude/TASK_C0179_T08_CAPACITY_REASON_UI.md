# C0179 — T08: explain capacity refusal in the operator screen

The API now returns `TOPUP_PALLET_PLACE_MAPPING_REQUIRED` when pallet-place or stacking data are not authoritative. The existing capacity screen displays the same generic warning for every `blocking_reason`, so the operator cannot tell whether the trip is already loading or the vehicle/master data are incomplete.

## Task

Update only `admin/wms_admin_frontend/src/features/integrations/tradecase/CapacityPreview.tsx` and its focused UI checks so every currently returned blocking reason has a concise Russian explanation tied to the API reason. At minimum:

- `TOPUP_PALLET_PLACE_MAPPING_REQUIRED`: the system cannot approve top-up until pallet type, places per box/pallet and stacking rules are configured and confirmed; capacity is not calculated and no order or reservation is created.
- `LOAD_ALREADY_STARTED`: explain that this preview cannot determine top-up after loading began.
- `MIXED_PACKAGE_LAYOUT_REQUIRED`: explain that a confirmed placement/layout is needed for mixed package dimensions.

Keep the numeric ceilings visible as estimates only; do not imply approval or promise that setup will make a product fit. Unknown future reasons must be shown as an explicit unknown blocking code with a neutral message, never silently mapped to success. Keep the existing help link and add no new API calls.

## Verification and handoff

- Run focused tests, TypeScript build/check and the Retailcase quality gate.
- Exercise the actual served screen against the current API response if the local service is available; capture 1440px and 390px checks. Do not fake the API response for the main acceptance evidence.
- Do not edit backend, Oracle, shared dist, docs outside the task report, or Codex-owned data.
- Save `RESULT_C0179.md`, commit the change and send RELEASE through the existing file channel. Include test commands, real API/UI evidence, and remaining limitations. Do not publish to GitHub.
