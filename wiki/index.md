- 29.10: ?????????? builder T03/T04 ????????? ???????? CRPT+EGAIS ??????? ????????? ?????????; 3 ????? ??????. ??. [????](roadmap/tradecase_execution_20261019.md).
- 29.10: T03/T04 ??????? ?????????? trace-manifest builder ??? 250 ????????????? ?????? ? ?????? root-???????; 2 ???????? ????? ??????. ??. [????](roadmap/tradecase_execution_20261019.md).
- 29.10: T04: live-?????? ?????? ?? ?????????? SAP XML ?? ?????????; ????????? ????? ?????????? fixture. ??. [????](roadmap/tradecase_execution_20261019.md).
- 29.10: T02 ????????? ???????? ??? SAP/???: ??????? ? worker ????????? ????????? ??? ???????? ???, ?????????, rollback ? ????????? ??????????. ??. [????](roadmap/tradecase_execution_20261019.md).
- 29.10: T11: ???????????? ?????? ???????? ????????? ??????????????? ?? ?????????? QA-???????????? ? ?? ?????? Oracle. ??? ????? ??????? ????? ????????? fixture; ?????????/??????? ??????? ? ??????? ???????. ??. [????](roadmap/tradecase_execution_20261019.md).
- 29.10: Владелец подтвердил границу текущей поставки: SAP, СКМ и оборудование не подключаются. Спринты закрываются по внутренним Oracle/API/UI контрактам и ручному вводу. См. [план СНС/BLC](roadmap/tradecase_execution_20261019.md).
# TMS Wiki Index
- 10.11: SNS — [требования к выгрузке SAP](../SNS%20График%20поставок/wiki/sap_export_requirements.md): приоритет заказов, короба/тонны, точные связи и фильтры; технические источники BLC требуют маппинга SAP-команды.
- 10.11: SNS — [переносимый проект install с контекстом для Codex](../SNS%20График%20поставок/wiki/deployment.md) опубликован в Drive, архив и распаковка проверены.
- 10.11: SNS — [постоянная публикация сборок в Google Drive](../SNS%20График%20поставок/wiki/deployment.md). Последняя версия размещена и проверена; лимит коннектора обойдён комплектом частей и INSTALL.cmd.
- 10.11: SNS — [XML всех данных и автономный установщик](../SNS%20График%20поставок/wiki/deployment.md), включая исходные файлы и актуальную базу; импорт одной транзакцией.
- 10.11: SNS — [спорные операции BLC получили план VDATU](../SNS%20График%20поставок/wiki/dates_pair_analysis.md) по решению владельца: все 15 конфликтов, 30 связей операций.
- 10.11: SNS — [план VBAK-VDATU из babak8](../SNS%20График%20поставок/wiki/dates_pair_analysis.md): обновлены заказы, поставки, BLC и транспортировки; 1350 рейсов покрыты, 15 конфликтов связей выделены.
- 10.11: SNS — [116 транспортировок: заказы и BLC](../SNS%20График%20поставок/reports/transports_without_actual_delivery.html); таблица с поставками и причинами отсутствия дат.
- 10.11: SNS — по поручению владельца требуемые даты дополнены фактическими: 2760 транспортировок; 116 без исходной даты перечислены в [отчёте](../SNS%20График%20поставок/reports/transports_without_actual_delivery.txt).
- 10.11: SNS — [vbak7: покрытие транспортировок](../SNS%20График%20поставок/wiki/dates_pair_analysis.md): 1350 из 2876 имеют совпадающий заказ; VDATU отсутствует, обновление требуемых дат невозможно. Окончание BLC принято как фактическая дата сдачи.
- 10.11: SNS — [анализ новой VBAK](../SNS%20График%20поставок/wiki/orders_analysis.md): найден фильтр-кандидат YRK0/YRK2/YRKK + C/20, сокращение 88,02%; точное наличие рейса подтверждается связями документов, не только типом заказа.
- 10.11: SNS — исправлена подготовка выгрузки VBAK из SE16: отбор ERDAT, пять полей, лимит и проверка полноты; проверена только компиляция, без SAP. См. [источники SNS](../SNS%20График%20поставок/wiki/sources.md).
- 29.10: T10 ???????? ???????? ???????????? ???????? ????? ? resource timeline: live 2 ????????, offline 52 ????????.
- 29.10: T12 ?????? ????????? TRADECASE-??????? ??????: 480 ??????. ????????, ??????? ? ??????????? ???????? ???????? ?????????? ?????????.
- 29.10: T09 ???????? ?????????? native ?????? ??????? ? ???????? ?????? 120/15: ??????? 12:55, ??????? 14:10. ??. [??????????????](../runtime/test-evidence/tradecase/2026-10-23/T09/program-reference-schedule-owner-approved.json).
- 29.10: T08 ???????? ?????? live-???????? ???????? Oracle/API: ??????? ???????????, ????????????, ???????????, ??????, ???????????? ? ?????. ??. [??????????????](../runtime/test-evidence/tradecase/2026-10-22/T08/topup-live-210899077.json).
- 29.10: T07 подтвердил конкуренцию двух разных команд выезда для одной составной root-паллеты: один TRIP_DEPART, один выезд, один магазин и одна приёмка. См. [доказательство](../runtime/test-evidence/tradecase/2026-10-29/T07/depart-race/final.json).
- 29.10: T06 применил Oracle-миграции multi-order root HU и подтвердил стендовый путь одной составной паллеты KG CASE + EA CASE до принятой магазином поставки: один root, один ST, один получатель, без разделения. Повторная Oracle-проверка пяти migration verify-скриптов прошла; package/body `RRL_STOCK_SHIPPING_CORE` остаются `VALID`. Текущая проверка журнала и Oracle снова подтвердила одну ST-паллету, одного получателя и один факт приёмки. Прогон использовал ручной ввод веса и внутренние API; SAP, СКМ и оборудование не подключались. См. [T06](database/t06_multi_order_root_hu_20261029.md).
- 29.10: T07 получил частичное доказательство на том же root: `LOAD/replay` и `DEPART/replay` прошли до приёмки магазина. Concurrent exact replay returned two identical HTTP 200 responses and retained one applied effect. Полная матрица T07 требует новой изолированной загруженной root-HU: доступные historical fixtures уже выехали. См. [план](roadmap/tradecase_execution_20261019.md).
- 29.10: применена миграция root-HU binding. Несколько CASE одного root могут быть привязаны только к одному ST с одним получателем; проверка блокирует различающиеся адреса и составы. См. [зеркало схемы](database/root_hu_shipment_bind_20261029.md).
- 29.10: T08 применил явную паллетизацию SKU для добивки. Расчёт использует тип паллеты, коробов на место и один слой; положительный Oracle/API-прогон подтвердил один выигравший конкурентный резерв и его освобождение. См. [паллетизацию T08](database/trade_topup_palletization_20261029.md).
- 29.10: T08 повторно проверил applied-миграцию версии получателя. Изменение только параметров добивки сохраняет строку заказа; изменение торговых условий и отсутствие истории по-прежнему блокируют её. См. [план](roadmap/tradecase_execution_20261019.md) и [доказательство](../reports/tradecase/2026-10-29/codex/t08-recipient-version-live.json).
- 29.10: T07 повторно проверил перенос короба в ожидание на текущем Oracle после применённой successor-миграции guard. Один короб выехал, второй сохранился в другом рейсе; полный конкурентный набор ещё открыт. См. [T07](database/tradecase_hu_defer_wait_20261022.md).
- 29.10: T12 local regression: 474 TRADECASE теста, архитектурный gate и TypeScript admin frontend прошли. См. [доказательство](../reports/tradecase/2026-10-29/codex/t12-local-regression.json).

