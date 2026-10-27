# C-0185 — T10: live refusal of a plan on a broken dock (closes the C0182 gate)

## Preflight (read-only, API 127.0.0.1:8093, 27.10 ~19:31 UTC)
- Warehouse 220793322 (TRADECASE QA): docks B22D1161 and N22DA1168 `blocked=false, ambiguous=false`; active visits `[]`; plans for 7 days `[]`.
- Stock of the warehouse (sum REMAIN / HARD_RESERVED_BASE / rows): `7 / 5 / 14`. Slow-log marker saved.

## Run (tag `C0185.119165bc3b`, identity admin, no temporary user)
1. **The only non-API write:** SUPPLY metadata document `C0185.119165bc3b` in RRL_TRADE_DOCUMENT. Absence checked first; marked "C-0185 controlled metadata; no ERP receipt proof"; no physical receipt claimed.
2. API `POST /yard/visits` → 200: my inbound visit **638** (supply_ids=[tag], vehicle=tag, arrival +3 h, EXPECTED).
3. API `POST /yard/docks/B22D1161/status` BLOCK (op `….block`) → 200 `blocked=true`.
4. **UI on my own Vite 127.0.0.1:3023 → 8093, no mocking** (`scripts/c0185_ui.cjs`, `c0185-ui.json` PASS). At both 1440 and 390:
   - the dock-status section shows B22D1161 "неисправны";
   - "Запланировать ворота" → visit 638, dock B22D1161, +5 h…+6 h → real click "Запланировать";
   - POST `/yard/dock-plans` → **409 `{code: YARD_DOCK_BLOCKED, outcome_confirmed: true, retry_same_operation_id: false}`**;
   - the screen shows the C0182 text: "Ворота отмечены неисправными (раздел «Состояние ворот»). План или назначение не создано; …";
   - after "Обновить план" there is no plan row for visit 638 and no "не подтверждена" command (the confirmed refusal cleared it);
   - scrollWidth = viewport (1440/390).
5. **finally:**
   - API UNBLOCK (separate op `….unblock`) → 200 `blocked=false`;
   - API CANCEL of visit 638 only (expected_version from the current GET) → 200.
- All 4 POST commands returned 200 on the first attempt; no unknown outcomes.

## Readback after the run
| Check | Result |
|---|---|
| B22D1161 open and unambiguous | true |
| Visit 638 | CANCELLED (RRL_YARD_VISIT, read-only) |
| Plans of visit 638 | 0 |
| Active visits before = after | `[]` = `[]` |
| Plans (7 days) before = after | `[]` = `[]` |
| Stock of 220793322 before = after | `7/5/14` = `7/5/14` |
| Temporary user | not created (admin), nothing to revoke |
| API processes | not restarted |

Slow SQL since the marker: entries belong to other read snapshots ("Current CASE queue READ ONLY snapshot" 1311 ms, "Bounded shift overview" 1201 ms); none come from the yard commands of this run.

Screenshots: `screenshots/blocked-plan-1440.png`, `screenshots/blocked-plan-390.png`. Full log of calls and states: `c0185-state.json`.

## Code
No changes: no defect reproduced. The C0182 text is shown, the refusal is confirmed, and no plan is created.

## Remaining / observations
- The tagged SUPPLY metadata document `C0185.119165bc3b` (ACCEPTED) remains in RRL_TRADE_DOCUMENT, as in the earlier fixtures; deleting it would be a direct table write. The visit history of 638 (append-only events) remains with the CANCELLED state.
- At 390 the hover hint of the "Обновить план" button (shared HelpButton) is cut off at the left edge of the screen. The page does not scroll sideways. The component is shared and outside the allowed files; noted for Codex.
