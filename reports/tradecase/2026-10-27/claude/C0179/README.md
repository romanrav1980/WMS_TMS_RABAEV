# C-0179 — T08: explanation of the capacity refusal on the operator screen

## Change
Only `admin/wms_admin_frontend/src/features/integrations/tradecase/CapacityPreview.tsx`:
- Every blocking_reason that the capacity read returns now gets its own short Russian text:
  - `TOPUP_PALLET_PLACE_MAPPING_REQUIRED` (C0178);
  - `MIXED_PACKAGE_LAYOUT_REQUIRED`;
  - `TOPUP_DEPARTURE_TIME_PASSED`, `TOPUP_AFTER_LOAD_ROUTE_ORDER_UNVERIFIED`, `TOPUP_AFTER_LOAD_RECIPIENT_NOT_ON_TRIP` (from `after_load_admission`);
  - `LOAD_ALREADY_STARTED` (from the task; the API does not return it today).
- Previously the screen chose between two texts by `loading_started`.
- An unknown code is shown as a refusal with a neutral text and its code ("Код: …"), never as success.
- The code is shown next to the text (`data-reason` for checks).
- The weight/volume/geometry ceilings are labelled "Оценка предела…", with a note that they are only an estimate and will not become approval after setup.
- The "В пределах расчёта" line still appears only when `maximum_boxes` is not null; with the C0178 refusal it is hidden.
- The help link (`HelpLink anchor="capacity"`) is kept. No new API calls; one capacity GET per calculation.

## Live check (no stub)
- The shared 8088 still serves code from before C0178 (a real GET on T1 gave `blocking_reason=null`, `maximum_boxes=0`). It is restarted only by root.
- So I used my own API instance `127.0.0.1:8093` (uvicorn `app.main:app`, current code, real Oracle) and my own Vite `127.0.0.1:3023` (`VITE_API_BASE=http://127.0.0.1:8093`). Both are stopped after the check.
- Screen: `?page=tradecase&tc_wh=226192056&tc_tab=TRIP&tc_open=T1`, product A, 1 box, a real click on "Рассчитать место".
- Script: `scripts/c0179_live_ui.cjs`; result: `c0179-live-ui.json` (PASS 2/2, 2 capacity GETs).
- 1440 and 390:
  - the real API returns `TOPUP_PALLET_PLACE_MAPPING_REQUIRED`, and the screen's `data-reason` matches it;
  - the text about pallet type, places and stacking says "заказ и резерв не создаются";
  - there is no "В пределах расчёта" line, the "только оценка" note is present, the help link is in place;
  - scrollWidth equals the viewport (1440/1440, 390/390), no page errors.
- Screenshots: `screenshots/capacity-reason-1440.png`, `screenshots/capacity-reason-390.png`.

## Checks
- tsc --noEmit OK; RETAILCASE quality gate PASS; encoding PASS; architecture PASS (cycles 0).
- There are no offline UI tests: tradecase has no test runner set up. The focused check is the live Playwright run above.

## Remaining
- On the shared 8088 the new reason will appear only after root restarts the API with C0178 (36499623). Until then the screen there shows the previous response.
- Texts for MIXED/after-load were not checked live (a real fixture for them is needed; I didn't create one). LOAD_ALREADY_STARTED is not returned by the API.
- Wiki help article not changed (the task excludes docs).