Короткий вход в проект. Открывать только страницы по текущему вопросу. Исторические статусы и полный каталог сохранены в [архиве оглавления](sources/wiki_index_catalog_20261015.md); они не заменяют актуальную карточку компонента.

## Текущая работа

- 29.10: DeepSeek исправил восстановление создания рейса и результат VRP: intent до POST, pending не чистится при закрытии, повтор по сохранённым параметрам, серверный operation_id (миграция `RRL_TRIP_CREATE_RESULT`+`RRL_TRANSPORT_IDEMPOTENT_API` применена к Oracle и проверена live — тот же operation_id даёт тот же task_id, изменённый payload даёт конфликт), async solve/cancel с полным результатом задачи, фиксированный payload применения. Очередь проверок — [D003_VALIDATION](../coordination/deepseek/D003_VALIDATION.md).
- 29.10: В форме создания обычного и кластерного рейса время отгрузки сохраняется в рейсе и участвует в проверке доступности машины. VRP больше не сохраняет пустой план как успешный: при наличии заявок без построенных рейсов API возвращает 422 с причиной.
- 29.10: ТМС-2 Sprint 102 повторно измерен корректно: таблица 2 000 СТ готова за 158 мс после входа; в DOM 31–42 строки. Замер не включает открытие страницы и форму входа. См. [runbook приёмки ТМС-2](runbooks/tms2_release_acceptance.md).
- 29.10: Приёмочный набор дневного VRP приведён к фактической fixture: 308 СТ всего, 272 свободны. Полный набор `test_final_vrp_daily_acceptance.py` прошёл 3/3.
- 29.10: Строгий TMS-2 release gate обнаружил устаревшие acceptance-проверки и неполные fixture операции: 407 passed, 26 failed, 15 skipped. Перечень и следующий порядок исправления сохранены в [плане спринтов](roadmap/transport_execution_plan.md).

