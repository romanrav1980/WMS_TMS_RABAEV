# TMS Wiki Index

Короткий вход в проект. Открывать только страницы по текущему вопросу. Исторические статусы и полный каталог сохранены в [архиве оглавления](sources/wiki_index_catalog_20261015.md); они не заменяют актуальную карточку компонента.

## Текущая работа

- [Атлас процессов и должностей RETAILCASE](components/retailcase_operations_guide_20261019.md): сайт4175;43 инструкции после редакторского чтения/272 обязанности, прямые ссылки на работу и99экранных назначений,19процессов/изометрия; СНС/BLC — TRADECASE.
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

## Logical Branches

[Oracle, C#, терминалы, интеграции](sources/wiki_index_catalog_20261015.md#logical-branches).

## Subprojects

[Подпроекты](sources/wiki_index_catalog_20261015.md#subprojects).

## Architecture

[Архитектурные страницы](sources/wiki_index_catalog_20261015.md#architecture) · [Права и встроенные знания](architecture/retailcase_scoped_access_and_knowledge.md).

## Database Mirror

[Oracle mirror](database/index.md) · [Изменения Oracle](database/oracle_change_protocol.md) · [WARES: PK и название как уникальный ключ](database/retailcase_wares_identity_keys_20261015.md).

## Incidents

[Инциденты и принятые исправления](sources/wiki_index_catalog_20261015.md#incidents).

## Concepts

[Дерево грузовых мест](concepts/retailcase_nested_hu_consolidation_20261015.md) · [Паспорта KPI](concepts/retailcase_kpi_passports_20261015.md) · [Остальные понятия](sources/wiki_index_catalog_20261015.md#concepts).

## Runbooks

[Приёмка сценария](runbooks/evidence_driven_process_testing.md) · [Долгие SQL](runbooks/slow_sql_review.md) · [Полный каталог](sources/wiki_index_catalog_20261015.md#runbooks).

## Roadmap

[Права/знания](roadmap/retailcase_access_knowledge_plan.md) · [ТМС-2](roadmap/transport_execution_plan.md) · [Остальные планы](sources/wiki_index_catalog_20261015.md#roadmap).

## Requirements

[Требования и версии](sources/wiki_index_catalog_20261015.md#requirements).

## Control Files

[AGENTS.md](../AGENTS.md) · [WIKI_SCHEMA](WIKI_SCHEMA.md) · [Архитектурная политика](../config/architecture/retailcase-policy.json) · [Остальные контрольные файлы](sources/wiki_index_catalog_20261015.md#control-files).
