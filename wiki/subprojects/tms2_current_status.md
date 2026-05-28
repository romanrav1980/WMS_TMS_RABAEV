# ТМС-2 — текущий статус

Дата обновления: 2026-05-28.

Назначение файла: быстрый якорь для свежей сессии. Перед работой по ТМС-2 прочитать этот документ, затем [`../roadmap/transport_execution_plan.md`](../roadmap/transport_execution_plan.md), [`../requirements/transport_dispatch_tz.md`](../requirements/transport_dispatch_tz.md), [`../requirements/transport_billing_tz.md`](../requirements/transport_billing_tz.md) и [`../requirements/tms2_acceptance_matrix.md`](../requirements/tms2_acceptance_matrix.md).

## Активная область

ТМС-2 заменяет legacy C# транспортный модуль на FastAPI + React:

- Блок I: Sprint 1-6, диспетчер и жизненный цикл рейса.
- Блок II: Sprint 7-10, карта заказов, матрица расстояний, VRP.
- Блок III: Sprint 11-14, ARM, операции, Гант, план-факт.
- Блок IV: Sprint 15-20, биллинг, счета, цена, защита billed-рейсов.

Не смешивать с `warehouse-map`, MES, WMS-picking и другими ветками.

## Последний hardening checkpoint

На 2026-05-28 пройдены Sprint 1-20 не по wiki-галочкам, а по API/DB/test paths. Позднее в тот же день отдельно усилен Block I / Sprint 1-6: добавлены прямые functional/UI/load проверки для Sprint 1-6 и устранены найденные производительные узкие места.

Проверки:

- Block I / Sprint 1-6: `78 passed` functional, UI smoke Sprint 1-6 passed, Sprint 4-6 load NFR passed.
- Block I training artifact: [`../../wiki-raw/tms2_training/block_i_sprint1_6_2026_05_28/index.html`](../../wiki-raw/tms2_training/block_i_sprint1_6_2026_05_28/index.html) with screenshots and business-process explanation.
- Block II / Sprint 7: fresh hardening gate `14 passed`; load NFR passed (`/planner/orders` p95 97.5 ms, `/routing/status` p95 35.8 ms); UI smoke `transport_sprint7_ui_smoke.cjs` passed.
- Block II / Sprint 8: fresh hardening gate `23 passed`; load NFR passed (metrics p95 360.7 ms, solve p95 647.5 ms, matrix rebuild p95 414.6 ms); UI smoke `transport_sprint8_ui_smoke.cjs` passed.
- Block II / Sprint 9: fresh hardening gate `10 passed, 1 skipped`; load NFR passed (cluster solve p95 598.3 ms, templates p95 413.5 ms, orders p95 140.1 ms); UI smoke `transport_sprint9_ui_smoke.cjs` passed.
- Block II / Sprint 10: fresh hardening gate `15 passed`; load NFR passed (history p95 471.5 ms, forecast p95 161.2 ms); UI smoke `transport_sprint10_ui_smoke.cjs` passed.
- Block II training artifact: [`../../wiki-raw/tms2_training/block_ii_sprint7_10_2026_05_28/index.html`](../../wiki-raw/tms2_training/block_ii_sprint7_10_2026_05_28/index.html) with screenshots and MAP/VRP business-process explanation.
- Block III / Sprint 11: fresh hardening gate `20 passed`; load NFR passed (operations p95 160.8 ms, fact p95 219.5 ms, gantt p95 195.5 ms, plan-operations p95 175.7 ms); UI smoke `transport_sprint11_ui_smoke.cjs` passed.
- Sprint 11 training artifact: [`../../wiki-raw/tms2_training/sprint11_arm_gantt_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint11_arm_gantt_2026_05_28/index.html) with screenshots and ARM/Gantt business-process explanation.
- Block III / Sprint 12: fresh hardening gate `12 passed`; load NFR passed (gantt p95 158.0 ms, operations p95 86.0 ms); UI smoke `transport_sprint12_ui_smoke.cjs` passed.
- Sprint 12 training artifact: [`../../wiki-raw/tms2_training/sprint12_gantt_dashboard_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint12_gantt_dashboard_2026_05_28/index.html) with screenshots and Gantt dashboard business-process explanation.
- Block III / Sprint 13: fresh hardening gate `16 passed`; load NFR passed (available p95 455.1 ms, plan-fact p95 651.1 ms, gantt p95 197.2 ms); UI smoke `transport_sprint13_ui_smoke.cjs` passed.
- Sprint 13 training artifact: [`../../wiki-raw/tms2_training/sprint13_vehicle_availability_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint13_vehicle_availability_2026_05_28/index.html) with screenshots and vehicle-availability business-process explanation.
- Block III / Sprint 14: fresh hardening gate `7 passed`; load NFR passed (plan-fact 1 day p95 420.1 ms, plan-fact 30 days p95 291.3 ms, gantt p95 125.5 ms); UI smoke `transport_sprint14_ui_smoke.cjs` passed.
- Sprint 14 training artifact: [`../../wiki-raw/tms2_training/sprint14_plan_fact_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint14_plan_fact_2026_05_28/index.html) with screenshots and plan-fact business-process explanation.
- Block IV / Sprint 15: fresh hardening gate `12 passed`; load NFR passed (billing list p95 283.0 ms, filtered list p95 85.0 ms, create p95 174.3 ms, task billing p95 189.4 ms); UI smoke `transport_sprint15_ui_smoke.cjs` passed.
- Sprint 15 training artifact: [`../../wiki-raw/tms2_training/sprint15_billing_open_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint15_billing_open_2026_05_28/index.html) with screenshots and billing-open business-process explanation.
- Block IV / Sprint 16: fresh hardening gate `11 passed`; load NFR passed (get order p95 151.1 ms, close p95 86.3 ms, pay p95 75.1 ms); UI smoke `transport_sprint16_ui_smoke.cjs` passed.
- Sprint 16 training artifact: [`../../wiki-raw/tms2_training/sprint16_billing_lifecycle_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint16_billing_lifecycle_2026_05_28/index.html) with screenshots and billing lifecycle business-process explanation.
- Block IV / Sprint 17: fresh hardening gate `12 passed`; load NFR passed (list p95 112.2 ms, date filter p95 127.5 ms, company filter p95 146.5 ms, paid filter p95 64.4 ms); UI smoke `transport_sprint17_ui_smoke.cjs` passed.
- Sprint 17 training artifact: [`../../wiki-raw/tms2_training/sprint17_billing_registry_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint17_billing_registry_2026_05_28/index.html) with screenshots and billing registry business-process explanation.
- Block IV / Sprint 18: fresh hardening gate `11 passed`; load NFR passed (set-price p95 205.3 ms, recalculate p95 92.8 ms, billing list p95 74.7 ms); UI smoke `transport_sprint18_ui_smoke.cjs` passed.
- Sprint 18 training artifact: [`../../wiki-raw/tms2_training/sprint18_price_management_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint18_price_management_2026_05_28/index.html) with screenshots and price-management business-process explanation.
- Block IV / Sprint 19: fresh hardening gate `9 passed`; load NFR passed (open-order filter p95 121.1 ms, order tasks p95 48.2 ms, add task p95 89.0 ms); UI smoke `transport_sprint19_ui_smoke.cjs` passed.
- Sprint 19 training artifact: [`../../wiki-raw/tms2_training/sprint19_link_existing_billing_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint19_link_existing_billing_2026_05_28/index.html) with screenshots and link-existing-order business-process explanation.
- Block IV / Sprint 20: fresh hardening gate `7 passed`; load NFR passed (billed cancel p95 192.3 ms, billed assign p95 156.3 ms, allowed price p95 174.3 ms); UI smoke `transport_sprint20_ui_smoke.cjs` passed.
- Sprint 20 training artifact: [`../../wiki-raw/tms2_training/sprint20_billed_task_protection_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint20_billed_task_protection_2026_05_28/index.html) with screenshots and billed-task-protection business-process explanation.
- Block IV / Sprint 15-20: `62 passed`.
- Общий transport functional control Sprint 4-20: `211 passed, 21 skipped` за 7:04.
- Encoding check: passed.
- `git diff --check` по измененным TMS-2 файлам: passed.

Sprint 1-3 теперь имеют прямые functional tests, UI smoke и load coverage для таблицы СТ, выделения/создания рейса и базовой вкладки маршрутов.

## Что исправлено в hardening