- 28.10: Кандидат миграции тары корневого HU не применён к Oracle. Прежнюю запись о применении в плане исправил.
- 28.10: Владелец исключил подключение SAP, СКМ и оборудования из текущей поставки. Внутренние WMS-сценарии закрываются по контрактным API и ручному вводу; реальные адаптеры, DESADV, аппаратные весы и промышленный обмен перенесены за её границу. См. [план СНС/BLC](roadmap/tradecase_execution_20261019.md).
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

- 2026-10-28: A second local, unapplied migration makes a root-HU tare booking bind to the scanned root, its current cell and composition version. Its read-only Oracle preflight passed; live DDL and replay/rollback evidence are still required.

- 29.10: DeepSeek переданы два блока UI-разработки: [D001 — создание рейса](../coordination/deepseek/INBOX/D001.md), [D002 — расчёт VRP](../coordination/deepseek/INBOX/D002.md). ACK ожидается; [правила канала](../coordination/deepseek/README.md).

- 29.10: [D003 — завершение разработки продукта](../coordination/deepseek/INBOX/D003.md) передано DeepSeek: сначала исправления D001/D002, затем кодовые пробелы ТМС-2 и внутренних спринтов TRADECASE. ACK ожидается; приёмка не объявлена.

- Контекст перезапуска 29.10: [Codex / DeepSeek D003](../coordination/deepseek/CODEX_RESUME.md). Основная разработка передана DeepSeek; на момент записи ACK D003 отсутствует, D001/D002 ещё не приняты.

- 06.11: [Плавающий вес и виды фасовки в WMS](concepts/wms_variable_weight_legacy_20261106.md): формулы legacy Oracle и отдельные механизмы точного веса, границы проверки.

- 07.11: [Минимальные данные обмена ERP — WMS](requirements/erp_wms_minimum_data_contract_20261107.md): логические таблицы, поля, условия обязательности, результаты и правила загрузки.

- 08.11: Начат проект [SNS график поставок](../SNS%20График%20поставок/wiki/index.md): локальная вики, цепи as is, структура источников и первичный профиль заказов; визуализация на согласовании.

- 08.11: Владелец согласовал две самостоятельные страницы SNS: напитки и сигареты; карта включает объём, стоимость, утилизацию, расстояние, число рейсов, недельный календарь выделяет разовые поставки оранжевым. См. локальную wiki проекта.

- 08.11: Создан первичный локальный прототип двух страниц SNS; критерии полноты, ограничения join и оставшаяся проверка описаны в локальной wiki проекта.

- 08.11: SNS: реализовано частичное оценочное распределение стоимости рейса по коробам × расстоянию с проверкой суммы; подробности и неполное покрытие в локальной wiki проекта.

- 08.11: Локальный SNS прототип дополнен выбором направления/города и детализацией отдельных или нескольких рейсов; ограничения веса, утилизации и подтверждения адресов сохранены в wiki проекта.

- 08.11: Проверены действия SNS на карте и список рейсов на широком и мобильном экранах; число точек открывает перечень с количеством по BLC. Данные заказа отдельно требуют сверки.

