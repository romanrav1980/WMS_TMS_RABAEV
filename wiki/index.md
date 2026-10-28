# TMS Wiki Index

- 2026-10-28: A local, unapplied candidate for an atomic multi-order root-HU shipment exists under `db/migrations/2026-10-28_multi_order_root_hu_shipping/`. When a child CASE requires final weight, the composite plan accepts explicit manual QC only; one electronic CASE capture is refused until per-CASE captures are implemented. Oracle compilation and live fixture evidence remain required.
- 2026-10-28: The intact root HU test contains CASEs for two orders of one recipient. Outgoing QC stops at `SHIPMENT_CUSTOMER_ORDER_AMBIGUOUS`; the planned atomic per-CASE shipping branch is documented in [the execution plan](roadmap/tradecase_execution_20261019.md). No load, departure or store receipt is accepted.

Короткий вход в проект. Открывать только страницы по текущему вопросу. Исторические статусы и полный каталог сохранены в [архиве оглавления](sources/wiki_index_catalog_20261015.md); они не заменяют актуальную карточку компонента.

## Текущая работа

- 28.10: T06 смешанного дерева дошёл до проверки KG CASE + EA CASE в изолированной fixture. C0191 остановился до погрузки: legacy DOCID ограничен 15 символами, а созданный номер СТ был длиннее; частичная СТ не содержит строк или исполнения. C0190 теперь берёт только сохранённый остаток после LOAD, а не текущий остаток БД; 79 адресных тестов, architecture и UTF-8 проверки прошли. C0192 получен, но не принят: прямое удаление тестовых пользователей/прав не журналируется, поэтому передано исправление. См. [план исполнения](roadmap/tradecase_execution_20261019.md).

- 27.10: [Сборка из 250 мест](database/grouped_st_assignment_20261027.md): отбор 660 завершён; отдельная граница legacy-функции исправлена, применение/откат/повтор 9/9/9. [Выборочное снятие](database/tt_selected_places_20261027.md) APPLIED и проверено на live Oracle/API: 4 места, 2 сняты, повтор/409/конкуренция/403; UI 1440/390 7/7.

- 27.10: [Совместный план](roadmap/tradecase_joint_execution_20261027.md): исходный T08 660→640 прошёл локально; C0178 блокирует добивку без данных паллетомест/укладки; события SAP/СКМ остаются PENDING. T10: C0177 устранил 500 при гонке сессий; C0180 live BLOCK/UNBLOCK/replay принят (K-0195); C0181 Гант принят (K-0197); C0182 не нашёл безопасного QA-визита (K-0200); C0183 добавил четыре подтверждённых текста отказа, тест 9/9 и quality gate PASS (K-0202); C0184 проверил 22 GET и оставил backlog по конкурентной задержке (K-0204); C0185 подтвердил 409 YARD_DOCK_BLOCKED на 1440/390, без плана и изменения остатков, ворота открыты и визит отменён (K-0206); C0186 исправил подсказку на узких экранах, проверка 320/390/768/1440 (K-0208). На четырёх других площадках есть дорожки ричтраков; за 7 дней реальный UI показал назначенную работу и карточку на 390/1440. T12: 394 offline TRADECASE tests pass with a repo-local pytest temp directory. T01 закрыт, T02–T12 частичные.