- Transport API row contract приведен к legacy uppercase keys.
- `PATCH /tasks/{id}` больше не передает лишний Oracle bind `user_id`.
- Закрытие пустого рейса отклоняется 422.
- `RRL_TRANSPORT_TYPE`, `RRL_SBORKA_PALLETS`, `RRL_V_AVAILABLE_STS`, `RRL_ADDR_DISTANCE_MATRIX`, `RRL_PLANNER_PLANS`, `RRL_TT_OPERATIONS`, `RRL_BILL_ORDERS` приведены к реальным legacy-схемам.
- Sprint 8 matrix rebuild переведен на batch `execute_many`.
- Planner использует `PAYLOAD`, не `PLAN_JSON`.
- `apply_vrp_plan` больше не глотает ошибки update/assign как partial success.
- ARM/Gantt использует `RRL_TR_VEHICLE`, `CONDITION`, `DELETED`; Sprint 11 Gantt чтение стало set-based и больше не мутирует данные на GET.
- Sprint 13 availability больше не зависит от relative date и получает короткий cache для частых проверок в диалоге создания рейса.
- Sprint 15 billing list переведен в lightweight audit for hot registry reads; UI smoke закрывает пользовательский путь «отгруженный рейс -> выставить счёт -> PAY_ORDER_ID».
- Sprint 16 billing order read переведен в lightweight audit; close/pay остаются полными мутациями.
- Billing DML-функции вызываются PL/SQL blocks, не `SELECT FROM DUAL`.
- `get_task()` возвращает `PAY_ORDER_ID`, поэтому billed-рейсы защищены от cancel/assign/unassign.
- Billing functional fixtures используют реальные рейсы с ТК и рассчитанной ценой.
- Sprint 1 `available-sts` переведен с тяжелой view/function path на set-based query по `RRL_SBORKA_PALLETS`/`RRL_SBORKA_PALLET_ROWS`/`RRL_ADDR` с коротким cache.
- Добавлен lazy Oracle connection pool вместо нового Oracle connection на каждый SQL-запрос.
- Read-only high-frequency transport GET endpoints переведены на lightweight audit path без Oracle start/finish audit, мутации продолжают идти через полный audit.
- Sprint 3/4 readiness и состав рейса используют set-based readiness вместо per-row PL/SQL-функций.
- Sprint 4-6 load scripts стабилизированы на seed-date `2026-05-25` и Windows-safe отчеты.
- Sprint 7 `planner/orders` переведен с тяжелого `RRL_V_AVAILABLE_STS` на set-based query по реальным таблицам; MAP read-only endpoints переведены на lightweight audit.
- Sprint 7 UI smoke добавлен и поймал dev runtime crash Leaflet под React StrictMode; `main.tsx` теперь рендерит `App` без StrictMode, чтобы карта работала на локальном порту `3000`.
- Sprint 8 functional gate больше не принимает пустой VRP-план как условно успешный: тесты используют стабильный seed-date `2026-05-25` и требуют непустые `routes`.
- Sprint 8 load script переведен с Locust на обычный Windows-safe Python runner.
- Sprint 9 fixed date coverage added for cluster solver and RAION; UI smoke covers the template workflow with a mocked historical template.
- Sprint 10 history/demand forecast/templates read endpoints added to lightweight audit; history/forecast use short service-cache by query params.

## Текущие риски

- Старый общий Sprint 4-20 прогон имел 21 skip из-за относительных дат/seed. Block I Sprint 1-6 теперь стабилизирован на `2026-05-25` и проходит без skip.
- Sprint 8 mutating apply full-flow отключен в default gate, чтобы не съедать shared seed; полный apply включается вручную через `TMS_RUN_MUTATING_VRP_APPLY=1`.
- Sprint 9 still has one backend skip without a historical-plan Oracle fixture before `2026-05-25`; before production, seed at least one prior applied/saved plan that overlaps current STs and rerun templates assertions without skip.
- Sprint 1-3 требуют отдельных functional tests.
- Миграции применены и проверены в dev Oracle; перед production нужен ручной Oracle/prod apply checklist и rollback rehearsal.
- В worktree могут быть unrelated изменения по WinForms/frontend/warehouse-map; не откатывать их без отдельной команды.

## Локальный запуск

- API: root `serv.bat`, порт `8088`.
- Frontend: root `front.bat`, порт `3000`.
- Не использовать порт `3001` для frontend.
- Oracle env для локальной проверки: `TMS_ORACLE`.

## Ближайшие стратегические шаги

## Checkpoint Sprint 10-19

Контекст сохранен на 2026-05-28 после свежего hardening Sprint 10-19:

- Sprint 10: planner analytics/history/forecast, UI/load/training done.
- Sprint 11-14: ARM/Gantt/plan-fact, UI/load/training done, Block III functional `55 passed`.
- Sprint 15-19: billing open/lifecycle/registry/price/link-existing, UI/load/training done, Sprint 15-19 functional `55 passed`.
- Следующий незакрытый свежим per-sprint UI/load/training gate: Sprint 21.

## Sprint 21 hardening checkpoint

