# C-0189 — T06: manual NET in the real CASE picker screen

## Line eligibility signal
- `GET /api/case-pick/tasks/{task}/lines/{line}/marking-policy` (scoped):
  - `weighted_kg` = a weighted SKU ∧ the KG→KG 1:1 conversion ∧ ¬SERIALIZED_WEIGHT_BOXES; added by root after K-0213;
  - `loose_weight_kg = weighted_kg ∧ ¬marking_required`; also `serialized_weight_boxes`, `marking_required` and `profiles`.
- `order-weight-preview` is not used for the classification: it does not state the conversion or serialization.
- The unit is never inferred from the name, barcode or quantity shown.

## Change (owned files)
- **New `wiki-raw/wms_admin_ui_reference/case-pick-manual-net.js` (`window.cpManualNet`):**
  - shown only when `weighted_kg ∧ ¬serialized_weight_boxes`;
  - the "Весов нет — ввести нетто вручную" checkbox and the "Нетто вручную, кг" field (decimal, Enter from keyboard/scanner = confirm), the "ручной ввод, не показание весов" note, and the link "Как ввести нетто вручную" → `/help/manual-weight.html#case-manual-net`;
  - for a **marked** KG line manual NET is forced: the checkbox is on and locked, and all marking profile codes are required (`cpCaseMarking.collect`, ≤50 like the contract);
  - the cumulative-fact field is locked for a KG line;
  - body: `{operation_id, net_weight_kg, scan_cell, scan_container, unit_scans}` only. **No** `fact_qty`/`warehouse_scale_capture`. Validation: >0 and ≤9 decimals.
- **`case-pick-posting.js`** (owned per K-0213), the existing journal:
  - the new route `weigh-line-manual`: the body with operation_id is saved before sending, retry with the same bytes, a reload keeps the command, and a different value cannot start a new command;
  - **a KG line (`weighted_kg`) never goes to the general `/confirm`**: without a scale reading and without manual NET it is a local refusal with no request. A loose line with no reading gets the hint "…или отметьте «Весов нет — ввести нетто вручную»";
  - success: "Отбор проведён: нетто N кг введено вручную…"; a 409 `WEIGHED_CASE_MANUAL_REJECTED` → "Ручное нетто не принято: … Команда завершена, товар не проведён";
  - 503/conflicts follow the existing logic (the command is kept, retry);
  - the regular EA/box, weighted-box, the electronic NET and the shortage paths are unchanged.
- `case-pick-tsd.html`: the `#cpTsdManualNet` container and the scripts (`case-pick-manual-net.js?v=20261028`, posting `?v=20261028-manual-net`).
- `docs/help/public/manual-weight.html`: the section `#case-manual-net` (what to enter, how the server computes the cumulative total, marked products, box-by-box products, repeat after a lost response).

## UI check (intercepted requests only, no live writes)
`scripts/c0189_ui.cjs` → `c0189-ui.json` **PASS, 9 scenarios**, no page errors. The page is served by a local static server; every `http://127.0.0.1:8088/**` request is intercepted by Playwright.
1. **360/390/1440, loose KG:** checkbox → typing 1.250 with the keyboard → Enter → exactly one POST to `/tasks/500/lines/700/weigh-line-manual` with the body keys `net_weight_kg, operation_id, scan_cell, scan_container, unit_scans`; 0 general `/confirm`; the message about manual entry; scrollWidth = viewport.
2. **390, unknown outcome:** 503 → "Исход не подтверждён" + "Повторить" → reload → the command is kept → a different value (0.900) is refused locally without a request → "Повторить" sends **byte-for-byte the same body** (0.800) → receipt; the button disappears.
3. **360:**
   - 409 confirmed refusal → a clear message, the command cleared, no retry offered;
   - 409 OPERATION_CONTENT_CONFLICT after an unknown outcome → the command is kept, not shown as success.
4. **1440:** a KG line without a reading and without manual NET → no request.
5. **390, marked KG:** manual is forced; without codes nothing is sent; with a code → `/weigh-line-manual` with `unit_scans`; 0 `/confirm`.
6. **1440, non-KG line:** the manual block is hidden; the regular `/confirm` with fact_qty is unchanged.

Screenshots: `screenshots/manual-net-entry-{360,390,1440}.png` (entry), `manual-net-{…}.png` (after success), `manual-net-retry-390.png`, `manual-net-marked-390.png`.

## Checks (commands)
- `node reports/tradecase/2026-10-28/claude/C0189/scripts/c0189_ui.cjs` → PASS 9
- `python scripts/retailcase_quality_gate.py` → PASS
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-encoding.ps1` → PASS
- `python scripts/check_architecture.py` → PASS (cycles 0)

## Limitations
- The check uses intercepted requests: no real API or Oracle, and no posting made. **T06 is not complete**: live posting through `/weigh-line-manual` (after root restarts the API with 442f80a9 and `weighted_kg`) and the mixed-tree acceptance remain Codex gates.
- Static assets in production are served from `/wms-admin/`; the help link points to `/help/manual-weight.html#case-manual-net` (the published section).
