# C-0181 — T10: shared shift resource Gantt

## Real API (read-only, no stub)
`GET /api/resources/timeline?warehouse_id=…&start_at=…&finish_at=…`, current local API `127.0.0.1:8093` (live Oracle). For comparison, the shared 8088 gives the same counts. Details: `timeline-api.json`.

| Warehouse | Window | HTTP / ms | Resources by type | Events by kind | Assignments |
|---|---|---|---|---|---|
| 220793322 | 27.10 00:00–28.10 00:00 | 200 / 425 | CASE_PICKER 6, DOCK 2 | CASE_PICK_TASK 3 | 3 |
| 220793322 | 20.10–27.10 (7 days) | 200 / 186 | CASE_PICKER 6, DOCK 2, VEHICLE 6 | CASE_PICK_TASK 6, LOAD_CONFIRMATION 2, TRIP_DEPARTURE 1, YARD_VISIT 5, YARD_DOCK 5 | 21 |
| 226192056 | 27.10 00:00–28.10 00:00 | 200 / 573 | DOCK 1, VEHICLE 1 | LOAD_CONFIRMATION 8 | 16 |
| 226192056 | 20.10–27.10 | 200 / 189 | DOCK 1 | — | 0 |

- Sources (all READY for admin): registry, attendance, warehouse_tasks, case_tasks, transport, sessions, yard. `warehouse_time_zone=null`, so the screen labels the axis "время UTC".
- **Source of each type:**
  - pickers, docks and reach trucks: `registry` (resource registry, `RRL_RESOURCE` by kind);
  - vehicles: `transport`/`yard`;
  - works: case_tasks (CASE_PICK_TASK), transport (LOAD_CONFIRMATION/TRIP_DEPARTURE), yard (YARD_VISIT/YARD_DOCK).
- **Reach trucks:** neither warehouse has any in the API response. The registry for 220793322/226192056 holds no REACHTRUCK resources. This is a source limitation; I didn't create rows, and the screen now names it. The same goes for "Прочие ресурсы" (OTHER: none).

## UI defects found and fixed
1. **Absent types:** "Ричтраки"/"Прочие ресурсы" were on but empty, with no explanation. Now each type button shows its count from the response, and a selected type with 0 resources gets a note: "Нет в ответе источника: … — реестр ресурсов склада не вернул ресурсов этого типа. Это ограничение данных, а не «свободны»".
2. **Indistinguishable rows:** six pickers had the same label "Factory CASE QA". When registry labels repeat, the row and the card show the server's resource id on the second line ("Комплектовщик · RESOURCE:86"). Search finds it too.
3. **Works invisible:** on 220793322 the summary showed "работ 3", but the works were neither on the axis nor in the queue. They are CONTROLLED tasks started 21–22.10 with no finish at the source (fact_finish_status=UNRESOLVED). A finished task is not stretched to "now" (correct), so its point fell before the window. They now appear in the queue "Без времени, без ресурса или вне шкалы" with the reason "начата до окна, окончание у источника неизвестно — на шкалу не ставится", and clicking one opens the work card.

Files:
- `features/platform/workspaces/resources/ResourceGantt.tsx`
- `timelineModel.ts` (`outsideWindow`)
- `timelineAdapter.ts` (id for repeated labels)
- `ganttHelp.ts` (queue text)
`ShiftSupervisorDesk.tsx` is unchanged.

## Live UI 1440/390
Own Vite `127.0.0.1:3023` → `127.0.0.1:8093`, screen `?page=workspace&workspace=shift&warehouse_id=…`. Script `scripts/c0181_live_ui.cjs`, result `c0181-live-ui.json` (PASS, 4 runs). Real clicks on each of the 4 runs:
- type switching ("Ворота"/"Машины" off and back on);
- resource selection → resource card;
- work selection: on 226192056 a bar ("Погрузка подтверждена · рейс 33697"), on 220793322 from the queue (3 "начата до окна" items) → work card;
- search by dock code → exactly 1 row;
- scale "4 ч" + "Позже" → axis 27.10 02:00–06:00, back to "всё окно";
- all planner controls (34/41) have an accessible name and a data-help-id; the help articles `resource-gantt` and `shift-supervisor` are published (GET /api/help/articles/… = 200);
- scrollWidth = viewport (1440/1440, 390/390): at 390 the axis scrolls inside its own container, the page does not.
Screenshots: `screenshots/gantt-{220793322,226192056}-{1440,390}.png`.

## Checks
tsc --noEmit OK; RETAILCASE quality gate PASS; encoding PASS; architecture PASS (cycles 0).

## Limitations
- Unknown/closed sources: for admin all 7 sources are READY. FORBIDDEN/ERROR/NOT_MAPPED were not reproduced live (that needs an identity without rights or a broken source). The display code is in SourceChips ("нет права …", "ошибка", "источник не подключён").
- Reach trucks and OTHER are missing from the source data for both warehouses (see above). Codex needs REACHTRUCK registry resources on the QA warehouse for a positive check of that row.
- The warehouse time zone is not set in the API (`warehouse_time_zone=null`), so the axis is in UTC with a label.
- No events were created; everything was read-only. My Vite is stopped (including the child node process).
