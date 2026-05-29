# ТМС-2 — матрица приемки

Дата обновления: 2026-05-29.

Назначение: фиксировать, что спринт считается рабочим только когда покрыт пользовательский путь, API contract, Oracle contract и functional test. Галочка в roadmap сама по себе не означает готовность.

## Общие правила приемки

- Любой бизнес-успех должен быть подтвержден состоянием Oracle, а не только HTTP 200.
- DML-функции Oracle вызываются через PL/SQL blocks, не через `SELECT ... FROM DUAL`.
- `rows_as_dicts()` может отдавать lowercase, но публичный transport API сохраняет legacy uppercase keys там, где этого ждут frontend/tests.
- Нет silent `except/pass` в бизнес-операциях: partial success не возвращается как success.
- Для операций создания/привязки/счетов нужны idempotency/retry правила или явное доказательство, что повторный вызов безопасен.
- Frontend payload/response должен совпадать с `schemas.py` и реальными Oracle column names.
- Если тест skipped из-за seed, это риск acceptance, а не зеленый статус.

## Блок I — Dispatcher, Sprint 1-6

| Sprint | Пользовательский путь | API/DB contract | Functional gate | Статус |
|---|---|---|---|---|
| 1 | Диспетчер открывает таблицу СТ, видит 16 колонок, фильтрует по дате/складу/адресу/типу ТС | `GET /available-sts`; реальные поля `RRL_V_AVAILABLE_STS`; быстрый empty-date path | `test_sprint1_functional.py`, `transport_sprint1_ui_smoke.cjs`, `transport_sprint1_load_test.py`; Block I training pack `wiki-raw/tms2_training/block_i_sprint1_6_2026_05_28/` | Passed |
| 2 | Выделить несколько СТ, увидеть итоги, создать рейс | `POST /tasks`, `POST /tasks/{id}/sts`; Oracle `RRL_TRANSPORT_TASK`; current implementation uses set-based assignment contract | `test_sprint2_functional.py`, `transport_sprint2_ui_smoke.cjs`, `transport_sprint2_load_test.py`; Block I training pack | Passed |
| 3 | Открыть вкладку маршрутов, увидеть рейс и состав | `GET /tasks`, `GET /tasks/{id}/sts`; uppercase response keys | `test_sprint3_functional.py`, `transport_sprint3_ui_smoke.cjs`, `transport_sprint3_load_test.py`; Block I training pack | Passed |
| 4 | Редактировать рейс, закрыть, отменить, назначить/снять СТ | `PATCH /tasks/{id}`, `close`, `cancel`; пустой рейс закрыть нельзя | `test_sprint4_functional.py` | Passed with seed skips |
| 5 | Видеть готовность сборки и требования к ТС | readiness functions, transport type columns | `test_sprint5_functional.py` | Passed with seed skips |
| 6 | Открыть паллеты СТ, менять load type/order | `GET /sts/{st}/pallets`; без несуществующего `SP.DELETED` | `test_sprint6_functional.py` | Passed with seed skips |

## Блок II — MAP / VRP, Sprint 7-10

| Sprint | Пользовательский путь | API/DB contract | Functional gate | Статус |
|---|---|---|---|---|
| 7 | Открыть карту заказов с геокодированными маркерами | `GET /planner/orders`, `GET /routing/status`; `RRL_ADDR` coordinates | `test_sprint7_functional.py`, `transport_sprint7_load_test.py`, `transport_sprint7_ui_smoke.cjs` | Fresh hardening passed: `14 passed`, load NFR passed, UI smoke passed |
| 8 | Rebuild matrix -> solve VRP -> apply plan -> получить рейсы с назначенными СТ | `RRL_ADDR_DISTANCE_MATRIX.DISTANCE_KM/UPDATED_AT`; `RRL_PLANNER_PLANS.PAYLOAD`; no partial-success apply | `test_sprint8_functional.py`, `transport_sprint8_load_test.py`, `transport_sprint8_ui_smoke.cjs` | Fresh hardening passed: `23 passed`, non-empty plan required, load NFR passed, UI smoke passed; mutating apply full-flow is optional via env |
| 9 | Смотреть кластеры/шаблоны/историю похожих планов | planner history/templates tables; deterministic fixture migration `055_apply.sql` seeds one historical `RRL_PLANNER_PLANS` row | `test_sprint9_functional.py`, `transport_sprint9_load_test.py`, `transport_sprint9_ui_smoke.cjs` | Passed; `test_sprint9_functional.py` -> `11 passed` after live fixture apply |
| 10 | Видеть метрики качества плана и forecast | history/forecast endpoints; forecast без тяжелой repeated view scan | `test_sprint10_functional.py`, `transport_sprint10_load_test.py`, `transport_sprint10_ui_smoke.cjs` | Fresh hardening passed: `15 passed`, load NFR passed, UI smoke passed |

Hard gate для Sprint 8 перед production: нужен non-empty fixture, где `routes.length > 0`, route stops имеют координаты, `apply` создает рейсы, назначает все route STs и не помечает plan applied при ошибке assign/update.