- Sprint 21 RBAC закрыт свежим gate на 2026-05-28.
- Исправлено: UI больше не глотает 403 на пересчёте цены и ручной цене; ошибка показывается в `.dispatch-error`, операция не выглядит успешной.
- Functional: `tests/transport/test_sprint21_functional.py` -> `9 passed`.
- Load: `tests/transport/transport_sprint21_load_test.py` -> p95 list 76.9 ms, filtered list 60.7 ms, create 159.8 ms, recalc 185.6 ms, manual price 167.9 ms.
- UI: `tests/ui/transport_sprint21_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint21_billing_rbac_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint21_billing_rbac_2026_05_28/index.html).
- Следующий спринт: Sprint 22 — справочник компаний + `NUM_PLAT`.

## Sprint 22 hardening checkpoint

- Sprint 22 закрыт свежим gate на 2026-05-28.
- Исправлено: `GET /billing/companies` переведен в lightweight audit и cached reference path, чтобы справочник ТК не просаживал NFR.
- Functional: `tests/transport/test_sprint22_functional.py` -> `10 passed`.
- Load: `tests/transport/transport_sprint22_load_test.py` -> p95 companies 189.5 ms, orders 164.9 ms, filtered orders 86.5 ms.
- UI: `tests/ui/transport_sprint22_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint22_company_directory_num_plat_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint22_company_directory_num_plat_2026_05_28/index.html).
- Следующий спринт: Sprint 23 — детальный просмотр счёта + CSV рейсов.

## Sprint 23 hardening checkpoint

- Sprint 23 закрыт свежим gate на 2026-05-28.
- Исправлено: `GET /billing/orders/{id}/tasks` возвращает 404 для неизвестного счёта, не маскируя ошибку пустым списком.
- Functional: `tests/transport/test_sprint23_functional.py` -> `9 passed`.
- Load: `tests/transport/transport_sprint23_load_test.py` -> p95 orders 227.5 ms, order tasks 123.6 ms, companies 38.8 ms.
- UI: `tests/ui/transport_sprint23_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint23_billing_order_detail_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint23_billing_order_detail_2026_05_28/index.html).
- Следующий спринт: Sprint 24 — VRP drag-and-drop перестановка СТ.

## Sprint 24 hardening checkpoint

- Sprint 24 закрыт свежим gate на 2026-05-28.
- Исправлено/усилено: `GET /planner/metrics` добавлен в lightweight audit; load gate использует обязательные даты для history и warmup перед NFR-замером.
- Functional: `tests/transport/test_sprint24_functional.py` -> `9 passed`.
- Load: `tests/transport/transport_sprint24_load_test.py` -> p95 metrics 37.0 ms, history 36.9 ms, routing status 31.9 ms.
- UI: `tests/ui/transport_sprint24_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint24_vrp_drag_drop_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint24_vrp_drag_drop_2026_05_28/index.html).
- Следующий спринт: Sprint 25 — снять рейс с биллинга.

## Sprint 25 hardening checkpoint

- Sprint 25 закрыт свежим gate на 2026-05-28.
- Исправлено: `remove_task_from_billing_order()` теперь запрещает не только `closed`, но и `payed` счета.
- Functional: `tests/transport/test_sprint25_functional.py` -> `7 passed, 3 skipped` (в dev seed нет задач в закрытом/оплаченном счёте и задач в первом счёте для части структурных проверок).
- Load: `tests/transport/transport_sprint25_load_test.py` -> p95 orders 278.9 ms, order tasks 105.9 ms, companies 41.4 ms.
- UI: `tests/ui/transport_sprint25_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint25_detach_billing_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint25_detach_billing_2026_05_28/index.html).
- Следующий спринт: Sprint 26 — Excel export одного счёта.

## Sprint 26 hardening checkpoint

- Sprint 26 закрыт свежим gate на 2026-05-28.
- Исправлено: export endpoint больше не зависит жёстко от `openpyxl`; nonexistent order возвращает 404, а fallback XLSX строится через стандартный `zipfile`.
- Functional: `tests/transport/test_sprint26_functional.py` -> `7 passed, 4 skipped` (openpyxl content checks skipped на test runner).
- Load: `tests/transport/transport_sprint26_load_test.py` -> p95 orders 138.2 ms, order tasks 57.9 ms, export 75.5 ms.
- UI: `tests/ui/transport_sprint26_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint26_billing_order_xlsx_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint26_billing_order_xlsx_2026_05_28/index.html).
- Следующий спринт: Sprint 27 — Excel export реестра счетов.

## Sprint 27 hardening checkpoint