- 28.10: T10 optimization in the resource timeline is committed as `6a9f0101`; it limits returned assignments to visible/unscheduled events and avoids repeated owner checks for the administrator. Focused timeline tests 24 PASS; combined query/timeline/weighted CASE tests 61 PASS; full TRADECASE suite 396 PASS; RETAILCASE quality gate PASS; Gantt browser test 360/390/1440 PASS. Live regression is not repeated; T10 remains partial. See [performance evidence](runbooks/resource_timeline_performance_20261027.md) and [execution plan](roadmap/tradecase_execution_20261019.md).
- 28.10: C0188 added an explicit manual NET endpoint for KG CASE lines; canonical `CASE_PICK_CONFIRM` records operator, value and source. The marking-policy read now distinguishes KG weight lines from serialized weighted boxes (`weighted_kg`) while preserving the existing `loose_weight_kg` meaning. Offline tests pass; no Oracle DDL or live posting was performed. The picker UI is implemented and intercepted UI-tested. New weighted KG writes through general `confirm` are refused; exact replay of saved legacy commands remains supported. Live posting and mixed-tree acceptance remain open; see [T06 execution status](roadmap/tradecase_execution_20261019.md).
- 27.10: Документы NICORA/SAP сокращены и проверены в PDF: заявка — 2 страницы, памятка по CSV и схема обмена — по 1 странице. [Запрос данных](requirements/nicora_sap_stand_data_request_20261027.md), [состав CSV](requirements/nicora_export_fields_examples_20261027.md), [округление единиц](requirements/nicora_order_units_20261027.md). Полный словарь 211 полей и CSV-примеры сохранены в архиве: [папка Google Drive](https://drive.google.com/drive/folders/1emoECef4meEFzSM9D5ClE8lzQ3N5OAAv).
- [Защитные строки единиц](database/existing_unit_guards_20261026.md) применены8/8/8; [снимок и индекс](database/stock_verify_snapshot_20261026.md) —11/10/11. Запуск660мест прошёлHTTP/56,5с; запуск и разрешение отбора имеют единый90сdeadline, прочие команды30с, mutex6с.

- [Коробный рейс](database/carton_trip_bounds_20261026.md): пределы1000мест/4000истории применены,660заданий отобраны и назначены33687. [Отдельный прогон660мест завершён](roadmap/tradecase_evening_result_20261026.md): выезд/повтор/DONE/0H0/QAзакрыт. Исходные3заказа/660→640 открыты.

- 27.10: [Три заказа/1100 коробов](roadmap/tradecase_program_orders_20261027.md): приёмка возобновляется из сохранённого запроса после ошибки записи состояния. [Добивка по прогнозу перемещений/X получателя](requirements/tradecase_topup_forecast_20261027.md): [Oracle-проверка](database/trade_topup_forecast_guard_20261027.md), [окно1000](database/trade_topup_source_window_20261027.md) и [отмена назначения](database/trade_cancelled_trip_assignments_20261027.md) применены7/7/7; гонка двух рейсов и очистка отдельного набора прошли. T01 готов, T02–T12 частичны.

- [Параллельные чтения и аудит](runbooks/tradecase_audit_concurrency_20261026.md): аудит вынесен из HTTP-потока, целостность журналов проверена. SQL обеспеченности сокращён до одного чтения с равным результатом; общее ускорение восьми HTTP-запросов не подтверждено.

- [Фактическая отгрузка для SAP/СКМ](database/trade_shipment_events_20261026.md): применено 11/10/11; выезды 600/200, общий rollback, потеря ответа и точный повтор прошли. Экран двух отправок и права проверены на 1440/390 px. Реальные адаптеры остаются неподключёнными.

- [Частичная отгрузка80→60+20](database/tradecase_partial_80_20261026.md): два настоящих выезда, закрытие0/H0, карточка сборки/погрузки/выезда/остатка. Права,1440/390pxи SQL проверены; отдельные исходящиеSAP/СКМс кодами ещё исследуются.

- [Формат даты отгрузки](database/shipping_time_nls_20261026.md): исправление применено26.10;28сочетаний, откат/повтор и INVALID0 проверены в Oracle. Порог часа и правила выбора дня сохранены.

26.10 до19:00МСК: Codex выполняет оставшиеся спринты самостоятельно. Claude недоступен до29.10 по лимиту, ожидающее C0171 остановлено владельцем. [Контекст и границы](../coordination/tradecase-20261019/RESUME_LATEST.md#активное-поручение2610-срок1900мск). C0171 успел подтвердить начало, завершённого результата нет.

[Публикация23.10](../coordination/tradecase-20261019/PUBLICATION_20261023.md) · [Контекст перезапуска](../coordination/tradecase-20261019/RESUME_LATEST.md) · [Снимок доказательств23.10](../reports/tradecase/2026-10-23/codex-snapshot/README.md).

23.10: владелец утвердил перерыв 120/15 и эталон магазин12:55/возврат14:10; [нативный расчёт совпал](runbooks/tradecase_live_road_provider_20261023.md#несовпадение-контрольного-расписания).

- [Настоящий дорожный расчёт](runbooks/tradecase_live_road_provider_20261023.md): работающие локальныеOSRM/Valhallaпроверены; через8088проверены два плеча, затем три остановки/четыре плеча и одна квитанция. Повторное созданиеHTTP-клиента устранено: тёплыйOSRM1339–1366→14–22мс при равной матрице; полный маршрут/окна остаются открытыми.

- [Приёмка12разделовTRADECASE](roadmap/tradecase_acceptance_20261021.md) сверена с результатами23.10; прежние4/4и незакрытые ранее проверки отделены от нынешних фактов. Все12разделов сохраняют частичный статус.

- [Дефицит при отборе](requirements/tradecase_pick_shortage_20261023.md): сценарий независимой проверки записан до примененияC0170; Claude подтвердил блокировку торговым стражем. Живая цепочка восстановления прошла26.10, тестовый набор закрыт20/H0; полныйT11ещё открыт.

- [Список складов: скорость](runbooks/warehouse_selectors_performance_20261023.md): одинаковыйHTTP-ответ для367складов,586→237мс; SQL412→68мс. МалыйMES-набор17→37мс сохранён как измеренный компромисс, без второй ветки/кэша/индекса.

- [Смена машины](database/tradecase_vehicle_change_20261023.md): настоящий интерфейс и рейс33677 прошли смену/выгрузку/перепогрузку/выезд, старый документ отклонён, товар0/H0 и тара0. [Заводская приёмка](database/tradecase_factory_receipt_20261023.md): SSCC с коробами6+4 принят одним сканом черезAPI,10единиц, повторы и отказы проверены; актор закрыт. Все спринты остаются частичными, кромеT01.

- [Инвентаризация: потери, находки и повтор](database/inventory_current_owner_20261023.md):42случая и настоящий UI с потерей ответа после commit/owner403/точным повтором прошли;250/H0 сохранены, ревизии418–421 закрыты. Первый неудачный кандидат откачен; действует проверка до квитанции.

- [Разделение паллеты и восстановление](components/tradecase_sort_recovery_20261023.md):273теста, настоящий отказ без изменения10единиц и8проверок собранного экрана1440/390 прошли; неизвестный исход сохраняет прежнюю команду.

- [Подтверждение состава заказа](database/trade_composition_ack_20261023.md): C0164 применён и проверен, включая повтор только отказавшей стороне и потерю ответа в UI. C0165 сдан без правки runtime; C0166 инвентаризация применена и проверена; ревизии и тестовые акторы закрыты.

- [Отгрузка вложенного места](database/tradecase_nested_shipping_20261023.md): новое дерево PALLET→BOX→STOCK,10 единиц/одно верхнее место, LOAD/DEPART/replay, раздельные подтверждения и обратная тара прошли. Волна623 DONE, товар0/H0, тара0, акторы отключены. Source review подтвердил attach CASE/HU; смешанное дерево после весовой сборки и полочного отбора остаётся открытым с конкретным чек-листом сквозной приёмки.
- [Состав поставки частями](database/trade_supply_parts_20261023.md): Native11/9/11,52HTTP, две аварии до/после commit, версия/гонка/отзыв и1МБ прошли. C0164 принят в указанном объёме; C0165 зарегистрирован 27-м, C0166 — 28-м.

- [Добивка после начала погрузки](database/trade_topup_after_load_20261023.md): C0161rev1 native9/9/9, настоящий LOAD части основного груза, добивка20EA/replay и отказ послеUNLOAD прошли. Возврат250/H0, собственные задания закрыты.

- [Торговый остаток в общем пуле](database/trade_pool_eligibility_20261023.md): Распределение/потребление20EA и нехватка230/300 прошли. C0162 native8/8/8, назначенная роль/legacy/склад/owner/replay проверены,250/H0.

- [Двор: конкуренция и видимость](database/tradecase_yard_visit_20261022.md): параллельные команды, две входящие машины на одни ворота и200скрытых+видимый проверены; входящие интервалы есть в общем Ганте.
- [План СНС/BLC](roadmap/tradecase_execution_20261019.md): полный перенос удержания40шт. и отмена со сверкой прошли; частичная передача/общий пул открыты. [Контекст и бюджет](../coordination/tradecase-20261019/RESUME_LATEST.md):26зарегистрированных обращений; C0164 передан, C0163rev1 у root. [Исполнитель ожидания](components/tradecase_deferred_worker_20261022.md):128сообщений, два аварийных завершения до/после commit и восстановление проверены; промышленные адаптеры открыты.
- [Остаток паллеты на следующем рейсе](database/tradecase_hu_defer_wait_20261022.md): первый короб выехал, второй перенесён в следующий рейс и физическое ожидание; две миграции/откат/replay прошли; проверка owner-права на архивные ответы исправлена,7EA/HARD5.
- [Профилирование PL/SQL в dev](database/plsql_profiler_dev_20261022.md): собственное хранилище применено с откатом,17профилей настоящего запуска собраны без DBA-прав;8EA/HARD4 восстановлены. Тёплый максимум38мс/2исполнения; холодная задержка остаётся открытой.
- [СНС/BLC: отмена пустого задания](database/tradecase_empty_case_cancel_20261022.md): две миграции и неизменный повтор прошли;8EA/HARD4, тара освобождена, волна608 DONE с возвратом потребности. Ручной повтор/гонка и отзыв прав проверены,6UI возврата прошли.
- [СНС/BLC: ручной вес пустого короба](database/tradecase_manual_case_tare_20261022.md): scoped запись0.1кг, настоящий отбор2EA и контроль2.1кг прошли;6UI1440/390 и9offline. Гонка перевзвешивания с первым отбором и два отрицательных итоговых контроля прошли; противоположная очередность и оборудование ещё не приняты.
- [Шлюз весов OPC UA 40200](../docs/integrations/weighing-gateway-opc40200.md): offline API/шлюз/протокол assembly и warehouse проверены150 тестами,2 пропущены; реальное оборудование и смешанное дерево отборов не подтверждены.
- [СНС/BLC: выпуск этикетки короба по назначению](database/tradecase_case_labels_scoped_20261022.md): собственные блокировки и действующая область проверены через native/API; применение, откат и повторное применение прошли.
- [СНС/BLC: короб навалом](database/tradecase_bulk_box_loading_20261022.md): погружены2EA, остаток8/HARD4; точный повтор, конфликт и отзыв owner-operate проверены. Выезд с непогруженными назначениями заблокирован;6UI1440/390 прошли. T07 остаётся частичным.
- [СНС/BLC: вложенные места](database/tradecase_hu_pack_20261022.md): две миграции APPLIED/rollback/reapply; роль46HTTP, дерево глубины3, отзыв owner/повторы/конкуренция и8UI1440/390 прошли; группа3EA восстановлена.
- [СНС/BLC: целая паллета](database/tradecase_full_pallet_admission_20261021.md): scoped MOVE/bind, исправленное окно Ганта, LOAD/UNLOAD/RELOAD/DEPART и повторы проверены. Два owned-склада0/HARD0; внешние ответы синтетические, вся программа не завершена; [тип паллеты по области](database/tradecase_pallet_floor_scope_20261022.md) и UI1440/390 прошли; исправлены мобильная raw-форма и контракт неизвестного исхода.
- [СНС/BLC: распределение места](components/tradecase_topup_allocation_20261021.md):40A+20B/обратный приоритет,35HTTP и UI1440/390; один READ ONLY snapshot, без заказа/резерва. [Профиль нового запуска](runbooks/tradecase_new_wave_profile_20261021.md) сохраняет3498мс; точная Oracle trace пока недоступна текущему пользователю.
- [СНС/BLC: источники21.10](sources/tradecase_20261021.md): Drive revision27 программы,12разделов вместо45проверок; [новая матрица](roadmap/tradecase_acceptance_20261021.md), прежние статусы автоматически не перенесены.
- [СНС/BLC: смена и ресурсы](components/tradecase_shift_resources_20261021.md): вместо статического демо открывается реальная смена/волна без потери входа; DONE603/604,10UI и прежние переходы прошли. [CASE queue](runbooks/tradecase_case_queue_performance_20261022.md): SQL95→51мс/HTTP203→191мс, холодные1.2с открыты; отдельный процесс480мс, пул292мс, очистка2–5мс. Двор/полный T10 не завершены.
- [Отзыв доступа отключённого сотрудника СНС/BLC](database/tradecase_retired_grant_revoke_20261021.md): исправлено и проверено8HTTP; повтор/версия/admin-only, inactive enable запрещён.
- [СНС/BLC: отбор после приёмки коробом](database/tradecase_case_receipt_modes_20261021.md): исправлено: роль/сессия, CASE2/повтор/возврат,10/HARD0; мобильный запас карточками; native/экраны1440/390 проверены.
- [СНС/BLC: продолжение21.10](database/tradecase_deferred_documents_20261021.md): владелец возобновил спринты; T02 — сохранение сообщений при отсутствии справочника и повторная проверка. Oracle apply/rollback/reapply и44+29HTTP прошли; UI1440/390 и6проверок восстановления прошли. Лимит Claude прежнего цикла4/4 сохранён.
- [СНС/BLC — выполнение](roadmap/tradecase_execution_20261019.md): T01 завершён, T02–T12 частичны; C0187 добавил 36 offline-проверок весового отбора CASE, но не живую смешанную приёмку. `/weigh-line` пока требует capture; ручной ввод NET для этой операции остаётся открытым; [программа revision27](roadmap/tradecase_acceptance_20261021.md), [Oracle](database/tradecase_contract_20261019.md), [источники](sources/tradecase_20261021.md). Реальные SAP/СКМ, оборудование и пилот остаются открыты.
- [Описание работы в системе RETAILCASE](components/retailcase_operations_guide_20261019.md#публикация-19102026-и-повторная-проверка-текста): опубликовано в GitHub/Pages и главном README;43должности/19процессов/272обязанности,597UI-checks. Расписание19.10 завершено; СНС/BLC продолжен21.10 новым поручением.
- [SQL TRADECASE19.10](runbooks/tradecase_sql_review_20261019.md):200строк203→5SQL, CASE owner через целевые ключи; cold-задержки, нагрузка и решения по каждому долгому блоку сохранены.
- [Проверка скорости вместе с функциональностью](runbooks/slow_sql_review.md#поручение-владельца19102026-скорость-вместе-с-функциональностью): UI/API/SQL, причина→исправление→сравнение; владелец разрешил код/SQL/индексы, миграции и live verify обязательны.

## Работа с документацией

[Схема wiki](WIKI_SCHEMA.md) · [Карта проекта](overview.md) · [Журнал изменений](log.md) · [Каталог источников](sources/index.md).

Не добавлять сюда хронику тестов; лимит100строк. Обновлять текущую ссылку, подробности хранить в focused page/log. Полный прежний индекс сохранён;798 относительных ссылок перенесены с проверкой целей.

## Общий стандарт розничной логистики

[Розничная логистика](requirements/retail_convenience_standard/README.md) · [Полный каталог](sources/wiki_index_catalog_20261015.md#общий-стандарт-розничной-логистики).

## RETAILCASE — межскладской подвоз и cross-dock

[Модульный договор](architecture/retailcase_modular_development_contract.md) · [Единая проводка](requirements/stock_posting_core_tz.md) · [Каталог RETAILCASE](sources/wiki_index_catalog_20261015.md#retailcase--межскладской-подвоз-и-cross-dock).

## Справочники проекта

- <a id="logical-branches"></a> **Logical Branches.** [Oracle, C#, терминалы, интеграции](sources/wiki_index_catalog_20261015.md#logical-branches).
- <a id="subprojects"></a> **Subprojects.** [Подпроекты](sources/wiki_index_catalog_20261015.md#subprojects).
- <a id="architecture"></a> **Architecture.** [Архитектурные страницы](sources/wiki_index_catalog_20261015.md#architecture) · [Права и встроенные знания](architecture/retailcase_scoped_access_and_knowledge.md).
- <a id="database-mirror"></a> **Database Mirror.** [Oracle mirror](database/index.md) · [Изменения Oracle](database/oracle_change_protocol.md) · [WARES: PK и название как уникальный ключ](database/retailcase_wares_identity_keys_20261015.md).
- <a id="incidents"></a> **Incidents.** [Инциденты и принятые исправления](sources/wiki_index_catalog_20261015.md#incidents).
- <a id="concepts"></a> **Concepts.** [Дерево грузовых мест](concepts/retailcase_nested_hu_consolidation_20261015.md) · [Паспорта KPI](concepts/retailcase_kpi_passports_20261015.md) · [Остальные понятия](sources/wiki_index_catalog_20261015.md#concepts).
- <a id="runbooks"></a> **Runbooks.** [Приёмка сценария](runbooks/evidence_driven_process_testing.md) · [Долгие SQL](runbooks/slow_sql_review.md) · [Полный каталог](sources/wiki_index_catalog_20261015.md#runbooks).
- <a id="roadmap"></a> **Roadmap.** [Права/знания](roadmap/retailcase_access_knowledge_plan.md) · [ТМС-2](roadmap/transport_execution_plan.md) · [Остальные планы](sources/wiki_index_catalog_20261015.md#roadmap).
- <a id="requirements"></a> **Requirements.** [Требования и версии](sources/wiki_index_catalog_20261015.md#requirements).
- <a id="control-files"></a> **Control Files.** [AGENTS.md](../AGENTS.md) · [WIKI_SCHEMA](WIKI_SCHEMA.md) · [Архитектурная политика](../config/architecture/retailcase-policy.json) · [Остальные контрольные файлы](sources/wiki_index_catalog_20261015.md#control-files).

- 27.10: [Гант ресурсов: замер Oracle](runbooks/resource_timeline_performance_20261027.md): фильтр ответа сократил назначения 1281→1 при равном 6-часовом наборе; admin-only fast path дал медиану 3,22→2,81 с. Oracle всё ещё тратит около1,5с на loading_rows; неадминистративный путь и реальный A-Rows не проверены.

- 28.10: C0189 ручного NET в действующем picker принят (`4723435a`): 9 перехваченных UI-сценариев PASS; тесты RETAILCASE 873 passed/2 skipped, TRADECASE 396 passed. Исправлена граница подтверждённого отказа доступа при переносе/возврате CASE (`be96e8c6`), 35 целевых тестов PASS. Оба quality gates, architecture и encoding PASS. Это offline/UI-intercept evidence; живые проводки и T06 mixed-tree gate остаются открытыми. T01 завершён, T02–T12 частичные.
- 28.10: C0190 RELEASE K-0219 принят после независимой проверки. Codex довёл offline suite до 60 PASS и read-only Oracle preflight до findings=[]; живой run заблокирован до восстановления частичных fixture commit и ввода фактических NET/тары. Складских записей не создавали. T01 завершён, T02–T12 частичные. [Отчёт проверки](../reports/tradecase/2026-10-28/codex/t06-c0190-readonly-review.md).
- 28.10: C0190 получил восстанавливаемую fixture: intent+сверка каждой конфигурационной строки и ревизии. Offline 63 PASS, TRADECASE 396 PASS; новый read-only preflight пустого склада прошёл. Полная живая цепочка ждёт фактические NET/тару и транспортную fixture; T06 частичный. См. [отчёт](../reports/tradecase/2026-10-28/codex/t06-c0190-recovery.md).
- 28.10: C0190 получил восстанавливаемую fixture: intent+сверка каждой конфигурационной строки и ревизии. Offline 63 PASS, TRADECASE 396 PASS; новый read-only preflight пустого склада прошёл. Полная живая цепочка ждёт фактические NET/тару и транспортную fixture; T06 частичный. См. [отчёт](../reports/tradecase/2026-10-28/codex/t06-c0190-recovery.md).
- 28.10: электронный и ручной NET CASE теперь оставляют различимый источник измерения в canonical operation; 71 адресный тест PASS. Живые весы не проверялись; T06 частичный.
- 28.10: проверена совместимость electronic CASE: новый источник веса сохраняется для новых операций, сохранённый legacy request повторяется без изменения; backend 57 PASS, UI 9 PASS.
- 28.10: повторная проверка C0190 исправила параметры Oracle-сверки, повтор сохранённого отказа и запись состояния; 67 тестов PASS. Полная восстанавливаемость ещё не подтверждена, принудительный флаг снят. См. [актуальный план](roadmap/tradecase_execution_20261019.md).

- 28.10: T06 — восстановление заказов/волны и сохранение команды тары; 74 адресных теста PASS. C0191 транспорт/магазин передан Claude, ACK ожидается; [контекст](../coordination/tradecase-20261019/RESUME_LATEST.md).

- 28.10: T06 mixed-tree runner recovery corrected; first incomplete live fixture retired with zero stock/reservations. API-launch run in progress. C0191 awaits Claude authentication/ACK. See [execution plan](roadmap/tradecase_execution_20261019.md).
- 28.10: C0191 was restored from its file-channel release and passed 25 focused tests. Live integration exposed the bounded legacy `DOCID` requirement before any load; C0192 cleanup is ACKed and C0191 recovery rework is queued. See [execution plan](roadmap/tradecase_execution_20261019.md).

- 28.10 correction: Claude C0191 RELEASE K-0221 received; commit restored, root integrating. C0192 cleanup companion handed off; ACK pending. See [coordination prompt](../coordination/retailcase-claude/CODEX_WORK_PROMPT.md).

- Current performance evidence: [[roadmap/tradecase_execution_20261019]] records the T10 timeline transport-window rewrite, its Oracle/API timing, and remaining concurrency work.
