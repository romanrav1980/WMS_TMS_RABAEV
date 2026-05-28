# ТМС-2 — матрица приемки

Дата обновления: 2026-05-28.

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
| 1 | Диспетчер открывает таблицу СТ, видит 16 колонок, фильтрует по дате/складу/адресу/типу ТС | `GET /available-sts`; реальные поля `RRL_V_AVAILABLE_STS`; быстрый empty-date path | Нужен отдельный Sprint 1 test; сейчас частично через Sprint 4-7 | Gap |
| 2 | Выделить несколько СТ, увидеть итоги, создать рейс | `POST /tasks`, `POST /tasks/{id}/sts`; Oracle `RRL_TRANSPORT_TASK`, `RRL_TT_ADD_PALL` | Нужен отдельный Sprint 2 test; частично Sprint 4 | Gap |
| 3 | Открыть вкладку маршрутов, увидеть рейс и состав | `GET /tasks`, `GET /tasks/{id}/sts`; uppercase response keys | Нужен отдельный Sprint 3 test; частично Sprint 4/6 | Gap |
| 4 | Редактировать рейс, закрыть, отменить, назначить/снять СТ | `PATCH /tasks/{id}`, `close`, `cancel`; пустой рейс закрыть нельзя | `test_sprint4_functional.py` | Passed with seed skips |
| 5 | Видеть готовность сборки и требования к ТС | readiness functions, transport type columns | `test_sprint5_functional.py` | Passed with seed skips |
| 6 | Открыть паллеты СТ, менять load type/order | `GET /sts/{st}/pallets`; без несуществующего `SP.DELETED` | `test_sprint6_functional.py` | Passed with seed skips |

## Блок II — MAP / VRP, Sprint 7-10

| Sprint | Пользовательский путь | API/DB contract | Functional gate | Статус |
|---|---|---|---|---|
| 7 | Открыть карту заказов с геокодированными маркерами | `GET /planner/orders`, `GET /routing/status`; `RRL_ADDR` coordinates | `test_sprint7_functional.py`, `transport_sprint7_load_test.py`, `transport_sprint7_ui_smoke.cjs` | Fresh hardening passed: `14 passed`, load NFR passed, UI smoke passed |
| 8 | Rebuild matrix -> solve VRP -> apply plan -> получить рейсы с назначенными СТ | `RRL_ADDR_DISTANCE_MATRIX.DISTANCE_KM/UPDATED_AT`; `RRL_PLANNER_PLANS.PAYLOAD`; no partial-success apply | `test_sprint8_functional.py`, `transport_sprint8_load_test.py`, `transport_sprint8_ui_smoke.cjs` | Fresh hardening passed: `23 passed`, non-empty plan required, load NFR passed, UI smoke passed; mutating apply full-flow is optional via env |
| 9 | Смотреть кластеры/шаблоны/историю похожих планов | planner history/templates tables | `test_sprint9_functional.py`, `transport_sprint9_load_test.py`, `transport_sprint9_ui_smoke.cjs` | Fresh hardening passed with one backend seed skip: cluster/RAION/load/UI passed; historical-template Oracle fixture still needed |
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

## Release gate для Sprint 1-20

Минимальный контроль:

```powershell
python -m pytest tests\transport\test_sprint4_functional.py tests\transport\test_sprint5_functional.py tests\transport\test_sprint6_functional.py tests\transport\test_sprint7_functional.py tests\transport\test_sprint8_functional.py tests\transport\test_sprint9_functional.py tests\transport\test_sprint10_functional.py tests\transport\test_sprint11_functional.py tests\transport\test_sprint12_functional.py tests\transport\test_sprint13_functional.py tests\transport\test_sprint14_functional.py tests\transport\test_sprint15_functional.py tests\transport\test_sprint16_functional.py tests\transport\test_sprint17_functional.py tests\transport\test_sprint18_functional.py tests\transport\test_sprint19_functional.py tests\transport\test_sprint20_functional.py -q -ra --tb=short
```

Текущий результат dev: `211 passed, 21 skipped`.

Полный release gate дополнительно требует:

- отдельные Sprint 1-3 functional tests;
- deterministic dated seed без skips для dispatcher и map flows;
- non-empty Sprint 8 VRP apply acceptance;
- ручной Oracle/prod apply checklist для migrations 051-054;
- frontend smoke на `http://127.0.0.1:3000`, без порта `3001`.