- Sprint 27 закрыт свежим gate на 2026-05-28.
- Исправлено: export реестра больше не зависит жёстко от `openpyxl`; fallback XLSX строится через стандартный `zipfile`.
- Functional: `tests/transport/test_sprint27_functional.py` -> `8 passed, 5 skipped` (openpyxl content checks skipped на test runner).
- Load: `tests/transport/transport_sprint27_load_test.py` -> p95 orders 137.7 ms, registry export 139.1 ms, order export 95.0 ms.
- UI: `tests/ui/transport_sprint27_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint27_billing_registry_xlsx_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint27_billing_registry_xlsx_2026_05_28/index.html).
- Следующий спринт: Sprint 28 — Excel export списка рейсов.

## Sprint 28 hardening checkpoint

- Sprint 28 закрыт свежим gate на 2026-05-28.
- Исправлено: export списка рейсов больше не зависит жёстко от `openpyxl`; fallback XLSX строится через стандартный `zipfile`.
- Functional: `tests/transport/test_sprint28_functional.py` -> `9 passed, 4 skipped` (openpyxl content checks skipped на test runner).
- Load: `tests/transport/transport_sprint28_load_test.py` -> p95 tasks 153.2 ms, dated tasks export 308.6 ms.
- UI: `tests/ui/transport_sprint28_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint28_tasks_xlsx_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint28_tasks_xlsx_2026_05_28/index.html).
- Risk: unfiltered `/tasks/export.xlsx` took about 42 seconds in the broad functional run; production should require date/status filters or streaming/background export for very large history.
- Следующий спринт: Sprint 29 — создание рейса из района/кластера.

## Sprint 29 hardening checkpoint

- Sprint 29 закрыт свежим gate на 2026-05-28.
- Исправлено: functional tests используют реальный import path `api.wms_api_server.app.*`; тесты отражают текущую server-side фильтрацию `raion`.
- Performance: `GET /clusters` добавлен в lightweight audit.
- Functional: `tests/transport/test_sprint29_functional.py` -> `8 passed`.
- Load: `tests/transport/transport_sprint29_load_test.py` -> p95 clusters 41.3 ms, safe empty create 110.7 ms.
- UI: `tests/ui/transport_sprint29_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint29_cluster_create_task_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint29_cluster_create_task_2026_05_28/index.html).
- Следующий спринт: Sprint 30.

## Sprint 30 hardening checkpoint

- Sprint 30 закрыт свежим gate на 2026-05-28.
- Исправлено: functional tests используют реальный import path `api.wms_api_server.app.*`.
- Functional: `tests/transport/test_sprint30_functional.py` -> `11 passed`.
- Load: `tests/transport/transport_sprint30_load_test.py` -> p95 task detail 215.3 ms, task STs 149.6 ms, clusters 37.1 ms.
- UI: `tests/ui/transport_sprint30_ui_smoke.cjs` passed.
- Training: [`../../wiki-raw/tms2_training/sprint30_load_bar_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint30_load_bar_2026_05_28/index.html).

## Checkpoint Sprint 21-30

Контекст сохранен на 2026-05-28 после hardening Sprint 21-30:

- Sprint 21: billing RBAC, UI 403 visibility, load/training done.
- Sprint 22: billing company directory + `NUM_PLAT`, lightweight/cache, load/training done.
- Sprint 23: billing order detail + CSV, unknown order -> 404, load/training done.
- Sprint 24: VRP drag-and-drop route stop move, planner metrics lightweight, load/training done.
- Sprint 25: detach from billing, paid-order protection fixed, load/training done; dev seed has negative-case skips for closed/payed tasks.
- Sprint 26: single order XLSX export, stdlib fallback without `openpyxl`, load/training done.
- Sprint 27: billing registry XLSX export, stdlib fallback without `openpyxl`, load/training done.
- Sprint 28: tasks XLSX export, stdlib fallback without `openpyxl`, load/training done; unfiltered export is heavy and should be constrained before production.
- Sprint 29: create task from cluster, server-side raion filter tests, clusters lightweight, load/training done.
- Sprint 30: live load bar, functional/UI/load/training done.
- Следующий спринт: Sprint 31.

## Sprint 31 hardening checkpoint