- 08.11: На карте SNS ширина стрелки зависит от количества рейсов, цвет — от средней оценочной утилизации; подсказка показывает средний вес, стоимость и покрытие данных.

- 08.11: В SNS карта разворачивается на весь экран; линии тоньше и с прозрачностью 40%, проверено на 1440/390 px.

- 08.11: SNS: фильтр утилизации и детализация рейса до товаров/заказов из выгрузок; количество найденных строк и ограничения сопоставления сохранены в wiki проекта.

- 08.11: В локальном SNS-графике добавлены маршрут SAP и признак отправления; московский хаб условно размещён у Дмитрова отдельно от филиалов. [Источник и ограничения](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: Для направлений «Хаб–Сеть» SNS-карта учитывает город или район РЦ по адресу BLC; координаты ориентировочные. [Источник](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: В SNS графике добавлен фильтр по набору хабов для карты, календаря и рейсов. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: В SNS-графике показаны наименование SAP-маршрута и стоимость рейса, а также отправители и получатели. [Источники](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: На карте SNS добавлены различимые стрелки и выбор входящих/исходящих рейсов точки. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: В SNS-графике добавлен контроль ненанесённых и частично нанесённых рейсов с причинами. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Совпадающие точки SNS-карты показываются кольцом, толщина которого зависит от числа рейсов. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Расширены координаты городов SNS; оставшиеся неоднозначные направления указаны в контроле полноты. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: На SNS-карту добавлены РЦ района Кочкина и Комсомольск-на-Амуре. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: На карте SNS учтены уточнения владельца по СНКТ, Алабино и городам в адресах. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Получатель НОВГОРОД_Ф на карте SNS привязан к Великому Новгороду. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: В календаре SNS добавлен выбор отдельных дней и диапазона Shift. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Уточнена легенда кругов и увеличены стрелки на SNS-карте. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Развёрнутая SNS-карта показывает действующие фильтры и позволяет сбросить каждый или все. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Шкала SNS-карты изменена: 100% утилизации отображается тёмно-синим. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: В развёрнутой SNS-карте добавлены диапазоны утилизации, веса, коробов и фильтр вместимости ТС. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Фильтры развёрнутой SNS-карты свёрнуты в компактную выпадающую панель. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: На SNS-карте доступна боковая аналитика по городам, направлениям и получателям. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Значок УССР наложен поверх значка Leaflet на SNS-карте. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: SNS-аналитика показывает итоги и доли выбранных строк; таблицы выгружаются в CSV для Excel. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Исправлена ширина и читаемость боковой аналитики SNS. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: В SNS-карте добавлен просмотр входящих рейсов точки по датам BLC и их товаров. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: В SNS-графике доступны множественный выбор плеч и фильтр сети с РЦ. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Календарь SNS показывает плановые даты заказа и даты BLC разными цветами при выборе сети. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Цвет календаря SNS сравнивает план с окончанием BLC, без даты начала. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Календарь SNS сравнивает план и окончание BLC при выборе направления или рейса. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: В календарь SNS добавлены шкалы дневной нагрузки по весу и коробам. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Календарь SNS сравнивает план и окончание BLC по рейсу и получателю. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Фильтры SNS уплотнены, список РЦ сгруппирован по городам и снабжён поиском. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Заголовок и показатели SNS собраны в компактную строку. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: SNS: множественный выбор РЦ и городов с районами из адресов. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Справочник SNS использует города и районы исходного графика, дополняя их по явным адресам; радиус 150 км ещё не проверен. [Источник](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: Список РЦ SNS представлен единой таблицей с сортировкой по городу и району. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Адреса Московской области сгруппированы в справочнике SNS под Москвой с отдельными районами. [Описание](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: Список рейсов SNS показывает плановую дату по точкам, окончание BLC и подтверждение SAP; фактическое прибытие отдельно не установлено. [Источник](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: Рассчитано попарное совпадение дат по торговым сетям SNS. [Анализ](../SNS%20График%20поставок/wiki/dates_pair_analysis.md).

- 08.11: Владелец принял сравнение плана с окончанием BLC для сайта SNS; подтверждение SAP справочное. [Анализ](../SNS%20График%20поставок/wiki/dates_pair_analysis.md).

- 08.11: Владелец уточнил, что окончание BLC — фактическая дата поставки товара получателю. [Источник](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: Исправление владельца SNS: окончание BLC — плановая дата поставки, прежнее определение как факта отозвано. [Источник](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: В SNS используется только плановая дата заказа; окончание BLC — проведение документов и исключено из текущего анализа. [Источник](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: Сохранён список рейсов SNS без однозначно связанного заказа. [Список](../SNS%20График%20поставок/reports/reis-no-linked-orders-2026-10.md).

- 08.11: SNS: рейсы без связи с заказом возвращены в выборку по дате окончания BLC. [Источник](../SNS%20График%20поставок/wiki/sources.md).

- 08.11: В SNS показываются ноябрьские окончания рейсов, начатых в октябре; календарь расширяется за пределы периода начала. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 08.11: Список РЦ SNS открывается отдельной панелью и не перекрывает календарь. [Описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: панель адресов доступна по всем клиентам без выбора сети; см. [визуализацию](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: в адресах клиентов доступны рейсы, тонны и короба за выбранный период; см. [визуализацию](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: выбор области точек прибытия на карте обновляет календарь; см. [визуализацию](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: календарь показывает количество точек по каждому дню; см. [визуализацию](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: окно графика клиентов и предварительного выравнивания недельной нагрузки; см. [визуализацию](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: рекомендации графика сохраняются сервером в локальную SQLite; [запуск и хранение](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: [перенос, запуск и резервное копирование](../SNS%20График%20поставок/wiki/deployment.md).

- SNS: предварительные рейсы по предложенным дням и источникам; см. [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: уточнены ограничения частоты и минимальной партии графика; см. [визуализацию](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: обновлён справочник районов адресов и отдельные колонки графика; [источники](../SNS%20График%20поставок/wiki/sources.md).

- SNS: дополнены районы по адресным источникам и справочнику СНС; компактный интерфейс графика и навигация — [источники](../SNS%20График%20поставок/wiki/sources.md).

- SNS: уточнены районы по РЦ и переключение недель; [источники](../SNS%20График%20поставок/wiki/sources.md).

- SNS: для адресов без определённого района интерфейс показывает город; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: частота синхронизируется с выбранными днями; [график](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: график отдельно показывает сумму выбранной недели и среднюю неделю периода; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: график содержит иконки сетей и цветовую шкалу дневного объёма; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: расширены значки сетей в графике; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- SNS: текущий и рекомендуемый источники снабжения в графике, сохранение в SQLite; [визуализация](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: распределение дней по городам и районам и просмотр состава фактических рейсов из графика. См. [решения SNS](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: исторические попутчики в графике и закреплённый прогноз нагрузки; [решения SNS](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: подсветка всех видимых ячеек совместных фактических рейсов; [решения SNS](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: массовое редактирование дней в выделенных ячейках и подсветка фактических соседей одного города; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: стабильная высота строк и общий лимит попутчиков в шапке; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: автономный установщик Windows с Python и SQLite, без исходных выгрузок; [перенос и запуск](../SNS%20График%20поставок/wiki/deployment.md).

- 09.11: SNS: зелёная подсветка заполненных строк графика; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: исправлено перекрытие дней недели в закреплённой шапке; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: быстрый ввод источника по Enter и пустые ячейки без поставок; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: подсветка соответствующего дня между фактом и рекомендациями; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: день недели подсвечивается одновременно в факте и рекомендациях; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: оранжевая отметка при превышении фактической частоты поставок; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: салатовый цвет выполненной строки при изменении дней поставки; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: меню предложений дней и копирование фактических дней выбранной недели; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: уточнён критерий салатовой строки — выбран день, отсутствующий в факте; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: XLSX-выгрузка таблиц с оформлением, числами и закреплённой шапкой; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: прогноз нагрузки по дням разделён на хабы и филиалы; [описание](../SNS%20График%20поставок/wiki/visualization_and_decisions.md).

- 09.11: SNS: перенос рекомендаций обеих цепей и настроек в XML, установщик обновлён; [запуск](../SNS%20График%20поставок/wiki/deployment.md).

- 09.11: SNS: [контекст для продолжения после перезагрузки](../SNS%20График%20поставок/wiki/resume_20261109.md).

- 10.11: SNS — пояснение, чего не хватает для зелёной строки графика; см. SNS График поставок/wiki/visualization_and_decisions.md.
