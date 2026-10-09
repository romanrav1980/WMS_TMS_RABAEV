# NICORA: каталог доработок существующей WMS/TMS

Минимум 80% ресурсов на создание функционала. Дополнительные тестовые прогоны остановлены поручением владельца. Существующие WMS/TMS и схема RABAEV — основа доработок. Старые сценарии сохранены как требования к результату, не поручение запускать проверки.

[Глобальный анализ текущего продукта](../../components/nicora_global_reuse_analysis_20261007.md). Основной план — [NI01–NI08 revision 10](implementation_plan.md); прежние назначения NI04–NI06 заменены. NI01 — baseline with gaps; NI02 manual SAP–ST bridge установлен; следующая функция NI03 — товарные эффекты заданий. NI04 завершает существующую вложенность SSCC. 68 ID сохранены как каталог объёма; NS01–NS04 ведутся с функцией, NS05 не блокирует работу.

## Рабочий входящий поток SAP → паллеты → хранение

| Карточка | Существующая основа | Доработка |
|---|---|---|
| [NS08: Атомарная команда и защита от повторов](sprints/ns08.md) | db.py, oracle_gateway.py, api_audit.py | Использовать gateway.transaction с общим cursor для составной команды; убрать отдельные commit и защитить повтор адресно. |
| [NS09: Приём и отправка интеграционных сообщений](sprints/ns09.md) | production_exchange_service.py, outbox_service.py, traceability_service.py | Расширить существующий журнал/inbox-outbox сообщениями SAP retail; production JSON не равен SAP контракту. |
| [NS13: Доработка: Карточка SKU и проверка упаковки](sprints/ns13.md) | finished_goods_service.py, raw_material_service.py, tserver_service.py | Расширить существующие SKU settings несколькими применимыми профилями табака/CRPT/ЕГАИС/других систем; сохранить GTIN и упаковки. |
| [NS14: Доработка: Подсклады, ячейки и правила обращения](sprints/ns14.md) | warehouse_topology_service.py, warehouse_map_service.py, picking_service.py | Настроить существующие подсклады/ячейки/pick faces; добавить ёмкость, условия и направление маршрута NICORA. |
| [NS15: Доработка: Магазины, тара и вместимость автомобилей](sprints/ns15.md) | customer_order_service.py, customer_rule_service.py, transport_service.py | Доработать существующие магазины/адреса/машины: календарь, типы тары, вместимость и температурные ограничения. |
| [NS16: Доработка: Обмен справочниками ERP](sprints/ns16.md) | production_exchange_service.py, outbox_service.py, traceability_service.py | Подключить SAP источник к существующим справочникам/журналам; регуляторные адаптеры добавлять по применимому профилю. |
| [NS17: Доработка: Приём заказов ERP](sprints/ns17.md) | customer_order_service.py, customer_rule_service.py, transport_service.py | Доработать customer order import для SAP: неизменность заказа, календарь, поздний заказ и дедупликация. |
| [NS18: Доработка: Приёмка и доступность в экспедиции](sprints/ns18.md) | Form1.cs, RRL_ACCEPT_ORDER2_3_FUNCTION.sql, finished_goods_service.py | Добавить современную приёмку на существующих приходах/паллетах: основание SAP, партия/срок/SSCC, фактическая укладка, марки либо разрешённые агрегации. |
| [NS19: Доработка: Слотирование и правила партий](sprints/ns19.md) | warehouse_topology_service.py, warehouse_map_service.py, picking_service.py | Доработать pick face/SKU mapping: партии, смешение только отбора, резерв диапазона и переход на новый диапазон. |
| [NS23: Доработка: Грузовое место и вложенные идентификаторы](sprints/ns23.md) | production_service.py, RRL_PRODUCTION_API_PACKAGE_BODY.sql, RRL_REGULATORY_API_PACKAGE_BODY.sql | Расширить паллеты/агрегации составом HU/заказов и версиями по системам; физическое количество считать один раз. |
| [NS30: Доработка: Сотрудники, техника и смены](sprints/ns30.md) | resource_management_service.py, warehouse_tasks.py | Настроить существующие resource/session/shift/equipment под роли NICORA и ранние смены. |
| [NS31: Доработка: Назначение задания и терминал исполнителя](sprints/ns31.md) | warehouse_task_service.py, warehouse_task_domain_sync_service.py, reachtruck-tsd.js | Доработать очередь и reachtruck TSD: квалификация, приоритет, сканы, безопасная передача и server-saved марки. |
| [NS20: Доработка: Размещение и выбор источника пополнения](sprints/ns20.md) | warehouse_task_service.py, warehouse_task_domain_sync_service.py, reachtruck-tsd.js | Добавить receipt putaway handler в существующие задания: пригодный адрес по времени пополнения до отбора, проводка остатка и марок при завершении. |