## Блок III — ARM / Gantt, Sprint 11-14

| Sprint | Пользовательский путь | API/DB contract | Functional gate | Статус |
|---|---|---|---|---|
| 11 | Создать/увидеть плановую цепочку операций рейса; открыть Гант, карточку рейса, отметить факт, увидеть план-факт | `RRL_TT_OPERATIONS`, `RRL_TRANSPORT_NORMS`; set-based Gantt read; no mutating GET; migration 053 legacy-compatible | `test_sprint11_functional.py`, `transport_sprint11_ui_smoke.cjs`, `transport_sprint11_load_test.py`; training pack `wiki-raw/tms2_training/sprint11_arm_gantt_2026_05_28/` | Passed |
| 12 | Открыть Гант по машинам и рейсам; проверить легенду, сводку, tooltip, фильтр, дата-навигацию и отклонения | `RRL_TR_VEHICLE`; set-based Gantt data from `RRL_TT_OPERATIONS`; no-vehicle tasks separated | `test_sprint12_functional.py`, `transport_sprint12_ui_smoke.cjs`, `transport_sprint12_load_test.py`; training pack `wiki-raw/tms2_training/sprint12_gantt_dashboard_2026_05_28/` | Passed |
| 13 | Получить доступные машины и конфликты в диалоге создания рейса | availability по `DELETED`, date ranges, real legacy columns; short cache invalidated by operation changes | `test_sprint13_functional.py`, `transport_sprint13_ui_smoke.cjs`, `transport_sprint13_load_test.py`; training pack `wiki-raw/tms2_training/sprint13_vehicle_availability_2026_05_28/` | Passed |
| 14 | Открыть plan-fact отчет, увидеть дельты/нарушения отдыха и экспортировать CSV | `CONDITION AS STATUS`, `DELETED`; operations fact/plan aggregation | `test_sprint14_functional.py`, `transport_sprint14_ui_smoke.cjs`, `transport_sprint14_load_test.py`; training pack `wiki-raw/tms2_training/sprint14_plan_fact_2026_05_28/` | Passed |

## Блок IV — Billing, Sprint 15-20

| Sprint | Пользовательский путь | API/DB contract | Functional gate | Статус |
|---|---|---|---|---|
| 15 | Создать счет по закрытому рейсу и увидеть тег счета | `RRL_BILL_ORDERS`, `PAY_ORDER_ID`; company matches carrier; billing list lightweight read | `test_sprint15_functional.py`, `transport_sprint15_ui_smoke.cjs`, `transport_sprint15_load_test.py`; training pack `wiki-raw/tms2_training/sprint15_billing_open_2026_05_28/` | Passed |
| 16 | Закрыть счет и отметить оплату | `RRL_CLOSE_BILLINGORDER`, `RRL_PAY_BILLINGORDER` via PL/SQL; read-only order GET lightweight | `test_sprint16_functional.py`, `transport_sprint16_ui_smoke.cjs`, `transport_sprint16_load_test.py`; training pack `wiki-raw/tms2_training/sprint16_billing_lifecycle_2026_05_28/` | Passed |
| 17 | Открыть реестр счетов с фильтрами, итогами и CSV | billing list joins by `PAY_ORDER_ID`; filters `company/closed/payed` | `test_sprint17_functional.py`, `transport_sprint17_ui_smoke.cjs`, `transport_sprint17_load_test.py`; training pack `wiki-raw/tms2_training/sprint17_billing_registry_2026_05_28/` | Passed |
| 18 | Пересчитать/задать цену, отвязать рейс | `RRL_UPDATE_PRICE` via PL/SQL; remove uses real rowcount | `test_sprint18_functional.py`, `transport_sprint18_ui_smoke.cjs`, `transport_sprint18_load_test.py`; training pack `wiki-raw/tms2_training/sprint18_price_management_2026_05_28/` | Passed |
| 19 | Добавить рейс к существующему открытому счету той же ТК | precheck order exists; Oracle business messages -> 409 | `test_sprint19_functional.py`, `transport_sprint19_ui_smoke.cjs`, `transport_sprint19_load_test.py`; training pack `wiki-raw/tms2_training/sprint19_link_existing_billing_2026_05_28/` | Passed |
| 20 | Billed-рейс нельзя расформировать или менять состав | `get_task()` returns `PAY_ORDER_ID`; cancel/assign/unassign -> 409 | `test_sprint20_functional.py`, `transport_sprint20_ui_smoke.cjs`, `transport_sprint20_load_test.py`; training pack `wiki-raw/tms2_training/sprint20_billed_task_protection_2026_05_28/` | Passed |

## Блок V — Billing hardening, Sprint 21-30

