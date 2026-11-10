# C0189 — T06: manual NET entry in the actual CASE picker screen

## Goal

Make the manual NET endpoint from commit `442f80a9` usable by a warehouse picker in the current case-pick screen. That screen is the runtime-mounted `/wms-admin/case-pick-tsd.html` from `wiki-raw/wms_admin_ui_reference/`, not a design reference. Keep the current line-confirmation, weighted-box, short, retry and electronic-weight behavior working.

## Before editing

1. Read `wiki/index.md`, T06 in `wiki/roadmap/tradecase_execution_20261019.md`, `RESULT_C0188.md`, `wiki-raw/wms_admin_ui_reference/case-pick-tsd.html`, `case-pick-tsd.js`, `case-pick-posting.js`, and `docs/help/public/manual-weight.html`.
2. The scoped `GET /api/case-pick/tasks/{task}/lines/{line}/marking-policy` now returns `weighted_kg`: true only for a KG→KG 1:1 product which is not SERIALIZED_WEIGHT_BOXES. Use that field as the KG eligibility signal; do not infer from product name, barcode, or displayed quantity. `loose_weight_kg` remains false when marking is required. For marked KG lines, use the existing marking-scan UI and pass its validated scans to the manual NET endpoint.

## Implementation

- Add a clearly labeled manual NET KG input for eligible KG lines, with the current warehouse location and selected CASE carrier supplied from server-confirmed task context.
- Submit only to `POST /api/case-pick/tasks/{task}/lines/{line}/weigh-line-manual`. Never put `fact_qty` or `warehouse_scale_capture` in the body. Show the entered NET value and that it was manually entered.
- Keep persisted operation_id and exact payload for retry after timeout/reload. Do not create a new id after unknown outcome; surface 409 confirmed refusal vs 503 unknown result using existing messages/recovery patterns.
- Do not route KG-weighted lines through generic `/confirm`; keep regular EA/box and serialized weighted-box scans on their existing paths. A marked loose-KG line may use the manual NET endpoint only with all required unit scans.
- Add a concise help section to `docs/help/public/manual-weight.html` and link it from the new field/action. Every new button must state action/purpose and link to the help section.
- Use existing static page design and keyboard/scanner behavior. No redesign or invented scale display.

## Ownership and boundaries

Own only `wiki-raw/wms_admin_ui_reference/case-pick-tsd.html`, `case-pick-tsd.js`, `case-pick-posting.js`, one new adjacent JS/CSS file, `docs/help/public/manual-weight.html`, corresponding focused UI tests and evidence, plus `RESULT_C0189.md`. Codex owns the read-only `weighted_kg` contract change; do not edit backend/Oracle, stock posting, shared application code, or C0188 files. No Oracle writes, API restart, hardware call, GitHub push, or fixture mutation.

## Validation and delivery

- First ACK the exact owned files and the verified source of the KG eligibility signal; wait for review before editing.
- Cover 360/390/1440 widths, keyboard and scanner entry, non-KG line, marked KG line, exact retry after unknown response, changed-body refusal, 409/503 distinction and zero unintended generic confirms. Use intercepted/mock reads and POSTs only.
- Run relevant UI tests and `python scripts/retailcase_quality_gate.py`; `scripts/check-encoding.ps1` must pass.
- Save screenshots/check results under `reports/tradecase/2026-10-28/claude/C0189/`, commit only owned files, write `RESULT_C0189.md`, and send RELEASE. Do not call T06 complete: live Oracle/API posting and mixed-tree acceptance remain Codex gates.