## Задание TMS → волна → резерв → пополнение

| Карточка | Существующая основа | Доработка |
|---|---|---|
| [NS21: Доработка: Мягкий резерв потребности](sprints/ns21.md) | stock_reservation_service.py, picking_service.py, RRL_PICK_WAVE_API_PACKAGE_BODY.sql | Доработать существующий SOFT резерв общего пула заказов по доступному количеству и блокировкам марок. |
| [NS22: Доработка: Распределение дефицита](sprints/ns22.md) | stock_reservation_service.py, picking_service.py, RRL_PICK_WAVE_API_PACKAGE_BODY.sql | Добавить алгоритм дефицита по кратностям, округлению и очередности отгрузки в существующее распределение. |
| [NS24: Доработка: Транспортный план и задание на сборку](sprints/ns24.md) | transport_service.py, TransportDispatchPage.tsx, transport.py | Доработать существующий рейс/СТ: плановые масса, объём, тара, температура и задание на сборку, связь с HU. |
| [NS25: Доработка: Волны по подскладам и срокам](sprints/ns25.md) | picking_service.py, case_pick_service.py, wave-replenishment.js | Создавать действующие waves из задания TMS по подскладу/сроку; добавить операционный день ночной смены. |
| [NS26: Доработка: Жёсткий резерв волны](sprints/ns26.md) | stock_reservation_service.py, picking_service.py, RRL_PICK_WAVE_API_PACKAGE_BODY.sql | Сохранить SOFT→HARD в RRL_PICK_WAVE_API; уточнить общий баланс, фактический фреш и исключительность маркированных единиц. |
| [NS27: Доработка: Пополнение мини-макс](sprints/ns27.md) | picking_service.py, case_pick_service.py, wave-replenishment.js | Доработать действующую mini-max очередь по ёмкости и открытым подачам; один источник/warehouse task. |
| [NS28: Доработка: Пополнение под волну целым поддоном](sprints/ns28.md) | picking_service.py, case_pick_service.py, wave-replenishment.js | Расширить текущую подачу под волну: целая паллета, свободные слоты/резервный отбор и баланс с mini-max. |
| [NS29: Доработка: Частичное пополнение категории B](sprints/ns29.md) | picking_service.py, case_pick_service.py, wave-replenishment.js | Добавить категорию B к partial movement: свободная ёмкость, остаток паллеты и перенесённые марки. |
| [NS32: Доработка: Разрешение волны и монитор препятствий](sprints/ns32.md) | picking_service.py, case_pick_service.py, wave-replenishment.js | Доработать get_wave_readiness/launch: полная обеспеченность, завершение пополнения и причины препятствий. |
| [NS33: Доработка: Прогноз загрузки склада](sprints/ns33.md) | resource_management_service.py, warehouse_tasks.py | Подключить реальные waves/tasks/resources к прогнозу нагрузки вместо replay; перенос сроков через действующие планы. |

## Отбор → состав → контроль → выпуск

