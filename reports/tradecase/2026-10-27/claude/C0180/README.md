# C-0180 — T10: dock fault status in the yard panel

## Change (UI only)
- `admin/wms_admin_frontend/src/features/platform/workspaces/shift/YardDockStatus.tsx` (new): the "Состояние ворот" section in the yard panel, under the dock plan:
  - **List:** each dock shows its state, latest reason, who changed it and when.
  - **Unknown state:** `blocked=null` (`ambiguous` → YARD_DOCK_AMBIGUOUS, or `status_error`) is shown as "состояние неизвестно" with the code; the row and form buttons are disabled.
  - **Actions:** "Неисправность…" / "Открыть…" with a required reason (≥3 characters).
  - **Wording:** the text explains that the mark keeps new assignments/plans off the dock and does not cancel a current visit, plan, loading or shipment.
- **Command:**
  - the `{operation_id, action, reason}` body is saved in localStorage BEFORE sending, and a retry sends the same bytes;
  - the receipt is accepted only when operation_id, dock and blocked=(action==BLOCK) all match;
  - a 409 with outcome_confirmed=true or an invalid body (422) is a refusal and clears the record;
  - `*_OPERATION_CONFLICT`, 401/403 (with the YARD_ACCESS_DENIED text), 503 and network failures keep the record with "Повторить";
  - a response that arrives after the login changed is not applied.
- Texts for YARD_DOCK_NOT_FOUND, YARD_DOCK_AMBIGUOUS, YARD_DOCK_STATUS_INVALID and YARD_ACCESS_DENIED.
- `YardPanel.tsx`: mounting only. `help.ts`: `shift.yard.dock.{refresh,block,unblock,retry,close}`. The existing help links and the narrow layout are kept.

## Live check (no stub), after API_READY_C0180
- Codex's API `127.0.0.1:8093` (uvicorn, current tree, live Oracle; not stopped or restarted). My own Vite `127.0.0.1:3023` with `VITE_API_BASE=http://127.0.0.1:8093`, now stopped.
- Warehouse 226192056, dock TR27D226192056; screen `?page=workspace&workspace=shift&warehouse_id=226192056` → real click on "Двор и ворота".
- Script: `scripts/c0180_live_ui.cjs`; result: `c0180-live-ui.json` (PASS, 4 checks, 3 POSTs).
- **1440:**
  - the real GET shows the dock as "исправны";
  - real BLOCK: the server executed it (200, blocked=true), and the reply was lost in the browser (route.fetch → abort), so the screen showed "не подтверждена" and kept the command;
  - after a page reload and login, "Повторить" sent the same bytes (both POSTs byte-identical, one operation_id); the receipt was accepted;
  - the GET shows "неисправны" with the reason.
- **390:** real click on "Открыть…", reason, "Открыть после ремонта" → 200, the GET shows "исправны"; scrollWidth 390 = viewport; no page errors.
- Final state from the real GET: TR27D226192056 `blocked=false` (dock left open, as asked). No unknown rows (`blocked=null`) on this warehouse.
- Screenshots: `screenshots/dock-retry-1440.png`, `dock-blocked-1440.png`, `dock-open-390.png`.

## Checks
- tsc --noEmit OK; RETAILCASE quality gate PASS; encoding PASS; architecture PASS (cycles 0).

## Remaining
- A live 403 was not checked: there is no identity without `tradecase_yard_operate` in the QA setup, and creating one is outside UI scope. The code path is the same as for other yard commands (record kept, rights text).
- The `blocked=null` rows and the refusals NOT_FOUND/AMBIGUOUS/STATUS_INVALID/OPERATION_CONFLICT were not reproduced in the UI: there was no such data and I didn't change Codex's fixture. Codex verified the API side (`C0180-live-api.json`).
- After the live run, the note text was changed: "ниже" → "выше: в визитах двора и в плане ворот" (the section sits below them). TS check only.
