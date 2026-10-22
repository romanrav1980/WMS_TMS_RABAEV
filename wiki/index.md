# TMS Wiki Index

Короткий вход в проект. Открывать только страницы по текущему вопросу. Исторические статусы и полный каталог сохранены в [архиве оглавления](sources/wiki_index_catalog_20261015.md); они не заменяют актуальную карточку компонента.

## Текущая работа

- [Продолжение СНС/BLC и бюджет Claude](roadmap/tradecase_execution_20261019.md#возобновление2210-три-дополнительных-обращения-claude): [добивка](database/tradecase_topup_proposal_20261022.md) — native резерв/конкуренция/повторы/освобождение проверены; [маршрут и обеспеченность](components/tradecase_trip_coverage_20261022.md) — замороженное дерево/15проверок доступа; прежний бюджет7/7 сохранён; по новому поручению C0146 применён/откат/повторное применение прошли, живой перенос проверяется; C0147 — исходная приёмка1000единиц и40+40/60 прошли; Claude C0148 делает маршрут. [Исполнитель ожидания справочников](components/tradecase_deferred_worker_20261022.md):7живых проверок прошли. Спринты остаются частичными.
- [Остаток паллеты на следующем рейсе](database/tradecase_hu_defer_wait_20261022.md): первый короб выехал, второй перенесён в следующий рейс и физическое ожидание; две миграции/откат/replay прошли; проверка owner-права на архивные ответы исправлена,7EA/HARD5.
- [Профилирование PL/SQL в dev](database/plsql_profiler_dev_20261022.md): собственное хранилище применено с откатом,17профилей настоящего запуска собраны без DBA-прав;8EA/HARD4 восстановлены. Тёплый максимум38мс/2исполнения; холодная задержка остаётся открытой.
- [СНС/BLC: отмена пустого задания](database/tradecase_empty_case_cancel_20261022.md): две миграции и неизменный повтор прошли;8EA/HARD4, тара освобождена, волна608 DONE с возвратом потребности. Ручной повтор/гонка и отзыв прав проверены,6UI возврата прошли.
- [СНС/BLC: ручной вес пустого короба](database/tradecase_manual_case_tare_20261022.md): scoped запись0.1кг, настоящий отбор2EA и контроль2.1кг прошли;6UI1440/390 и9offline. Гонка перевзвешивания с первым отбором и два отрицательных итоговых контроля прошли; противоположная очередность и оборудование ещё не приняты.
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
- [СНС/BLC — выполнение19.10](roadmap/tradecase_execution_20261019.md): T01 завершён, остальные спринты частично; [матрица45](roadmap/tradecase_acceptance_20261019.md), [Oracle](database/tradecase_contract_20261019.md), [источники](sources/tradecase_20261019.md), [история](roadmap/tradecase_execution_20261019_history.md). Три режима выкупа/два выезда/возврат1+10/обратное направление1 проверены локально; добивка/маршрут/промышленные подключения открыты. Claude4/4 RELEASE; цикл остановлен18:20сопозданием, [состояние](../coordination/tradecase-20261019/STOPPED.json); завершение не объявлено.
- [Описание работы в системе RETAILCASE](components/retailcase_operations_guide_20261019.md#публикация-19102026-и-повторная-проверка-текста): опубликовано в GitHub/Pages и главном README;43должности/19процессов/272обязанности,597UI-checks. Расписание19.10 завершено; СНС/BLC продолжен21.10 новым поручением.
- [SQL TRADECASE19.10](runbooks/tradecase_sql_review_20261019.md):200строк203→5SQL, CASE owner через целевые ключи; cold-задержки, нагрузка и решения по каждому долгому блоку сохранены.
- [Проверка скорости вместе с функциональностью](runbooks/slow_sql_review.md#поручение-владельца19102026-скорость-вместе-с-функциональностью): UI/API/SQL, причина→исправление→сравнение; владелец разрешил код/SQL/индексы, миграции и live verify обязательны.
- [Локальный продукт17.10: запуск и ограничения](runbooks/retailcase_local_product_20261017.md): KPI V2/25EA→магазин/restart/UI PASS; [REPORT](database/retailcase_case_report_scope_20261017.md) и [MOVE](database/retailcase_case_move_scope_20261017.md) APPLIED; C0124/C0125 RELEASE; [контекст](../coordination/retailcase-claude/RESUME_TO_20261017_1100.md), Ponytail — [AGENTS.md](../AGENTS.md).
- [Погрузка отдельного места по области](database/retailcase_single_load_scope_20261016.md): dev APPLIED/4SHA;30HTTP, CASE1150→магазин25EA, rollback/REV/replay/revoke PASS.
- [Финансовые области](database/retailcase_finance_scoped_20261015.md): rates APPLIED/1SHA;20HTTP rates/monthly/XLSX/PLATFORM shell +composite/independence native PASS.
- [Возврат CASE по области](database/retailcase_case_return_scope_20261016.md): APPLIED/3SHA;25EA/10HTTP/rollback/REV; [ошибка компиляции и предотвращение](incidents/retailcase_case_return_compile_20261016.md), TRANSFER отдельно.
- [Передача CASE по области](database/retailcase_case_transfer_scope_20261016.md): APPLIED/4SHA;24EA/11HTTP +immutable receipt/assignment-version; C0121/C0122 scoped UI PASS, TEST access retired.
- [Полный HU/отправление/выгрузка](database/retailcase_full_shipping_scope_20261016.md): HU/DEPART37HTTP25EA FULL; UNLOAD APPLIED/14HTTP25EA/rollback/REV PASS, повторный QC обязателен.
- [Водитель SELF](database/retailcase_driver_self_scope_20261016.md): APPLIED/6SHA/ERROR0/INVALID0;40HTTP SELF/expiry/delegation/composite +native rollback/REV/independence PASS.
- [Погрузка: области чтения](components/retailcase_loading_scoped_read_20261016.md):11HTTP WARE/GROUP/twoRC; живой role-only UI390, отказ очищает прежние рейс/окна.
- [Слоты/упаковка HU по области](database/retailcase_hu_slot_scopes_20261016.md): dev APPLIED/5SHA;5EA/два слота,12HTTP/rollback/REV PASS.
- [Плановые HU и прямые CASE scopes](database/retailcase_hu_task_scopes_20261016.md): dev APPLIED/10SHA +policy2SHA;14HTTP, назначение/START/COMPLETE/REV PASS.
- [Вложенный BOX manifest](database/retailcase_nested_box_manifest_20261016.md): dev APPLIED/8SHA; nested CASE1148→магазин25EA; multi-store handover снят владельцем16.10, не реализовывать.
- [Неизвестный START разгрузки](database/retailcase_unloading_intent_20261016.md): dev APPLIED/7SHA; late START/rollback/REV и новая original/control race PASS, UI390 PASS.
- [Окно и прибытие машины](database/retailcase_delivery_time_20261016.md): dev APPLIED/9SHA; ON_TIME/FULL25EA, окно/exact retry/прибытие UI390 PASS.
- [KPI proof отбора](database/retailcase_kpi_pick_proof_20261016.md): dev APPLIED;4rates/self/foreign, KPI390/help200/компактные фильтры PASS; полнота WORK false, зачёт недостачи уточняется.
- [План завершения](roadmap/retailcase_finish_two_claude_20261016.md): до17.10 11:00MSK; Codex F1/F3/F5, два запроса Claude на UI и финальный прогон. Multi-store снят, [контекст продолжения](../coordination/retailcase-claude/RESUME_TO_20261017_1100.md).
- [Согласованные KPI](concepts/retailcase_kpi_passports_20261015.md): строка — завершившему, коробки — по своим отборам; прибытие в окно и полная приёмка; наблюдённые API/UI реализованы.
- [Базовые HU-команды по области](database/retailcase_hu_scoped_execute_20261016.md): dev APPLIED/5SHA/INVALID0;3EA/14HTTP/rollback/REV PASS; CASE/slot/task расширены отдельными инкрементами.
- [Ручной QC в погрузочном архиве](database/retailcase_manual_qc_load_origin_20261016.md): dev APPLIED/3SHA/INVALID0; две CASE manual proof, без фиктивного capture, погрузка26EA PASS.
- [Ручной вес складского контроля](database/retailcase_manual_warehouse_qc_20261016.md): dev APPLIED/4SHA/INVALID0; два QC/replay/conflict, UI exact retry и9 focused tests PASS; электронная ветка сохранена.
- [Межскладское продолжение CASE](database/retailcase_interware_case_bridge_20261016.md): dev APPLIED/34SHA + scalar fix; ASM1+BOX24+EA1 → два плеча → магазин26EA PASS; custody/заказы1/25 без повторов, SQL backlog зафиксирован.
- [Разделение Codex/Claude C0117](roadmap/retailcase_codex_claude_c0117_20261016.md): RELEASE K-0068 интегрирован, root9 UI checks и общий gate PASS; native матрица остальных ролей/subtree остаются.
- [Простая справка](components/retailcase_simple_solution_rule_20261016.md): файл и ссылка; [offline-read](components/retailcase_public_offline_knowledge_20261016.md) трёх публичных инструкций, без кэша закрытых статей.
- [Ручной ввод веса](database/retailcase_manual_weight_20261016.md): dev APPLIED + persist fix/INVALID0; новая3EA приёмка/rollback/replay/custody PASS; Claude C0116 RELEASE, root live UI план save/cancel и акт магазина PASS.
- [Пустая сборка после недостачи](database/retailcase_empty_short_disposition_20261016.md): dev APPLIED/4SHA/INVALID0; DONE/SHORT_PICKED сохранены, своя тара освобождена, волна574 DONE.
- [Исторический итог к23:00](roadmap/retailcase_execution_2300_20261015.md): baseline перед новым поручением выполнить блоки1–3.
- [Текущие очереди и области склада](components/retailcase_queue_scoped_read_20261015.md): блок1 в работе; scoped read/отзыв/потребители проверены, write и блоки2–3 ещё открыты.
- [Исполнение сборки на весах](database/retailcase_assembly_scoped_execute_20261016.md): dev APPLIED; TEST ASM1140/12HTTP/REV PASS; mixed HU26EA далее проверен отдельно, hardware остаётся.
- [Назначение аудитора и пересчёт](database/retailcase_inventory_task_scope_20261016.md): dev APPLIED; shortage→claim→count/replay/scopes PASS,19 HTTP pairs/max258мс, QA retired; остаток блока1 открыт.
- [Legacy + роль на другом складе](database/retailcase_additive_legacy_task_scopes_20261016.md): dev APPLIED/23SHA/INVALID0;6 HTTP/replay/отзыв PASS, новая quantity матрица ещё открыта.
- [HU thermal admission](database/retailcase_hu_thermal_admission_20261016.md): dev APPLIED/13SHA;15 native checks/mixed26EA/revoke PASS; manifest/interWARE выполнены, multi-store снят владельцем.
- [Expected consolidation manifest](database/retailcase_consolidation_manifest_20261016.md): dev APPLIED/15SHA;16HTTP/replay/revoke, missing child blocks SHIP; CASE interWARE выполнен, multi-store снят владельцем.
- [Список планов консолидации](database/retailcase_consolidation_list_20261016.md): dev APPLIED/7SHA/INVALID0; live page/cursor PASS, отдельная scoped матрица открыта.
- [Independent shortage decisions](database/retailcase_short_independent_scope_20261016.md): dev APPLIED/7+4SHA/INVALID0;10HTTP/REV lock, ACCEPT_SHORT count/RESTORE PASS; empty CASE disposition закрыт отдельным инкрементом.
- [Права, знания и складские рабочие места — living checklist](roadmap/retailcase_access_knowledge_plan.md). Все спринты ещё не закрыты.
- [Завершение спринтов с одним запросом Claude](roadmap/retailcase_finish_single_claude_20261015.md): C0116 RELEASE и root live integration PASS; остальные backend gates открыты.
- [ТМС-2 — план17спринтов](roadmap/transport_execution_plan.md), [ТЗ диспетчера](requirements/transport_dispatch_tz.md).
- [Экономный режим разработки](components/retailcase_development_cost_skills_20261015.md): local defaults Sol6.1/low/priority; рекомендован Standard, конфиг не изменён. Один исполнитель, отдельное критическое ревью.
- [HU: текущие области чтения](components/retailcase_hu_scoped_read_20261015.md): WARE/GROUP/revoke actualHTTP PASS, тестовые назначения закрыты.
- [UI и сканирование магазина](components/retailcase_operator_ui_evidence_20261015.md): GS1-128, точный повтор, живой shift production UI390; recovery scope и performance остаются открытыми.
- [Масса дерева и подготовленный SHIPPING_GROSS](concepts/retailcase_hu_mass_projection_20261015.md): v8 связывает freeze с версией ожидаемого состава; full freeze/capture/use/QC/loading открыты, кандидат не установлен.

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

- [Защита передачи добивки волне](database/tradecase_topup_adoption_guard_20261022.md): подготовлено узкое исключение для зафиксированного запуска; живой перенос ещё проверяется.


- [Сверка добивки после отмены волны](database/tradecase_topup_cancelled_wave_20261022.md): подготовлена сверка освобождённого удержания без повторного списания; применение и приёмка впереди.


- Текущая приёмка добивки: полный перенос40шт./sameRID/units и отмена со сверкой прошли;17SHA/INVALID0. Частичный перенос и полная матрица остаются открыты. Claude C0149 выполняет двор; root принимает маршрут C0148.


- [Порядок завершения после замечания владельца](roadmap/tradecase_execution_20261019.md#коррекция-порядка-работы-по-замечанию-владельца2210): исходные критерии отдельно от дополнительных проверок; следующий пакет — исправленный двор C0150.


- [Продолжение после перезапуска22.10](../coordination/tradecase-20261019/RESUME_LATEST.md): проверенные результаты, остатки, API и очередной шаг; C0150 сдан кандидатом, C0151 передан, ACK ожидается.

- [Двор/ворота22.10](database/tradecase_yard_visit_20261022.md): миграция применена с откатом/повтором; native цикл и история прошли в откатываемой fixture; scopes/конкуренция/HTTP ещё открыты.

- [Двор: HTTP после apply](database/tradecase_yard_visit_20261022.md#проверки): owner/actor/revoke/retireduser прошли17HTTP, тестовые визиты отменены; API75144/session92806.

- [Двор: настоящий экран1440/390](database/tradecase_yard_visit_20261022.md#экран-после-применения): API200, без переполнения/JS-ошибок; вход из сводки обновлён.

- [Адрес склада по назначенной роли23.10](database/warehouse_depot_scope_20261023.md): исправление выявленного отказа scoped сотруднику; кандидат до Oracle apply.

- [Порядок блокировок адреса склада](database/warehouse_depot_scope_20261023.md): отдельное исправление scope-precheck, обязательная живая проверка продолжается.