| Карточка | Существующая основа | Доработка |
|---|---|---|
| [NS34: Доработка: Стеллажная комплектация и состав места](sprints/ns34.md) | case_pick_service.py, tserver_service.py, useScanInput.ts | Доработать confirm_line и клиентскую паллету: односторонний маршрут, партии, марки и план укладки. |
| [NS35: Доработка: Весовая коробка по штрихкоду](sprints/ns35.md) | case_pick_service.py, tserver_service.py, useScanInput.ts | Добавить весовой ШК к существующему scanner/product lookup и фактическую массу идентифицированной упаковки. |
| [NS36: Доработка: Комплектация на весах и накидывание](sprints/ns36.md) | case_pick_service.py, tserver_service.py, useScanInput.ts | Дополнить текущий отбор весовым постом и накидыванием, допуском заказа и точным составом марок. |
| [NS37: Доработка: Пикбайлайн из экспедиции приёмки](sprints/ns37.md) | case_pick_service.py, tserver_service.py, useScanInput.ts | Добавить pick-by-line к действующему отбору: источник приёмки, распределение магазинам и состав. |
| [NS38: Доработка: Срочная инвентаризация пустой ячейки](sprints/ns38.md) | warehouse_task_service.py, warehouse_task_domain_sync_service.py, reachtruck-tsd.js | Добавить срочную инвентаризацию пустого pick face как вид действующего задания с решением КРО. |
| [NS39: Доработка: Срочное восстановление отбора](sprints/ns39.md) | warehouse_task_service.py, warehouse_task_domain_sync_service.py, reachtruck-tsd.js | Связать shorts, пополнение и задания восстановления в срочную цепочку с одним товарным эффектом. |
| [NS40: Доработка: Малая тара поштучного отбора](sprints/ns40.md) | case_pick_service.py, tserver_service.py, useScanInput.ts | Расширить pallet types/состав заказа малой тарой и связью с родительским HU без двойного учёта. |
| [NS41: Доработка: Весовой контроль и разрешение отгрузки](sprints/ns41.md) | tserver_service.py, REMAINS_PACKAGE_BODY.sql, App.tsx | Расширить весовой контроль: тара, допуски, версия состава и блокировки выпуска по маркировке. |
| [NS42: Доработка: Проверка состава после ошибки веса](sprints/ns42.md) | tserver_service.py, REMAINS_PACKAGE_BODY.sql, App.tsx | Доработать lot/place audit: отдельный проход после ошибки веса, роли и точные марки. |
| [NS43: Доработка: Исправление и повторный выпуск](sprints/ns43.md) | tserver_service.py, REMAINS_PACKAGE_BODY.sql, App.tsx | Добавить версию исправленного состава и повторный выпуск в текущий аудит, отменив прежнее разрешение. |
| [NS44: Доработка: Выборочная проверка перепикиванием](sprints/ns44.md) | tserver_service.py, REMAINS_PACKAGE_BODY.sql, App.tsx | Расширить существующее перепикивание правилами выборки и профилем SKU. |

## Консолидация → погрузка → выезд → магазин

| Карточка | Существующая основа | Доработка |
|---|---|---|
| [NS45: Доработка: Консолидация по упаковочному листу](sprints/ns45.md) | production_service.py, RRL_PRODUCTION_API_PACKAGE_BODY.sql, RRL_REGULATORY_API_PACKAGE_BODY.sql | Связать упаковочный лист с HU/aggregation составом; добавить комплектность и переупаковку. |
| [NS46: Доработка: Экспедиция и развозка к воротам](sprints/ns46.md) | warehouse_task_service.py, warehouse_task_domain_sync_service.py, reachtruck-tsd.js | Расширить warehouse tasks перемещением экспедиции к воротам и рейсу; план отделить от факта. |
| [NS47: Доработка: Подтверждение погрузки в автомобиль](sprints/ns47.md) | transport_service.py, TransportDispatchPage.tsx, transport.py | Добавить факт погрузки HU в машину; не обходить обязательный контроль при ошибке can_print. |
| [NS48: Доработка: Ожидание рейса и перенос грузов](sprints/ns48.md) | transport_service.py, TransportDispatchPage.tsx, transport.py | Разделить готов/погружен/выехал и закрытие рейса; перенос груза после подтверждённой выгрузки. |
| [NS49: Доработка: Приёмка магазина по штрихкоду](sprints/ns49.md) | driver_mobile.py, DriverMobilePage.tsx, transport_service.py | Доработать DriverMobilePage приёмкой магазина по HU/ШК и фактическому составу отдельно от закрытия рейса. |

## Кросс-док, возвраты и тара

| Карточка | Существующая основа | Доработка |
|---|---|---|
| [NS51: Доработка: Межскладские плечи и кросс-док](sprints/ns51.md) | CROSS_DOCKING_PACKAGE_BODY.sql, transport_service.py | Добавить два плеча/консолидацию поверх TMS/HU; legacy SYNC_* не считать готовым процессом. |
| [NS52: Доработка: Приёмка магазина по весу и фото](sprints/ns52.md) | driver_mobile.py, DriverMobilePage.tsx, transport_service.py | Добавить вес/несколько фото/акт к приёмке магазина; готовность всего сценария не установлена. |
| [NS53: Доработка: Поиск потери и расследование](sprints/ns53.md) | warehouse_task_service.py, warehouse_task_domain_sync_service.py, reachtruck-tsd.js | Связать task/short/audit в расследование потери с ролями, сроками и конкретными марками. |
| [NS54: Доработка: Возврат товара и склада брака](sprints/ns54.md) | Form1.cs, RRL_ACCEPT_ORDER2_3_FUNCTION.sql, finished_goods_service.py | Добавить SAP возврат на существующий приход/остаток: разрешение, исправная коробка/брак/поставщик и жизненный цикл марки. |
| [NS55: Доработка: Оборотная тара по типам](sprints/ns55.md) | driver_mobile.py, DriverMobilePage.tsx, transport_service.py | Расширить return operations балансом тары по типу/машине/магазину; полноценный реестр пока не установлен. |