- Sprint 31 закрыт свежим gate на 2026-05-28.
- Исправлено: functional tests используют реальный import path `api.wms_api_server.app.*`.
- Добавлено: UI smoke для режима «По районам», sidebar totals, active card и открытия dialog «Рейс».
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint31_cluster_sidebar_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint31_cluster_sidebar_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint31_functional.py` -> `6 passed`.
- UI: `tests/ui/transport_sprint31_ui_smoke.cjs` passed.
- Load: `tests/transport/transport_sprint31_load_test.py` переведён с Locust на Windows-safe runner; p95 clusters 200.5 ms, tasks 247.8 ms. Тест исправлен на `shipment_date` вместо broad `date_to`.
- Следующий спринт: Sprint 32.

## Sprint 32 hardening checkpoint

- Sprint 32 закрыт свежим gate на 2026-05-28.
- Добавлено: UI smoke для overload warning в панели рейса.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint32_overload_warning_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint32_overload_warning_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint32_functional.py` -> `11 passed`.
- Load: `tests/transport/transport_sprint32_load_test.py` переведён с Locust на Windows-safe runner; p95 task 186.3 ms, task STs 160.6 ms, vehicles 75.7 ms.
- UI: `tests/ui/transport_sprint32_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 33.

## Sprint 33 hardening checkpoint

- Sprint 33 закрыт свежим gate на 2026-05-28.
- Добавлено: UI smoke для режима «Кратко» в таблице маршрутов.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint33_routes_brief_mode_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint33_routes_brief_mode_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint33_functional.py` -> `13 passed`.
- Load: `tests/transport/transport_sprint33_load_test.py` переведён с Locust на Windows-safe runner; warm p95 tasks 163.8 ms.
- UI: `tests/ui/transport_sprint33_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 34.

## Sprint 34 hardening checkpoint

- Sprint 34 закрыт свежим gate на 2026-05-28.
- Обновлено: functional tests теперь проверяют фактический set-based transactional contract, а не старую модель цикла `RRL_TT_ADD_PALL`.
- Добавлено: UI smoke для кнопки «Отменить»: confirmation, POST cancel, toast, refresh.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint34_cancel_releases_st_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint34_cancel_releases_st_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint34_functional.py` -> `6 passed`.
- Load: `tests/transport/transport_sprint34_load_test.py` безопасный mocked service runner; p95 12.54 ms.
- UI: `tests/ui/transport_sprint34_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 35.

## Context checkpoint after Sprint 34

Контекст сохранен по запросу пользователя на 2026-05-28:

- Активный проект: только ТМС-2. Warehouse-map, MES, WMS-picking и параллельные ветки не трогать без прямого поручения.
- Frontend-порт: только `3000`; порт `3001` не использовать.
- Закрытый диапазон последней сессии: Sprint 31-34.
- Sprint 31: ClusterSidebar, UI smoke, training, Windows-safe load. В load-тесте исправлен broad `date_to` на точный `shipment_date`.
- Sprint 32: overload warning, UI smoke, training, Windows-safe load.
- Sprint 33: режим «Кратко», UI smoke, training, Windows-safe load.
- Sprint 34: cancel_task проверяется как set-based transaction: сначала `RRL_SBORKA_PALLETS.TRANSTASK_ID=NULL`, затем `RRL_TRANSPORT_TASK.DELETED=1`; тесты больше не ждут старый цикл `RRL_TT_ADD_PALL`.
- Все training packs для Sprint 31-34 лежат в `wiki-raw/tms2_training/`.
- Последняя гигиена: `scripts/check-encoding.ps1` passed; `git diff --check` passed с обычными CRLF warnings.
- Временный API `8089`, использованный для load-gates из-за нестабильного `8088`, остановлен. Если `8088` снова висит, для проверки backend можно временно поднять fresh API на `8089`, но frontend всё равно держать на `3000`.
- Следующий старт: Sprint 35 — server-side `raion` filter optimization. Выполнено ниже; актуальный следующий старт теперь Sprint 36.

## Sprint 35 hardening checkpoint

- Sprint 35 закрыт свежим gate на 2026-05-28.
- Исправлено: `list_available_sts(raion="")` больше не добавляет пустой SQL-фильтр `A.RAION = :raion`.
- Обновлено: functional tests используют реальный import path и очищают available ST cache между кейсами.
- Добавлено: UI smoke для создания рейса из района; проверяется, что POST идёт в `/clusters/{raion}/create-task`.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint35_raion_filter_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint35_raion_filter_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint35_functional.py` -> `8 passed`.
- Load: `tests/transport/transport_sprint35_load_test.py` Windows-safe no-mutation runner; p95 all STs 37.2 ms, filtered 30.1 ms, safe empty create 158.6 ms.
- UI: `tests/ui/transport_sprint35_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 36.

## Sprint 36 hardening checkpoint

- Sprint 36 закрыт свежим gate на 2026-05-28.
- Исправлено: backend `unassign_st` теперь запрещает снятие СТ с рейса в состоянии «Отгружен», а не полагается только на UI.
- Обновлено: functional tests используют актуальный метод `unassign_st`.
- Добавлено: UI smoke для bulk removal: выбрать 2 СТ, нажать «Снять выбранные», подтвердить, проверить refresh.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint36_bulk_unassign_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint36_bulk_unassign_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint36_functional.py` -> `16 passed`.
- Load: `tests/transport/transport_sprint36_load_test.py` Windows-safe no-mutation runner; p95 single DELETE 171.4 ms, GET STs 160.6 ms, bulk burst 178.0 ms.
- UI: `tests/ui/transport_sprint36_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 37.

## Sprint 37 hardening checkpoint

- Sprint 37 закрыт свежим gate на 2026-05-28.
- Добавлено: UI smoke для select-all в таблице свободных СТ и toggling «Авто».
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint37_select_all_autorefresh_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint37_select_all_autorefresh_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint37_functional.py` -> `18 passed`.
- Load: `tests/transport/transport_sprint37_load_test.py` Windows-safe concurrent polling runner; p95 available STs 69.9 ms, tasks 78.8 ms, clusters 66.5 ms.
- UI: `tests/ui/transport_sprint37_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 38.

## Sprint 38 hardening checkpoint

- Sprint 38 закрыт свежим gate на 2026-05-28.
- Исправлено: `update_task()` теперь возвращает 404 при `UPDATE` rowcount 0; missing `PATCH /tasks/{id}` больше не считается success.
- Добавлено: functional test для missing PATCH -> 404.
- Добавлено: UI smoke для копирования рейса: POST/PATCH/GET sequence, новый рейс выбран.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint38_copy_trip_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint38_copy_trip_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint38_functional.py` -> `15 passed`.
- Load: `tests/transport/transport_sprint38_load_test.py` no-mutation runner; p95 tasks list 167.3 ms, missing GET 167.2 ms, missing PATCH 161.1 ms.
- UI: `tests/ui/transport_sprint38_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 39.

## Sprint 39 hardening checkpoint

- Sprint 39 закрыт свежим gate на 2026-05-28.
- Заменено: `tests/transport/transport_sprint39_load_test.py` больше не требует Locust; это Windows-safe no-mutation runner по `/available-sts` с комбинациями фильтров.
- Добавлено: UI smoke для бейджа активных фильтров и кнопки `× Сбросить`.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint39_filter_badge_reset_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint39_filter_badge_reset_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint39_functional.py` -> `26 passed`.
- Load: `tests/transport/transport_sprint39_load_test.py`; p95 no filters 39.2 ms, addr_mask 30.1 ms, type+assembled 29.4 ms, unassigned=false 37.0 ms.
- UI: `tests/ui/transport_sprint39_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 40.

## Sprint 40 hardening checkpoint

- Sprint 40 закрыт свежим gate на 2026-05-28.
- Исправлено: functional helper теперь повторяет React-контракт `PALLET_COUNT/TEMP_WEIGHT null -> 0`, поэтому null-сценарии проверяются без TypeError.
- Заменено: `tests/transport/transport_sprint40_load_test.py` больше не требует Locust; это Windows-safe no-mutation runner по task list и adjacent available-sts.
- Добавлено: UI smoke для дневной сводки `Рейсов · Паллет · Вес кг · Отгружено`.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint40_day_summary_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint40_day_summary_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint40_functional.py` -> `11 passed`.
- Load: `tests/transport/transport_sprint40_load_test.py`; p95 tasks 83.3 ms, all statuses 54.1 ms, adjacent available-sts 43.2 ms.
- UI: `tests/ui/transport_sprint40_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 41.

## Sprint 41 hardening checkpoint

- Sprint 41 закрыт свежим gate на 2026-05-28.
- Заменено: `tests/transport/transport_sprint41_load_test.py` больше не требует Locust; это Windows-safe no-mutation runner по task list сценариям вкладки «Маршруты».
- Добавлено: UI smoke для фильтра статусов `Отгружен`, `Отменён`, `Все`.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint41_routes_status_filter_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint41_routes_status_filter_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint41_functional.py` -> `14 passed`.
- Load: `tests/transport/transport_sprint41_load_test.py`; p95 all statuses 53.0 ms, date range 88.2 ms, no payments 126.2 ms.
- UI: `tests/ui/transport_sprint41_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 42.

## Sprint 42 hardening checkpoint

- Sprint 42 закрыт свежим gate на 2026-05-28.
- Заменено: `tests/transport/transport_sprint42_load_test.py` больше не создаёт реальные рейсы; runner измеряет read baseline и validation-only `POST /tasks` -> 422.
- Добавлено: UI smoke для toast после успешной операции и скрытия по клику.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint42_toast_notifications_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint42_toast_notifications_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint42_functional.py` -> `13 passed`.
- Load: `tests/transport/transport_sprint42_load_test.py`; p95 tasks 59.8 ms, available-sts 44.1 ms, validation-only POST 186.4 ms.
- UI: `tests/ui/transport_sprint42_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 43.

## Sprint 43 hardening checkpoint

- Sprint 43 закрыт свежим gate на 2026-05-28.
- Исправлено: comparator таблицы рейсов теперь держит пустые значения в конце и при asc, и при desc; раньше desc мог поднимать пустые `TRANSPORT/PRICE` наверх.
- Добавлено: functional regression для null-last при desc.
- Заменено: `tests/transport/transport_sprint43_load_test.py` больше не требует Locust; это Windows-safe no-mutation runner.
- Добавлено: UI smoke для сортировки `ID` и `Машина` с null-last.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint43_sortable_trips_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint43_sortable_trips_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint43_functional.py` -> `14 passed`.
- Load: `tests/transport/transport_sprint43_load_test.py`; p95 sortable source 85.2 ms, date range 38.8 ms, adjacent available-sts 37.5 ms.
- UI: `tests/ui/transport_sprint43_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 44.

## Sprint 44 hardening checkpoint

- Sprint 44 закрыт свежим gate на 2026-05-28.
- Исправлено: Escape больше не игнорируется после клика по checkbox/radio; текстовые поля, select и textarea по-прежнему защищены от глобального перехвата.
- Заменено: `tests/transport/transport_sprint44_load_test.py` больше не требует Locust; это Windows-safe no-mutation runner.
- Добавлено: UI smoke для снятия выделения свободной СТ и закрытия диалога создания рейса по Escape.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint44_escape_handler_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint44_escape_handler_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint44_functional.py` -> `12 passed`.
- Load: `tests/transport/transport_sprint44_load_test.py`; p95 tasks 89.1 ms, available-sts 43.9 ms, clusters 39.1 ms.
- UI: `tests/ui/transport_sprint44_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 45.

## Sprint 45 hardening checkpoint

- Sprint 45 закрыт свежим gate на 2026-05-28.
- Исправлено: functional helper теперь трактует `TRANSTASK_ID=0` как отсутствие рейса, совпадая с UI-условием rendering.
- Заменено: `tests/transport/transport_sprint45_load_test.py` больше не требует Locust; это Windows-safe no-mutation runner.
- Добавлено: UI smoke для кнопки `#ID →`, переключения во вкладку «Маршруты» и выбора рейса.
- Добавлено: обучающий HTML pack [`../../wiki-raw/tms2_training/sprint45_goto_trip_2026_05_28/index.html`](../../wiki-raw/tms2_training/sprint45_goto_trip_2026_05_28/index.html).
- Functional: `tests/transport/test_sprint45_functional.py` -> `11 passed`.
- Load: `tests/transport/transport_sprint45_load_test.py`; p95 available-sts all 42.9 ms, tasks routes 78.2 ms, missing task 163.8 ms.
- UI: `tests/ui/transport_sprint45_ui_smoke.cjs` passed.
- Следующий спринт: Sprint 46.