| Sprint | Пользовательский путь | API/DB contract | Functional gate | Статус |
|---|---|---|---|---|
| 21 | Биллинг-оператор выполняет операции только при профильных правах; отказ 403 виден в UI | `edit_bill_tt`, `calc_tt_price`, `create_tt_price`; protected billing endpoints use billing permissions, read-only endpoints stay view-only | `test_sprint21_functional.py`, `transport_sprint21_ui_smoke.cjs`, `transport_sprint21_load_test.py`; training pack `wiki-raw/tms2_training/sprint21_billing_rbac_2026_05_28/` | Passed |
| 22 | Оператор видит номер платёжного поручения и выбирает ТК из справочника при выставлении счёта | `RRL_BILL_COMPANY`, `RRL_BILL_ORDERS.NUM_PLAT`; companies read cached/lightweight, billing orders include `num_plat` | `test_sprint22_functional.py`, `transport_sprint22_ui_smoke.cjs`, `transport_sprint22_load_test.py`; training pack `wiki-raw/tms2_training/sprint22_company_directory_num_plat_2026_05_28/` | Passed |
| 23 | Оператор открывает счёт, видит все рейсы, итог и выгружает CSV | `GET /billing/orders/{id}/tasks`; unknown order -> 404, existing order without tasks -> `[]` | `test_sprint23_functional.py`, `transport_sprint23_ui_smoke.cjs`, `transport_sprint23_load_test.py`; training pack `wiki-raw/tms2_training/sprint23_billing_order_detail_2026_05_28/` | Passed |
| 24 | Диспетчер перетаскивает СТ между VRP-рейсами, видит пересчёт и может сбросить правку | Client-side `plan.routes[].stops` copy; metrics/history/status remain fast read endpoints | `test_sprint24_functional.py`, `transport_sprint24_ui_smoke.cjs`, `transport_sprint24_load_test.py`; training pack `wiki-raw/tms2_training/sprint24_vrp_drag_drop_2026_05_28/` | Passed |
| 25 | Оператор снимает рейс с открытого счёта из карточки рейса или деталей счёта | `DELETE /billing/orders/{order_id}/tasks/{tt_id}`; closed/payed -> 409; missing link -> 404 | `test_sprint25_functional.py`, `transport_sprint25_ui_smoke.cjs`, `transport_sprint25_load_test.py`; training pack `wiki-raw/tms2_training/sprint25_detach_billing_2026_05_28/` | Passed with seed skips |
| 26 | Оператор выгружает выбранный счёт в Excel | `GET /billing/orders/{id}/export.xlsx`; unknown order -> 404; fallback XLSX без `openpyxl` | `test_sprint26_functional.py`, `transport_sprint26_ui_smoke.cjs`, `transport_sprint26_load_test.py`; training pack `wiki-raw/tms2_training/sprint26_billing_order_xlsx_2026_05_28/` | Passed with content-test skips |
| 27 | Оператор выгружает отфильтрованный реестр счетов в Excel | `GET /billing/orders/export.xlsx`; route before `/{order_id}`; fallback XLSX без `openpyxl` | `test_sprint27_functional.py`, `transport_sprint27_ui_smoke.cjs`, `transport_sprint27_load_test.py`; training pack `wiki-raw/tms2_training/sprint27_billing_registry_xlsx_2026_05_28/` | Passed with content-test skips |
| 28 | Диспетчер выгружает список рейсов в Excel с текущими фильтрами | `GET /tasks/export.xlsx`; route before task-id routes; fallback XLSX без `openpyxl` | `test_sprint28_functional.py`, `transport_sprint28_ui_smoke.cjs`, `transport_sprint28_load_test.py`; training pack `wiki-raw/tms2_training/sprint28_tasks_xlsx_2026_05_28/` | Passed with content-test skips |
| 29 | Диспетчер создаёт рейс из всех свободных СТ района | `POST /clusters/{raion}/create-task`; server-side raion filter; safe negative create returns 404 | `test_sprint29_functional.py`, `transport_sprint29_ui_smoke.cjs`, `transport_sprint29_load_test.py`; training pack `wiki-raw/tms2_training/sprint29_cluster_create_task_2026_05_28/` | Passed |
| 30 | Диспетчер видит live-индикатор загрузки машины в карточке рейса | LoadBar uses `sum(taskSts.PALLETS_COUNT)` vs selected vehicle `PALLETS`; green/amber/red thresholds | `test_sprint30_functional.py`, `transport_sprint30_ui_smoke.cjs`, `transport_sprint30_load_test.py`; training pack `wiki-raw/tms2_training/sprint30_load_bar_2026_05_28/` | Passed |

## Блок VI — Dispatcher UX hardening, Sprint 31+