## Затраты, закрытие дня и оптимизация

| Карточка | Существующая основа | Доработка |
|---|---|---|
| [NS56: Доработка: Ежедневные нормативные затраты](sprints/ns56.md) | transport_service.py, BillingTransport.cs | Дополнить действующие ставки/расчёт рейса нормативными складскими операциями и стоимостью коробки/точки/выгрузки. |
| [NS57: Доработка: Дополнительные расходы и пересчёт ставок](sprints/ns57.md) | transport_service.py, BillingTransport.cs | Расширить billing orders допрасходами, согласованием и распределением; не создавать второй счёт. |
| [NS58: Доработка: Сверка отгрузки и закрытие дня](sprints/ns58.md) | transport_service.py, TransportDispatchPage.tsx, transport.py | Доработать закрытие дня сверкой HU/рейсов/остатков/ERP/марок и причин неотгрузки, сохраняя факты. |
| [NS59: Доработка: Рекомендации динамических диапазонов](sprints/ns59.md) | warehouse_topology_service.py, warehouse_map_service.py, picking_service.py | Добавить рекомендации диапазона на существующие pick face mappings и статистику с утверждением/вымыванием. |
| [NS60: Доработка: Автопланирование через общий контроль](sprints/ns60.md) | vrp_solver.py, distance_matrix_service.py, TransportPlannerPage.tsx | Расширить действующий solver общим валидатором ручного/авто-плана NICORA и объяснением исключений. |

## Выпуск/пилоты после функционала

| Карточка | Существующая основа | Доработка |
|---|---|---|
| [NS06: Воспроизводимое промышленное развёртывание](sprints/ns06.md) | db.py, oracle_gateway.py, api_audit.py | Использовать текущую установку; startup без reload и production упаковка перед выпуском. |
| [NS07: Пул Oracle и аудит без блокирования API](sprints/ns07.md) | db.py, oracle_gateway.py, api_audit.py | Доработать действующий pool/audit адресно по нужде сценария; не заменять gateway целиком. |
| [NS10: Надёжное фоновое исполнение](sprints/ns10.md) | production_exchange_service.py, outbox_service.py, traceability_service.py | Доработать существующий worker: возврат просроченного lease, повторы и очередь ошибок. |
| [NS11: Монитор технического состояния](sprints/ns11.md) | db.py, oracle_gateway.py, api_audit.py | Добавить нужные причины блокировки и очереди к существующим журналам API/SQL/outbox. |
| [NS12: Хранение истории и архив](sprints/ns12.md) | production_exchange_service.py, outbox_service.py, traceability_service.py | Ограничить чтение журналов и архивировать историю с сохранением связей документов и кодов. |
| [NS50: Сквозная репетиция сухого потока](sprints/ns50.md) | nicora_approved_code_analysis.md | Собрать доработанные экраны в сухой бизнес-поток; новые прогоны сейчас не запускать. |
| [NS61: Резервирование и восстановление среды](sprints/ns61.md) | db.py, oracle_gateway.py, api_audit.py | Подготовить восстановление существующей ORCL/RABAEV и файлов перед промышленным выпуском. |
| [NS62: Нагрузка миллионов операций](sprints/ns62.md) | db.py, oracle_gateway.py, api_audit.py | Большую нагрузку отложить до рабочего функционала и отдельного этапа; разработку не блокировать. |
| [NS63: Полная ночная смена и приёмочный набор](sprints/ns63.md) | nicora_approved_code_analysis.md | Полную приёмочную смену сохранить перед выпуском; не проводить вместо разработки. |
| [NS64: Наблюдаемый пилот сухого подсклада](sprints/ns64.md) | nicora_approved_code_analysis.md | Пилот сухого подсклада после готовности потока и решения владельца. |
| [NS65: Пилот фреша и межскладского потока](sprints/ns65.md) | nicora_approved_code_analysis.md | Пилот фреша/межскладского потока после реализации и решения владельца. |
| [NS66: Инструкции и управляемый запуск](sprints/ns66.md) | nicora_approved_code_analysis.md | Инструкции по фактическим рабочим функциям; GPU/model qualification не prerequisite запуска. |
| [NS67: Закрытие полного объёма NICORA](sprints/ns67.md) | nicora_approved_code_analysis.md | Закрывать объём по фактическим функциям и нерешённым требованиям редакции 57, не числу карточек. |

Нагрузочные смены/пилоты — после рабочего функционала. Новые испытания не запускаются. Прежние 175–304 дня — архивная оценка, не текущий прогноз. Технические NS07/NS10 выполняются раньше только при необходимости конкретного сценария.