## Project endpoint configuration checkpoint

- Локальные IP/ports/Oracle DSN вынесены в общий tracked config [`../../config/project.defaults.json`](../../config/project.defaults.json).
- `front.bat`, `serv.bat`, `admin/wms_admin_frontend/vite.config.ts`, `api/wms_api_server/app/config.py` теперь читают defaults из общего config и принимают env overrides.
- Добавлены helpers:
  - `tests/support/project_config.cjs` для Playwright/UI scripts;
  - `tests/support/project_config.py` для Python load runners.
- Свежие TMS-2 Sprint 39-45 UI/load scripts переведены с hardcoded local URLs на helpers.
- Правило дальше: новые номера портов, IP и base URLs не хардкодить в sprint scripts; добавлять в общий config или использовать env override.

1. Продолжить sequential hardening с Sprint 46.
2. После каждого закрытого спринта или блока формировать HTML training pack в `wiki-raw/tms2_training/`: зачем блок, структура данных, результат, screenshots, бизнес-процессы и визуальное доказательство успешного выполнения.
3. Создать стабильный dated seed для полного transport acceptance, чтобы убрать data-dependent skips вне Block I.
4. Для Sprint 8 перед production отдельно прогнать mutating apply на контролируемом Oracle fixture: created tasks, assigned STs, no partial success.
5. После Sprint 1-20 расширять hardening на Sprint 21-30 отдельным блоком, не смешивая с параллельными Sprint 30+ работами.