| Sprint | Пользовательский путь | API/DB contract | Functional gate | Статус |
|---|---|---|---|---|
| 31 | Диспетчер открывает режим «По районам», видит левую панель районов, раскрывает район и открывает диалог создания рейса | `GET /clusters`; карточки используют `RAION/ST_COUNT/PALLET_COUNT/WEIGHT_KG/VOLUME_M3`; `(без района)` сортируется последним | `test_sprint31_functional.py`, `transport_sprint31_ui_smoke.cjs`, `transport_sprint31_load_test.py`; training pack `wiki-raw/tms2_training/sprint31_cluster_sidebar_2026_05_28/` | Passed |
| 32 | Диспетчер видит предупреждение, если паллет в рейсе больше нормы машины | `GET /tasks/{id}/sts`, `GET /vehicles`; warning condition `tripP > vehicle.PALLETS`; LoadBar remains clamped at 100% | `test_sprint32_functional.py`, `transport_sprint32_ui_smoke.cjs`, `transport_sprint32_load_test.py`; training pack `wiki-raw/tms2_training/sprint32_overload_warning_2026_05_28/` | Passed |
| 33 | Диспетчер включает «Кратко» и видит маршрутную таблицу без второстепенных колонок | `GET /tasks` unchanged; hidden columns are client-only state, full mode restores all columns | `test_sprint33_functional.py`, `transport_sprint33_ui_smoke.cjs`, `transport_sprint33_load_test.py`; training pack `wiki-raw/tms2_training/sprint33_routes_brief_mode_2026_05_28/` | Passed |
| 34 | Диспетчер отменяет рейс; СТ освобождаются до удаления рейса | `cancel_task` transaction: select pay order, reject billed, set `RRL_SBORKA_PALLETS.TRANSTASK_ID=NULL`, then `RRL_TRANSPORT_TASK.DELETED=1` | `test_sprint34_functional.py`, `transport_sprint34_ui_smoke.cjs`, `transport_sprint34_load_test.py`; training pack `wiki-raw/tms2_training/sprint34_cancel_releases_st_2026_05_28/` | Passed |
| 35 | Диспетчер создаёт рейс из района без лишней выборки всех СТ | `GET /available-sts` supports `raion`; `(без района)` -> `A.RAION IS NULL`; empty `raion` does not add a filter | `test_sprint35_functional.py`, `transport_sprint35_ui_smoke.cjs`, `transport_sprint35_load_test.py`; training pack `wiki-raw/tms2_training/sprint35_raion_filter_2026_05_28/` | Passed |
| 36 | Диспетчер снимает несколько СТ с рейса одной bulk-операцией | UI sends N `DELETE /tasks/{id}/sts/{st}` calls; backend rejects shipped and billed tasks | `test_sprint36_functional.py`, `transport_sprint36_ui_smoke.cjs`, `transport_sprint36_load_test.py`; training pack `wiki-raw/tms2_training/sprint36_bulk_unassign_2026_05_28/` | Passed |
| 37 | Диспетчер выбирает все видимые СТ и держит экран актуальным автообновлением | Client state `selectedStNums`; polling reloads available STs/tasks/clusters when not blocked by dialog/edit/loading | `test_sprint37_functional.py`, `transport_sprint37_ui_smoke.cjs`, `transport_sprint37_load_test.py`; training pack `wiki-raw/tms2_training/sprint37_select_all_autorefresh_2026_05_28/` | Passed |
| 38 | Диспетчер копирует рейс с реквизитами, но без СТ, цены и счёта | Copy sequence uses `POST /tasks`, optional `PATCH /tasks/{id}`, then `GET /tasks/{id}`; missing PATCH returns 404 | `test_sprint38_functional.py`, `transport_sprint38_ui_smoke.cjs`, `transport_sprint38_load_test.py`; training pack `wiki-raw/tms2_training/sprint38_copy_trip_2026_05_28/` | Passed |
| 39 | Диспетчер видит число активных фильтров и сбрасывает их одним кликом | Client state `activeFilterCount`; reset restores all 11 filter defaults; read endpoint remains fast under filter flips | `test_sprint39_functional.py`, `transport_sprint39_ui_smoke.cjs`, `transport_sprint39_load_test.py`; training pack `wiki-raw/tms2_training/sprint39_filter_badge_reset_2026_05_28/` | Passed |
| 40 | Диспетчер видит дневную сводку по рейсам, паллетам, весу и отгрузкам | Client summary from loaded `tasks`; `PALLET_COUNT/TEMP_WEIGHT` nulls count as 0; no extra API | `test_sprint40_functional.py`, `transport_sprint40_ui_smoke.cjs`, `transport_sprint40_load_test.py`; training pack `wiki-raw/tms2_training/sprint40_day_summary_2026_05_28/` | Passed |
| 41 | Диспетчер фильтрует маршруты по статусам `Все/Активен/Отгружен/Отменён` | Client status filter by `CONDITION`; counters built from loaded `tasks`; no extra API | `test_sprint41_functional.py`, `transport_sprint41_ui_smoke.cjs`, `transport_sprint41_load_test.py`; training pack `wiki-raw/tms2_training/sprint41_routes_status_filter_2026_05_28/` | Passed |
| 42 | Диспетчер получает явное подтверждение успешных операций toast-уведомлением | Client `toastMsg`/`showToast`; success handlers emit message; click dismisses; no silent success | `test_sprint42_functional.py`, `transport_sprint42_ui_smoke.cjs`, `transport_sprint42_load_test.py`; training pack `wiki-raw/tms2_training/sprint42_toast_notifications_2026_05_28/` | Passed |
| 43 | Диспетчер сортирует таблицу рейсов кликом по заголовкам | Client sort by selected field/direction; empty values stay last in asc and desc; no extra API | `test_sprint43_functional.py`, `transport_sprint43_ui_smoke.cjs`, `transport_sprint43_load_test.py`; training pack `wiki-raw/tms2_training/sprint43_sortable_trips_2026_05_28/` | Passed |
| 44 | Диспетчер нажимает Escape, чтобы закрыть диалог или снять выделение | Global key handler priority chain; text inputs are protected, checkbox/radio do not block Escape cleanup | `test_sprint44_functional.py`, `transport_sprint44_ui_smoke.cjs`, `transport_sprint44_load_test.py`; training pack `wiki-raw/tms2_training/sprint44_escape_handler_2026_05_28/` | Passed |
| 45 | Диспетчер переходит от распределённой СТ к её рейсу | `TRANSTASK_ID` truthy -> `#ID →`; `0/null` no button; existing task selected or `GET /tasks/{id}` fetched | `test_sprint45_functional.py`, `transport_sprint45_ui_smoke.cjs`, `transport_sprint45_load_test.py`; training pack `wiki-raw/tms2_training/sprint45_goto_trip_2026_05_28/` | Passed |
| 46 | Диспетчер переключает соседние дни кнопками `◄`/`►` | Shared `shiftDate`; tasks/routes date fields update by ±1 day; endpoint config via shared helpers | `test_sprint46_functional.py`, `transport_sprint46_ui_smoke.cjs`, `transport_sprint46_load_test.py`; training pack `wiki-raw/tms2_training/sprint46_day_step_buttons_2026_05_28/` | Passed |
| 47 | Диспетчер возвращается к сохранённой вкладке, датам и режиму просмотра после reload | `localStorage` keys `tms_filterDate/tms_routeShipDate/tms_viewMode/tms_activeTab`; fallback on storage errors | `test_sprint47_functional.py`, `transport_sprint47_ui_smoke.cjs`, `transport_sprint47_load_test.py`; training pack `wiki-raw/tms2_training/sprint47_localstorage_persistence_2026_05_28/` | Passed |

## Блок VII — Dispatcher UX completion, Sprint 48-95

Sprint 48-95 are implemented in the roadmap and have functional/load test files under `tests/transport/`. Sprint 48-59 are covered with per-sprint Playwright/training packs. Sprint 60-95 now have grouped Playwright coverage via `transport_sprint60_95_ui_smoke.cjs`, fresh functional regression (`245 passed` in the cross-platform proof gate), and plain Python no-mutation load gates using `tests/support/transport_load_runner.py`.

| Sprint | Пользовательский путь | API/DB contract | Functional gate | Статус |
|---|---|---|---|---|
| 48 | Диспетчер сбрасывает дату фильтра на сегодня | Client date state + immediate `GET /tasks?shipment_date=today` reload; API contract unchanged | `test_sprint48_functional.py`, `transport_sprint48_load_test.py`, `transport_sprint48_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint48_today_button_2026_05_29/` | Passed |
| 49 | Диспетчер включает компактный режим таблицы СТ | Client dense class + virtualizer row-height switch; table contract unchanged | `test_sprint49_functional.py`, `transport_sprint49_load_test.py`, `transport_sprint49_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint49_dense_mode_2026_05_29/` | Passed |
| 50 | Полностью собранные СТ получают зелёную полосу | `VERIFY_PERC >= 100` visual rule; selected row suppresses ready highlight | `test_sprint50_functional.py`, `transport_sprint50_load_test.py`, `transport_sprint50_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint50_ready_highlight_2026_05_29/` | Passed |
| 51 | Закреплённая панель выделения показывает count/P/M/V и действия | Client summary from selected ST rows; selected task enables add-to-trip action | `test_sprint51_functional.py`, `transport_sprint51_load_test.py`, `transport_sprint51_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint51_selection_bar_2026_05_29/` | Passed |
| 52 | Диспетчер сортирует таблицу доступных СТ | Client sort over loaded/paged STs; null values stay last in both directions | `test_sprint52_functional.py`, `transport_sprint52_load_test.py`, `transport_sprint52_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint52_st_sorting_2026_05_29/` | Passed |
| 53 | Диспетчер сворачивает/разворачивает панель фильтров | `localStorage.tms_fpCollapsed`; collapsed panel keeps active-filter badge | `test_sprint53_functional.py`, `transport_sprint53_load_test.py`, `transport_sprint53_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint53_filter_panel_collapse_2026_05_29/` | Passed |
| 54 | Диспетчер экспортирует выделенные СТ в CSV | Client CSV over selected ST rows; UTF-8 BOM, semicolon delimiter, totals row | `test_sprint54_functional.py`, `transport_sprint54_load_test.py`, `transport_sprint54_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint54_selected_st_csv_2026_05_29/` | Passed |
| 55 | Тулбар показывает итоги по всем видимым СТ | Client aggregate over `wareFilteredSts`; selected totals remain separate | `test_sprint55_functional.py`, `transport_sprint55_load_test.py`, `transport_sprint55_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint55_visible_totals_2026_05_29/` | Passed |
| 56 | Диспетчер печатает маршрутный лист | Client print window from selected task/STs; empty trips cannot print | `test_sprint56_functional.py`, `transport_sprint56_load_test.py`, `transport_sprint56_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint56_route_sheet_print_2026_05_29/` | Passed |
| 57 | Быстрое добавление СТ по номеру | Existing assign endpoint; client quick-add row; load gate is no-mutation, UI smoke validates POST payload | `test_sprint57_functional.py`, `transport_sprint57_load_test.py`, `transport_sprint57_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint57_quick_add_st_2026_05_29/` | Passed |
| 58 | Развернуть/свернуть все районы в кластерном режиме | Client `expandedRaions` state over loaded clusters | `test_sprint58_functional.py`, `transport_sprint58_load_test.py`, `transport_sprint58_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint58_expand_collapse_clusters_2026_05_29/` | Passed |
| 59 | Быстрый поиск по маршрутам | Client search over loaded tasks by ID, vehicle, driver, region, carrier | `test_sprint59_functional.py`, `transport_sprint59_load_test.py`, `transport_sprint59_ui_smoke.cjs`; training pack `wiki-raw/tms2_training/sprint59_route_search_2026_05_29/` | Passed |
| 60 | Пагинация таблицы доступных СТ по 100 строк | `ST_PAGE_SIZE = 100`; page/global index contract | `test_sprint60_functional.py`, `transport_sprint60_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 61 | Быстрый фильтр по складу | Client warehouse filter resets page/selection | `test_sprint61_functional.py`, `transport_sprint61_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 62 | Sticky header таблицы СТ | CSS sticky inside `.dispatch-st-section` | `test_sprint62_functional.py`, `transport_sprint62_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 63 | Значок количества несобранных СТ | Client count from `VERIFY_PERC` | `test_sprint63_functional.py`, `transport_sprint63_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 64 | Клик по значку выделяет все несобранные | Client selection over unready STs | `test_sprint64_functional.py`, `transport_sprint64_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 65 | Вкладка «Заявки» показывает число выделенных | Client tab badge from selected set | `test_sprint65_functional.py`, `transport_sprint65_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 66 | `VERIFY_PERC` отображается в составе рейса | Task ST row includes readiness bar | `test_sprint66_functional.py`, `transport_sprint66_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 67 | Несобранные строки состава подсвечены amber | `VERIFY_PERC < 100` visual rule | `test_sprint67_functional.py`, `transport_sprint67_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 68 | `Ctrl+Enter` добавляет выделенные СТ в рейс | Existing assign endpoint; keyboard handler | `test_sprint68_functional.py`, `transport_sprint68_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 69 | `Delete` снимает выбранные СТ с рейса | Existing unassign endpoint; keyboard handler | `test_sprint69_functional.py`, `transport_sprint69_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 70 | «Все»/«Нет» управляют выделением состава рейса | Client selected trip ST set | `test_sprint70_functional.py`, `transport_sprint70_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 71 | Sticky header таблицы рейсов | CSS sticky inside routes wrapper | `test_sprint71_functional.py`, `transport_sprint71_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 72 | Inline-фильтр по СТ/адресу в составе рейса | Client filter over selected task STs | `test_sprint72_functional.py`, `transport_sprint72_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 73 | Колонка «Логист» в таблице рейсов | `LOGIST` field from task list | `test_sprint73_functional.py`, `transport_sprint73_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 74 | Состав рейса сворачивается/разворачивается | Client expanded detail state | `test_sprint74_functional.py`, `transport_sprint74_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 75 | Итоги заголовка рейса показывают объём | `VOLUME_M3` aggregate | `test_sprint75_functional.py`, `transport_sprint75_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 76 | Состав рейса показывает `VOLUME_M3` | Task ST row field | `test_sprint76_functional.py`, `transport_sprint76_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 77 | Состав рейса экспортируется в CSV | Client CSV over task STs | `test_sprint77_functional.py`, `transport_sprint77_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 78 | Фильтры нераспределённые/собранные сохраняются | `localStorage` filter keys | `test_sprint78_functional.py`, `transport_sprint78_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 79 | Таблица рейсов показывает ТК | `TK_NAME` field | `test_sprint79_functional.py`, `transport_sprint79_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 80 | Таблица доступных СТ показывает направление | `NAPR` field | `test_sprint80_functional.py`, `transport_sprint80_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 81 | Клавиатурная навигация по рейсам | Client selected task navigation | `test_sprint81_functional.py`, `transport_sprint81_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 82 | Готовность и даты сохраняются корректно | `VERIFY_PERC >= 100`, persisted `stDate/dateTo` | `test_sprint82_functional.py`, `transport_sprint82_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 83 | Несобранные доступные СТ получают amber border | `VERIFY_PERC < 100` visual rule | `test_sprint83_functional.py`, `transport_sprint83_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 84 | Таблица маршрутов показывает `% сборки` | `READY_PERC` field | `test_sprint84_functional.py`, `transport_sprint84_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 85 | Вкладка маршрутов показывает сводку | Client aggregate over route tasks | `test_sprint85_functional.py`, `transport_sprint85_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 86 | Вкладка маршрутов экспортируется в CSV | Client CSV over route table | `test_sprint86_functional.py`, `transport_sprint86_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 87 | Закрытие рейса предупреждает о несобранных СТ | Close confirmation includes unready count | `test_sprint87_functional.py`, `transport_sprint87_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 88 | Рейс переносится на следующий день | `PATCH /tasks/{id}` shipment date update | `test_sprint88_functional.py`, `transport_sprint88_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 89 | Состав рейса фильтруется по несобранным | Client filter by `VERIFY_PERC` | `test_sprint89_functional.py`, `transport_sprint89_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 90 | Номер СТ копируется в буфер | Clipboard action in ST rows | `test_sprint90_functional.py`, `transport_sprint90_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 91 | Состав рейса сортируется по временным окнам | Client sort by time window | `test_sprint91_functional.py`, `transport_sprint91_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 92 | Все номера СТ состава копируются в буфер | Clipboard action over task STs | `test_sprint92_functional.py`, `transport_sprint92_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 93 | Сводка дня считает пустые рейсы | Client count where task has no STs | `test_sprint93_functional.py`, `transport_sprint93_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 94 | Рейсы с несобранными СТ подсвечены amber border | `UNREADY_COUNT/READY_PERC` visual rule | `test_sprint94_functional.py`, `transport_sprint94_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |
| 95 | Примечание рейса показывается tooltip при наведении | `PRIMECHANIE` tooltip | `test_sprint95_functional.py`, `transport_sprint95_load_test.py`, `transport_sprint60_95_ui_smoke.cjs` | Fresh functional/load/UI passed 2026-05-29 |

## Инфраструктурные и NFR решения

| Требование | Решение | Gate |
|---|---|---|
| OSRM/Valhalla infrastructure | Добавлены `docker-compose.osrm.yml`, `docker-compose.valhalla.yml`; backend probes use real OSRM route endpoint and Valhalla `/status`; `/routing/status` exposes active provider and availability flags. | `test_routing_infrastructure.py`; `scripts/tms2-routing-smoke.ps1`; live smoke after starting containers |
| Таблица СТ, 2000 строк | Принята фактическая Sprint 102 модель: `@tanstack/react-virtual` по полному списку доступных СТ; Sprint 60 pagination остается историческим контрактом, но текущий UI держит bounded DOM через virtualizer, top/bottom spacers и стабильный scroll. | `test_frontend_virtualization_nfr.py`; frontend build; `node tests\ui\transport_table_2000_nfr_smoke.cjs` -> first render 777 ms, rendered rows 31/43/33 |
| WebSocket `/ws/dispatch` | **Реализован Sprint 96.** `ws_manager.py` — ConnectionManager, broadcast_sync из sync endpoints. Клиент: exponential backoff reconnect 1→30s, обновление tasks/STs по событиям. | `test_sprint96_functional.py`; `transport_sprint96_ui_smoke.cjs` |
| SSE VRP progress | **Реализован Sprint 101.** `POST /planner/solve` → `{job_id, stream_url}`; `GET /planner/solve/{id}/stream` — SSE; `DELETE /planner/solve/{id}` — отмена; 60s timeout watchdog. | `test_sprint101_102_functional.py` |

## Блок VII — Фаза 3: Инфраструктура и расширения (Спринты 96–119)

| Sprint | Пользовательский путь | API/DB contract | Functional gate | Статус |
|---|---|---|---|---|
| 96 | Несколько диспетчеров видят изменения друг друга без F5; индикатор ● WS в хедере | `WS /ws/dispatch`; `broadcast_sync` после каждой мутации; reconnect 1→30s | `test_sprint96_functional.py`; `transport_sprint96_ui_smoke.cjs` | Passed (unit) |
| 97-98 | Администратор добавляет/редактирует/удаляет ТС и водителей из веб-интерфейса | `POST/PATCH/DELETE /vehicles`, `/drivers`; migrations 055-056 (Oracle packages); TRANSPORT_FLEET_EDIT permission | `test_sprint97_98_functional.py`; `transport_sprint97_98_ui_smoke.cjs` | Passed (unit) |
| 99-100 | Администратор видит пользователей, группы, права; добавляет права группам через чекбоксы | `GET /users`, `/groups`, `/rights`; `POST/DELETE /groups/{g}/rights`; `RIGHTS_ADMIN_VIEW/EDIT` | `test_sprint99_100_functional.py`; `transport_sprint99_100_ui_smoke.cjs` | Passed (unit) |
| 101 | Диспетчер нажимает «Отмена» во время VRP-solve; OR-Tools останавливается | `POST /planner/solve → {job_id}`; `GET /solve/{id}/stream` SSE; `DELETE /solve/{id}`; 60s timeout | `test_sprint101_102_functional.py` | Passed (unit) |
| 102 | Таблица СТ с 2000+ строками рендерится за ≤300 мс через react-virtual | `@tanstack/react-virtual` useVirtualizer; пагинация удалена; paddingTop/Bottom spacers | `test_sprint101_102_functional.py` | Passed (unit) |
| 103-104 | Водитель открывает ?page=driver, видит свои рейсы, нажимает «Начать» / «Готово» | `GET /api/driver/trips`; `POST /ops/{id}/start,done`; auth via driver_id param | `test_sprint103_107_functional.py`; `transport_sprint103_ui_smoke.cjs` | Passed (unit) |
| 105 | Водитель работает без сети; операции синхронизируются при восстановлении | `driver-sw.js` Service Worker; IndexedDB pending_ops; Background Sync tag | `test_sprint103_107_functional.py` | Passed (unit) |
| 106-107 | Диспетчер получает browser push / email при VRP-готовности и готовности рейса | `POST /notifications/subscribe`; pywebpush VAPID; SMTP graceful fallback | `test_sprint103_107_functional.py` | Passed (unit) |
| 108-109 | Руководство видит утилизацию парка, топ регионов, расходы по ТК за период | `GET /kpi/fleet,summary,regions,billing,billing/by-company?date_from&date_to` | `test_sprint108_114_functional.py`; `transport_sprint108_109_ui_smoke.cjs` | Passed (unit) |
| 110-111 | GPS-трекер присылает координаты; на карте видны live-иконки машин, обновление 30 сек | `POST /api/gps/track`; UPSERT RRL_VEHICLE_GPS_LAST; migration 060; `GET /vehicles/positions` | `test_sprint108_114_functional.py` | Passed (unit) |
| 112-114 | Администратор видит тарифы ТС; экспортирует счёт в 1С XML; архивирует старые рейсы | `/tariffs/table-info`; `/billing/orders/{id}/export/1c` CommerceML 2.09 XML; `/maintenance/archive?dry_run=true` | `test_sprint108_114_functional.py` | Passed (unit) |
| 115-117 | Диспетчер выбирает «AI-решатель» — OR-Tools заменяется Attention Model PyTorch | `solver=attention_model`; `am_solver.py`; graceful fallback → OR-Tools если нет модели | `test_sprint115_119_functional.py` | Passed (unit) |
| 118-119 | GPS-въезд в геозону магазина → авто-отметка UNLOAD fact_start; выезд → fact_end | `haversine_m`; `check_geofences`; migration 062 GEO_FENCE_RADIUS_M; `[GPS-auto]` в NOTE | `test_sprint115_119_functional.py` | Passed (unit) |

## Release gate для Sprint 1-20

Минимальный контроль:

```powershell
python -m pytest tests\transport\test_sprint1_functional.py tests\transport\test_sprint2_functional.py tests\transport\test_sprint3_functional.py tests\transport\test_sprint4_functional.py tests\transport\test_sprint5_functional.py tests\transport\test_sprint6_functional.py tests\transport\test_sprint7_functional.py tests\transport\test_sprint8_functional.py tests\transport\test_sprint9_functional.py tests\transport\test_sprint10_functional.py tests\transport\test_sprint11_functional.py tests\transport\test_sprint12_functional.py tests\transport\test_sprint13_functional.py tests\transport\test_sprint14_functional.py tests\transport\test_sprint15_functional.py tests\transport\test_sprint16_functional.py tests\transport\test_sprint17_functional.py tests\transport\test_sprint18_functional.py tests\transport\test_sprint19_functional.py tests\transport\test_sprint20_functional.py tests\transport\test_routing_infrastructure.py tests\transport\test_frontend_virtualization_nfr.py -q -ra --tb=short
```

Current strict local result on 2026-05-29 after Phase 3 migrations (055-062) applied: `scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeSprint60To95 -IncludeUiSmoke -IncludeLoadSmoke` -> core **`427 passed`**, Sprint 60-95 **`234 passed`**, load/UI/NFR passed, **no pytest skips**.

Спринты 96–119 добавлены в release gate. Seed date: **2026-05-24** (актуальные свободные СТ в dev Oracle).

Полный release gate дополнительно требует:

- Sprint 1-3 functional/UI/load tests are now present and must be included in the final command;
- deterministic dated seed без skips для dispatcher, map, and billing fixture flows: covered by seed date `2026-05-24`, Sprint 9 historical template `PLAN_DATE=2026-05-23`, and explicit narrow legacy billing fixture date ranges;
- historical `RRL_PLANNER_PLANS` template fixture for Sprint 9: covered by `055_apply.sql`;
- non-empty Sprint 8 VRP apply acceptance with `TMS_RUN_MUTATING_VRP_APPLY=1`: verified separately on 2026-05-29, `23 passed`; active `vrp_auto` transport tasks for the seed date remained `0`;
- ручной Oracle/prod apply checklist для migrations 051-054;
- routing infrastructure smoke: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-routing-smoke.ps1`;
- combined strict release gate runner: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeSprint60To95 -IncludeUiSmoke -IncludeLoadSmoke`;
- mandatory slow SQL/SKV review after each gate: see `wiki/runbooks/slow_sql_review.md`;
- NFR table rendering smoke on a 2000-row mocked or seeded dataset;
- frontend smoke на `http://127.0.0.1:3000`, без порта `3001`.
