# Полный каталог и исторические обновления wiki

Снимок прежнего оглавления15.10.2026. Исторические статусы не считаются текущими. [Короткий вход](../index.md). Относительные ссылки перенесены с сохранением исходных целей.

- [HU read scopes](../components/retailcase_hu_scoped_read_20261015.md): actual WARE/GROUP HTTP200, revoke/member-remove403, flat0/no admin login; фикстура retired без quantity effects.16 SQL/local pairs/max260ms. Live UI на Vite отделён от production-bundle mock.
- [Текущий контекст к23:00](../roadmap/retailcase_execution_2300_20261015.md): native CASE1139 отбор/CLOSE/HTTP replay/RETURN PASS,24/H0; actual time и UI доказательства, текущие границы и следующая очередь.
- [SQL после совместной проверки](../components/retailcase_joint_sql_review_20261015.md):63 API/51 local HTTP, max335ms; native cumulative prepare/execute363/325ms. Background845ms и catalog5.9s имеют владельцев и решения; это не нагрузочный пилот.
- [UI: время, камера, Гант и дерево HU](../components/retailcase_operator_ui_evidence_20261015.md): реальное чтение и отдельные production/mock проверки; software camera stream не является физическим commissioning.
- [Масса дерева HU](../concepts/retailcase_hu_mass_projection_20261015.md):37 pure cases PASS; SHIPPING_GROSS read подготовлен, root исправил locking/dirty-TX границы,15 boundary tests PASS. Native SQL не установлен, archive/consumer/QC ещё отсутствуют.
- [Ключи складов](../database/retailcase_wares_identity_keys_20261015.md): APPLIED PK(ID)+mandatory UNIQUE(NAME),291 пар сохранены,4 duplicate/null проверки PASS;4 actual-time FK используют новый PK.
- [CASE/TASK metadata-intent fence](../database/retailcase_resource_metadata_intents_20261015.md): APPLIED/readback7 exact/INVALID0;8 caller-rollback checks и4 actualHTTP группы с race/revoke/late fence PASS; CASE1139 IN_PROGRESS, UI recovery проверяется отдельно.
- [Стоимость разработки: навыки и режим работы](../components/retailcase_development_cost_skills_20261015.md): local defaults уже Sol6.1/low, но priority/Fast; первая рекомендация — Standard. Сокращены параллельность/контекст/повторные проверки. Конфиг не менялся, полного usage сессии нет.
- [Последняя UI-проверка](../../reports/retailcase/2026-10-15/execution-1900/checkpoint.md): damaged unloading intent больше не сбрасывается и сохраняет блокировку после reload;131 native control с help/title, финальные gate/build/PWA PASS.
- [Проверенный итог к18:45 МСК](../../reports/retailcase/2026-10-15/execution-1900/checkpoint.md): Claude C0113/C0114,25 CASE UI+8 store UI,48 pure tests и quality gate PASS; TEST fixtures retired24/H0. Mixed HU/SHIPPING_GROSS/runtime KPI/аппаратный пилот ещё открыты.
- [Следующий источник KPI](../roadmap/retailcase_picker_time_source_increment_20261015.md): фактические aware WORK/PAUSE/SHIFT transitions, owner TX/current scopes и полнота as_of; live типы legacy clocks проверены, исторический backfill не предполагается.
- [CASE work UI](../components/retailcase_case_work_ui_20261015.md):25 rendered fault/recovery cases и production role-only native read/helpv3 на3ширинах PASS; полный gate1059/0/72+24+обаTS PASS; native metadata-abandon ещё открыт. Реальный Claude C0113 review интегрирован; TEST CASE1138 штатно отменён,24/H0 и все назначения отозваны.
- [Время для KPI: ядро расчёта](../components/retailcase_picker_time_denominators_20261015.md):24 focused и независимые100 interval sets PASS; union/паузы/DST/as_of/no-data. Runtime подтверждённых интервалов и числители ещё открыты.
- [Исполнение к17:43](../roadmap/retailcase_access_knowledge_plan.md): TASK_ASSIGN/START APPLIED и TEST cleanup; новый `/case-work/`,21 mocked checks и actual role-only read/help3viewport PASS. Реальный Claude review после18:00; полный mixed-HU сценарий AK06-F открыт.
- [KPI выработки: решение владельца](../concepts/retailcase_kpi_passports_20261015.md): приняты оба знаменателя — фактическая сборка без зарегистрированных пауз и смена с паузами; в каждом строки/час и коробки/час. Aware интервалы и атрибуция строк ещё требуют реализации/уточнения.
- [Назначение и старт обычного складского задания](../database/retailcase_task_scoped_assignment_20261015.md): native/API APPLIED,28 actualHTTP calls, concurrent retry/revoke и19 unit PASS; TEST1188/1189 канонически отменены, сессия58 закрыта; qty не менялось.
- [AK06-F: паллета-матрёшка](../roadmap/retailcase_access_knowledge_plan.md#ak06-f--смешанная-многоуровневая-консолидация--добавлено-владельцем1510): добавлен обязательный смешанный ASM/rack сценарий (native readiness → изолированный TEST → компенсация), план ожидаемых поддеревьев, независимый вес внешнего HU, совместимость зон, CASE-aware межскладской мост и scoped приёмка поддерева.
- [Терминал весовой сборки](../runbooks/retailcase_assembly_scale_terminal.md): UI запросы EMPTY/FINAL с подтверждённым нулём и привязкой preparedСТ;52 rendered checks/qualitygate PASS; setup identity и3viewport повтор PASS; исправлен публикуемый Work-раздел, новая публикация отдельно.
- [Исполнение спринтов к16:45](../roadmap/retailcase_access_knowledge_plan.md): полный TEST OPC цикл сборки/компенсация, CASE roles и ZERO проверены; UI/TASK_ASSIGN ещё выполняются, аппаратный пилот открыт.
- [Спецификация шлюза весов](../../docs/integrations/weighing-gateway-opc40200.md): обновлён применённый request/claim/ZERO обмен и отдельный ASM_FINAL; добавлен проект внешнего веса вложенного HU/AK06-F. Аппаратный пилот открыт.
- [Собственная рабочая сессия CASE](../database/retailcase_case_resource_commands_20261015.md): 12 native +10 actual HTTP +5 own-session guard groups PASS; role-only CLAIM/START, конкуренция, отзыв и точный replay. QA1138/session55 активны до UI C0113; GROUP/NETWORK/DC native pure-read admission10 групп PASS, write execution/hardware отдельно.
- [Рабочее место комплектовщика](../runbooks/retailcase_case_work_terminal.md): сервер CLAIM/START проверен; UI реализован, независимая приёмка продолжается; инструкция APPROVED для локальной публикации.
- [ASM_FINAL identity v3](../database/retailcase_assembly_final_snapshot_20261015.md): APPLIED10/0/source6EXACT; encrypted TEST FINAL/rawMATCHED и native FINALIZED/exactrepeat, rollback history guard PASS; OPEN mutation negatives pending.
- [Финальный вес сборки: выявленная зависимость](../incidents/retailcase_assembly_final_transit_signature_20261015.md):1EA software APPLIED/replay PASS; close+bind и отдельный ASM_FINAL/v3 FINAL→FINALIZED/exactrepeat доказаны; shipping cell guards сохраняются.
- [Сборочный пост → подготовленная отгрузка](../database/retailcase_assembly_shipping_context_20261015.md): APPLIED5/0 read-only context, actual existing close/bind; последующий ASM_FINAL snapshot отдельно, stock writer не меняется.
- [Складская очередь весов](../database/retailcase_warehouse_scale_requests_20261015.md): APPLIED + scalar SQL forward fix,20 native/11 actualHTTP checks, claims/expiry/revoke/history; shipping whole-pallet отдельно.
- [OPC клиент складской очереди](../components/retailcase_warehouse_opc_requests_20261015.md): actual encrypted localhost OPC→HTTP, durable claim/bundle, GROSS only; аппаратный пилот открыт.
- [Отказ от несозданного запроса сборки](../database/retailcase_assembly_intent_abandon_20261015.md): APPLIED/source4 exact/INVALID0, 11 native/HTTP checks и production UI360/390/1440 PASS; позднее создание блокируется, товарного эффекта нет.
- [Восстановление сборки после расхождения](../database/retailcase_assembly_recovery_20261015.md): APPLIED16/0, native HOLD→отдельный контролёр→измеренная сверка. [OPC1.2](../database/retailcase_reconciliation_evidence_20261015.md): APPLIED6/0, encryptedOPC→HTTP→native CANCELLED/OPEN, без товарного эффекта. UI восстановления:23 rendered проверки; production native чтение контролёра и help проверены.
- [Терминал сборки: восстановление UI](../components/retailcase_assembly_recovery_ui_20261015.md):23 rendered mocked checks; [production native чтение](../../reports/retailcase/2026-10-15/assembly-scale/production-native-ui.json)360/390/1440 и локальные help links PASS; обе PWA offline оболочки PASS.
- [Запуск волны: продолжение после сбоя](../database/retailcase_wave_launch_continuation_20261015.md): APPLIED14/0,20 native/HTTP/compat checks и21 unit PASS; потеря ответа, revoke и2 одновременных повтора, canonical compensation P24/H0, история сохранена.
- [OPC assembly binding: native приёмка](../database/retailcase_assembly_evidence_binding_20261015.md): обе фазы и восемь неправильных ссылок, replay/revoke/hash/append-only PASS; shape fix4/0, старая v1.0 native регрессия PASS.
- [Сборка на весах: native](../database/retailcase_incremental_assembly_20261015.md):27 statements/0 errors, source13 exact/INVALID0; положительный CASE_PICK_CONFIRM с caller rollback, расширенная приёмка продолжается. [OPC v1.1 binding](../database/retailcase_assembly_evidence_binding_20261015.md):APPLIED6/0, исходная тара вместо фиктивного нуля.
- [Часы товарной операции](../database/retailcase_stock_operation_clock_20261015.md):APPLIED,8 native checks PASS; время APPLIED внутри TX, без backfill.
- [Инструкция поста сборки](../runbooks/retailcase_assembly_scale_terminal.md): опубликована в локальной базе знаний как assembly-scale v9; исходная wiki revision проверена,2 локальные связанные статьи.
- [Паспорта KPI и фактические источники](../concepts/retailcase_kpi_passports_20261015.md): строки/час, коробки/час, плановое окно и стратегия приёмки; недостающие правила явно на согласовании, legacy timestamps не выдаются за UTC.
- [Исходные OPC показания в Oracle](../database/retailcase_opc_scale_evidence_20261015.md): APPLIED/INVALID0; [native приёмка](../database/retailcase_opc_scale_evidence_acceptance_20261015.md), точные повторы/исходный sender/SHA/append-only, три контекста. Архив не является товарной командой.
- [Складской HTTPS шлюз весов](../components/retailcase_warehouse_scale_gateway_20261015.md): PICK/EMPTY_TARE/FINAL_GROSS, 20 focused +2 shared tests, три native ACK/replay; без нового stock effect.
- [Завершение назначенного задания по областям](../components/retailcase_task_scoped_write_increment_20261015.md): исправленный native комплект APPLIED/INVALID0,20 native+реальных HTTP checks и13 unit PASS; назначение и фактический склад проверяются в native.
- [Актуальные восемь спринтов и распределение](../roadmap/retailcase_access_knowledge_plan.md#актуальное-распределение-после-уточнения-весовой-сборки--15102026): Codex/Claude, очередь заданий→OPC шлюз→отгрузка→накидывание→ресурсный Гант→KPI/пилот; назначения Claude не означают активную сессию.
- [Сборка накидыванием: товар к человеку](../components/retailcase_weighing_gateway.md#сборка-накидыванием--решение-владельца-15102026): решение владельца — подтверждение каждой укладки кнопкой или автоматически по стабилизации/приросту веса и отдельный финальный замер; целевой workflow описан, реализация впереди.
- [Шлюз весов склада и магазина](../components/retailcase_weighing_gateway.md): принято OPC 40200 v2.00 → общий шлюз → HTTPS API; [полная спецификация](../../docs/integrations/weighing-gateway-opc40200.md), текущие адаптеры и необходимые расширения разделены.
- [API-запрос измерения весов](../database/retailcase_store_scale_requests_20261015.md): APPLIED/INVALID0,11 native rollback +6 live API +15 HTTP tests; exactrequest и native ACK, без физического оборудования.
- [Пустой черновик рейса](../database/retailcase_transport_empty_draft_20261015.md): APPLIED,7 native +9 scoped regressions PASS, защитные ограничения сохранены.
- [Положительная текущая шкала v7](../database/retailcase_transport_time_scoped_view_20261015.md):7 native rollback PASS, source-change/revoke; AK06-CLOCK01 закрыт.
- [Приложение магазина: результат интеграции](../../reports/retailcase/2026-10-15/store-app/report.md): самостоятельный PWA, три native стратегии, 11 live +8 production UX сценариев, offline оболочка; физический пилот отдельно.
- [Приложение приёмки магазина](../runbooks/retailcase_store_receiving_app.md): самостоятельный `/store/`, три стратегии и сохранённая команда; инструкции подключены к штатной публикации знаний.
- [Приложение магазина: сервер и native](../database/retailcase_store_app_strategies_20261015.md): APPLIED/INVALID0, scoped STORE без admin-login, final-leg filter, caller-owned receipt rollback и exact replay dev PAPER_COUNT; UI/PWA интеграция продолжается.
- [Текущий допуск приёмщика и dev-квитанция](../database/retailcase_store_app_strategies_20261015.md): PREPARED guard replay; dev THERMAL1168 приёмка сохранилась из-за COMMIT NativeAPI, журнал сохранён, policy восстановлена.
- [Только финальная поставка магазину](../database/retailcase_store_app_strategies_20261015.md): PREPARED final-leg guard preview/list по существующему trigger; промежуточные плечи не являются приёмкой магазина.
- [Порядок блокировок scoped-команд](../database/retailcase_store_app_strategies_20261015.md): PREPARED follow-up, revision guard после begin_plan до policy/resources; strict dirty-transaction invariant сохранён.
- [Приложение магазина: native стратегии](../database/retailcase_store_app_strategies_20261015.md): PREPARED, PAPER_COUNT с полным пересчётом и реквизитом; scoped STORE и legacy binding.
- [Решение владельца: приложение магазина и KPI](../concepts/retailcase_store_app_and_kpi_owner_20261015.md): отдельное приложение обязательно; три стратегии приёмки, строки/час и коробки/час, точное плановое окно; C0095 Claude.
- [Нативная область запуска](../database/retailcase_wave_launch_scope_20261015.md): PREPARED, final guard по фактическому складу вместо плоского права; продолжение отдельно.
- [Текущее исполнение AK/KH](../roadmap/retailcase_access_knowledge_plan.md): актуальная матрица8инкрементов, ClaudeK0056/Codex интеграция; полный объём ещё открыт.
- [Складские очереди по областям](../components/retailcase_warehouse_scoped_reads_20261015.md): CASE5/tasks5/sessions4 livePASS, фильтр доlimit, межскладское задание по обеим сторонам.
- [Восстановление запуска волны](../components/retailcase_wave_launch_recovery_20261015.md): прежний operation_id; запуск APPLIED и незавершённое продолжение различаются, native сквозная приёмка ещё открыта.
- [Время рейса → общий Гант](../database/retailcase_transport_time_scoped_view_20261015.md): APPLIED/INVALID0, pure native view по всему составу; source hash определяет действительность approval.
- [Старший смены: пакет готовности волн](../database/retailcase_wave_scoped_views_20261015.md): до50ids/одинREADONLYsnapshot/4источника, native scopes и ошибки отдельно; C0088 READY дляClaude.
- [Волны и время: scoped view](../database/retailcase_wave_scoped_views_20261015.md): APPLIED,8live checks; native по складу волны, read-only; запуск/отмена остаются отдельными.
- [Диспетчер: scoped list/detail/Гант/Excel](../components/retailcase_dispatch_scoped_reads_20261015.md):8livechecks, mixedобласти/revoke, полныйXLSX; businessrows read-only.
- [Scoped-редактирование рейса: native](../database/retailcase_transport_scoped_edit_20261015.md): APPLIED/INVALID0,9native checks, guard на входе команды; чистая проверка фактического склада сохраняет read-only preflight.
- [Источник общего Ганта и задания](../architecture/retailcase_resource_gantt_shift_supervisor.md): /api/resources/timeline, native scope/отзыв/чужой склад PASS; RRL_WAREHOUSE_TASK + CASE-сборка, без третьей копии работы.
- [Общий Гант и старший смены](../architecture/retailcase_resource_gantt_shift_supervisor.md): решение владельца — ричтраки/комплектовщики/ворота/машины, будущие волны/риски/текущая сборка; исполнение C0074.
- [Цифровой двойник → конкретный рейс](../../reports/retailcase/2026-10-15/twin-integration/report.md): deep link, API503 без демоподмены; live UI/gate PASS, C0072–C0073 переданы Claude.
- [Рабочие места в стиле цифрового двойника](../architecture/retailcase_scoped_access_and_knowledge.md): существующая сцена, задания/ресурсы и план/факт; Claude UI, Codex scoped API/Oracle, уточнение C0072.
- [Scoped-согласование расходов](../database/retailcase_finance_scoped_20261015.md): native guards, автор/LOGIST/FINANCE разделены,6rollback-only checks PASS, без права изменения ставок.
- [Oracle прав и знаний](../database/retailcase_scoped_access_knowledge_20261014.md): APPLIED/INVALID0,11nativecases+liveHTTP PASS, роли с областями/мандатами, редакции знаний и квитанции; UI и бизнес-интеграция продолжаются.
- [Идентичность RUSERS](../database/retailcase_rusers_identity_20261014.md): UK/FK и normalized-login UNIQUE, по прямому поручению удалён один soft-deleted дубль, backup в Oracle, INVALID0.
- [Принято: права и встроенные знания](../architecture/retailcase_scoped_access_and_knowledge.md): роли с областями и help для действий; [8 спринтов](../roadmap/retailcase_access_knowledge_plan.md), Oracle-модель и UI применены; актуальные проверенные инкременты AK03–AK08 и открытые границы в плане.
- [Начало ролевой модели retailcase: ревью](../components/retailcase_roles_initial_review_20261014.md): 10 предварительных ролей, reuse существующих API/экранов; замечания по назначению, совмещению ролей и KPI; Claude получил C0055.
- [retailcase: автоматический установщик и имя продукта](../database/retailcase_branding_20261014.md): [инструкция](../../docs/install-retail-case.md), [report75](../../reports/retailcase/2026-10-13/75-automatic-install-branding.md), минимальная Oracle+API+UI установка; чистая Windows репетиция отдельно.
- [Комплект Oracle и установка с нуля](../database/retailcase_release_20261014.md): актуальный SQL-снимок, минимальное наполнение, [описание системы](../subprojects/retailcase_system_reference.md), [каталог объектов](../database/release_20261014/README.md), [методы/API](../components/api_reference_20261014/README.md). Новый ролевой UX поручен Claude [C0049](../../coordination/retailcase-claude/TASK_C0049.md).
- [Текущий кодовый объём RETAILCASE18/18 завершён — report73](../../reports/retailcase/2026-10-13/73-current-sprint-code-completion.md): план76, Oracle/API/UI и ночная Ганта интегрированы, gate778/0/73 +24tests +обаTS PASS. Внешняя/независимая/промышленная приёмка отдельно, госшлюз отложен владельцем.
- [Ночные операции Ганта: сервер](../components/retailcase_gantt_day_overlap_20261014.md): пересечение суток вместо одной даты отгрузки, bounded20000/error, SQL35мс; UI C0034 у Claude.
- [Актуальный план75](../requirements/retailcase_delivery_v55/implementation_plan.md): 17 из18 текущих кодовых объёмов реализованы; NI08.1 UI: C0033 сдан, C0034 ночная Ганта/mobile в работе. Приёмка/реальные внешние интеграции отдельно; deadline15.10 07:00МСК.
- [Магазин → окна и допуск машины](../database/retailcase_store_profile_20261014.md): четыре миграции APPLIED/INVALID0, native и live профиль PASS, report71; текущий остаток NI08.1 — C0033/C0034. Срок продолжения:15.10.2026 07:00 МСК либо все спринты.
- [Claude и Codex: карточки магазина и ТС](../components/retailcase_store_fleet_coordination_20261014.md): Claude: очередь C0029 → C0032 → C0033 без ожидания повторного разрешения; Codex: native интеграция; C0023 завершён.
- [Геозоны и атомарный GPS](../components/retailcase_geofences_gps_20261014.md): report70, реальные поля/ADDR, история+позиция в одной транзакции, запоздалый пакет не откатывает позицию; наблюдение не меняет произвольную разгрузку.
- [Шлюз маркировки отложен владельцем](../../reports/retailcase/2026-10-13/69-ni043-gateway-deferred.md): local queue/audit/diagnostics готовы; real sender отсутствует как код. Claude C0025 добавляет bounded каталог магазинов; ведомый исправляет реальные колонки и адресную безопасность GPS.
- [Ускорение СТ, report68](../../reports/retailcase/2026-10-13/68-ni022-narrow-header-group.md): HTTP1.038с/200, узкая группировка, live unique index подтверждён. Claude C0025 выполняет выбор областиQC. Шлюз маркировки владелец отложил отдельно; локальная диагностика NI04.3 обновлена.
- [Итог совместного исполнения —18 спринтов](../../reports/retailcase/2026-10-13/67-sprint-code-readiness.md): редакция72, назначенные кодовые блоки обоих исполнителей RELEASE; NI05.1 native audit/label guard и NI08.1 route/rest применены. Внешняя/независимая приёмка и performance NI02.2 отдельно.
- [Адресный контроль, report65](../../reports/retailcase/2026-10-13/65-ni051-scoped-quality.md): Oracle/API/UI, exact replay и текущий экран114; F1 native positive в работе. [Решение по SQL СТ](../../reports/retailcase/2026-10-13/66-ni022-wide-page-decision.md): ухудшающий hint отвергнут. Gate759/0/73 PASS.
- [Совместное исполнение, редакция71](../requirements/retailcase_joint_execution_20261014.md): NI08.1 native REST/final approval сдан; NI05.1 storage proof и положительный QC в работе. [Поручение ведомому](../../coordination/retailcase-codex/TASK_CURRENT.md).
- [Адресные правила контроля NI05.1](../database/retailcase_ni051_scoped_policy_20261014.md): подтверждён обязательный кодовый остаток NS41; Oracle в работе. Ведомый реализует NI08.1 единый маршрут с перерывами. Все спринты ещё не завершены.
- [Контроль → назначенный рейс](../components/retailcase_ni051_control_label_20261012.md): report64, same-snapshot assignment, SQL4мс. [Возврат → точное размещение](../components/retailcase_ni062_receipt_recovery_20261014.md): ведомый сдал, фильтр до limit100; gate755/0/73, encodingPASS.
- [Погрузка: восстановление команды](../components/retailcase_ni052_loading_recovery_20261014.md): report63, исходный operation_id и повтор после reload.
- [Приёмка: неотправленный ввод](../components/retailcase_ni011_form_draft_20261014.md) и [межскладская приёмка](../components/retailcase_ni061_group_recovery_20261014.md): ведомый Codex завершил блоки, далее возврат → размещение.
- [Реестр конфликтов остатков](../components/retailcase_ni072_stock_keys_20261014.md): report62, keyset UID+CELL, полная навигация по50, SQL7мс; ошибочный запас не создавался.
- [Параллельные функциональные блоки](../components/retailcase_parallel_delivery_20261014.md): report61; Codex четыре блока, ClaudeC0020 сдан; C0023 передан Codex по лимиту Claude.
- [Назначение складского задания](../components/retailcase_ni032_task_family_20261014.md): report60, карточка сохраняется вне фильтра, состояния кнопок; [ведомый Codex NI07.2](../components/retailcase_ni072_stock_keys_20261014.md) — ключи конфликтов20/показатель,65мс.
- [Цепочка складского задания](../components/retailcase_ni032_task_family_20261014.md): этапы/факт/остаток/следующее действие, report59, shots105–106, SQL2–3мс. ClaudeC0018 → поправкиC0021 → C0020тара.
- [Совместное исполнение спринтов](../requirements/retailcase_joint_execution_20261014.md): пять этапов, Codex — склад/ядро, Claude — диспетчер/тара/доставка/финансы/UI; сейчас W1406 иC0018, затемC0020.
- [Внешние документы сверки](../components/retailcase_ni072_documents_20261014.md): report58, ERP/регуляторные ID, прямое досье4459/без полного списка, SQL8–22мс.
- [Настройки ресурсов по группе/периоду](../components/retailcase_ni081_scoped_configuration_20261014.md): SQL8–34мс, report57; [тара C0015](../components/retailcase_b05_tare_workspace_20261014.md) сдана, [Claude C0018](../../coordination/retailcase-claude/TASK_C0018.md) — страницы СТ.
- [Документы сверки NI07.2](../components/retailcase_ni072_documents_20261014.md): два SQL-пакета вместо32 обращений, до20 ID/показатель, 38–62мс, report56.
- [Переходы оператора: нагрузка и CASE](../components/retailcase_operator_next_steps_20261014.md): reports54–55, screenshots98–100; Claude далее C-0015.
- [План66](../requirements/retailcase_delivery_v55/implementation_plan.md): результаты52–53 и реальный финансовый цикл K-0015 учтены отдельно от внешней приёмки.
- [СТ: ранняя страница и индекс1381](../database/retailcase_ni022_st_page_keys_20261014.md): VALID,22.182с→5.691с/200равныхстрок; report53, широкая история2с ещё не достигнута.
- [NI04.2 архив весов](../components/retailcase_ni042_scale_archive_20261014.md): точный поиск, однократность, сохранение сканов; report52.
- [Claude C-0010](../../coordination/retailcase-claude/TASK_C0010.md): финансовый цикл и сверка, ACK K-0014; ранее C-0008 сдан.
- [NI04.1: дерево и скан1370](../components/retailcase_ni041_hu_tree_20261014.md): визуальная вложенность/история/отдельный физический скан, report51.
- [NI06.2: путь возврата1363](../components/retailcase_ni062_return_route_20261014.md): единое досье SAP/вывоз/приёмка/размещение/поставщик/утилизация, report50, read-only.
- [Claude C-0008: финансовый процесс](../../coordination/retailcase-claude/TASK_C0008.md): прямое основание суммы → реестр допрасходов/согласование/распределение; ACK ожидается.
- [B05: двухсторонняя тара1353](../components/retailcase_b05_tare_workspace_20261014.md): существующий мобильный UI/история/баланс, dev6→6→4→4, итог4+2+0, report49.
- [B04: маршрут между складами1346](../components/retailcase_b04_interwarehouse_workspace_20261014.md): карточки/этапы/существующие формы/составные места, report48, screenshots88–89.
- [NI08.1 часы по нормам1341](../components/retailcase_ni081_forecast_labour_20261014.md): explicit mapping2/Decimal/currentnorm/full-vs-partial/UI/actual lost-response replay, report47.
- [NI08.1 нормативы прогноза1328](../database/retailcase_ni081_forecast_norm_scope_20261014.md): prepared versioned scope→site, existing native config and norms, no guessed labour capacity.
- [B03: водитель→магазин1326](../components/retailcase_b03_driver_delivery_20261014.md):order2135/36EAприняты/replay/P0H0, мобильный UI, миграции1302/1316VALID; report46.
- [Driver workspace1302](../database/retailcase_ni053_driver_workspace_20261014.md): подготовлен текущий account binding и повтор временных отметок через прежний пакет.
- [B02: маркированный отбор1300](../components/retailcase_b02_terminal_profiles_20261014.md):CASE1134/5EA/10кодов/потеря ответа→replay/WAIT_CONTROL, отчёт45; NET ручной факт блокируется.
- [B01 завершённый dev-проход1291](../components/retailcase_b01_departure_20261014.md):36EA/2места/33571DEPARTED/559DONE/отчёт44; план59, далееB02. Это актуализирует промежуточные записи1266–1275 ниже.
- [Укладка СТ1275](../database/retailcase_ni022_prepared_row_move_20261014.md): actual row move18+18/6boxes/24kg, oldST IDs/trip/replay; FULLPAL scope reuse подготовлен.
- [Согласование укладки1266](../database/retailcase_ni022_prepared_row_move_20261014.md): подготовлена обёртка существующего переноса строки СТ; точные суммы/Root/replay, без движения запаса.
- [B01: физическое исполнение1261](../components/retailcase_b01_receiving_staging_20261014.md):36EA приняты/размещены,559 запущена,1165/1166 DONE; отчёт43, укладка СТ — следующий разрыв.
- [Claude: NI07.2 обзор](../components/retailcase_ni072_day_overview_20261014.md) и [NI08.1 прогноз](../components/retailcase_ni081_forecast_screen_20261014.md) переданы; [следующее поручение C-0004: NI07.1](../../coordination/retailcase-claude/CODEX_TO_CLAUDE.md), ACK ожидается.
- [Точный артикул в плане1248](../database/retailcase_ni033_pick_article_identity_20261014.md): подготовлена коррекция UPPER в существующем планировщике; волна558 остановлена до проведения.
- [Действующее поручение Claude: NI07.2 + NI08.1](../../coordination/retailcase-claude/TASK.md): две независимые UI-части, закреплённые файлы; [канал обмена](../../coordination/retailcase-claude/README.md), сообщение C-0001, ACK ожидается.
- [Повтор создания плана1236](../database/retailcase_ni033_pick_create_idempotency_20261014.md): потерянный ответ→тот же план2189, общий admission/OP lock, один receipt, отчёт42/скриншот64; B01 открыт.
- [Параллельные задания Claude Code](../requirements/retailcase_claude_parallel_tasks_20261014.md): остаток 16 спринтов; 6 заданий в 5 потоках, владельцы файлов, критерии и передача результатов.
- [B01: заказ→рейс→обеспечение1232](../components/retailcase_order_trip_warehouse_workspace_20261014.md): actualSAP_2135→33571/2places/replay/P0H0; current loading link, pickplan2187 NO_STOCK36/0/36/no issued tasks/report41.
- [Требования к WMS/TMS как источнику двойника](../requirements/twin_source_system_requirements.md): опубликованная топология с полным покрытием RRL_CELLS через LEGACY_CELL_CODE, позиции по сканам, журнал фактов заданий, лента изменений, остатки по ячейкам, факты двора.
- [3D-двойник: live-операции склада](../subprojects/wms_twin_3d.md): задания техники и CASE-сборка по спецификации складских заданий, правило WMS выбора топологии, состояние связи.
- [Единое описание складских операций для цифрового двойника](../requirements/warehouse_operations_digital_twin.md): ричтрак, сборка, CASE/HU, контроль, приёмка, экспедиция, инвентаризация/возвраты/оборудование; реальные сущности/API, контракт адаптера и правила LIVE/SIM.
- [Тип паллеты при сборке1219](../database/retailcase_ni022_case_type_20261014.md): shared recipient policy/empty CASE Root override/actual1133/CLI+HTTP replay/UI58–59/report40; full repack remains separate.
- [План RETAILCASE58](../requirements/retailcase_delivery_v55/implementation_plan.md):18 спринтов/7 сквозных блоков, готовность кода и внешней приёмки отдельно; текущий B01/NI02.2; история57 сохранена.
- [Тип плановой паллеты от адресата1209](../database/retailcase_ni022_recipient_floor_20261014.md): installed shared TMS check/default store→customer→actual CASE; rollback2trolley→2EU→unknown/report39.
- [Правила исполнения RETAILCASE](../concepts/retailcase_execution_delivery_rules.md): сквозные сценарии,80/20,раздельная готовность; тип паллеты из настроек адресата, переопределение при сборке.
- [Prepared1202: целая STOCK-паллета](../database/retailcase_ni022_stock_floor_type_20261014.md): zero-quantity Root type command/one metadata table/version/scan/same journal+outbox; no second stockwriter.
- [Delivered1200: физический TOP/type](../database/retailcase_ni052_loading_floor_20261014.md): actual33637/typeEU/load+depart/rollback/replay/UI53–54/report37; plan57, fullSTOCKtype/deadline next.
- [Physical1195–1197](../database/retailcase_ni052_loading_floor_20261014.md): actual33637 one typed TOP/rollback/replay/depart; shared planned loaded TOP merge prepared.
- [Prepared1192: физический TOP/type](../database/retailcase_ni052_loading_floor_20261014.md): same Root immutable proof/vehicle-lock normative check/departure; no child multiplication, not yet applied.
- [Delivered1190: норматив тары](../database/retailcase_ni022_vehicle_tare_20261014.md): currentfleet/UI/nativefinalcheck/6cases/unknownrefusal/report36/screens49–50; plan56, TOP next.
- [Общий норматив тары1186](../database/retailcase_ni022_vehicle_tare_20261014.md): prepared shared native final planning check/preview; unknown top type refuses new configured profiles.
- [Промпт Codex: данные для live-двойника](../requirements/twin_live_data_fixes_codex_prompt.md): связь RRL_TT_DOCK↔ворота топологии, склад рейса, read-only состояние двора, порча zone_name, серверная пагинация available-sts, карта без distances, доработка двойника.
- [Нормативные варианты тары1180](../database/retailcase_ni022_vehicle_tare_20261014.md): существующий versioned vehicle profile/catalog, подготовлены API и native validation; не новый allocator.
- [3D-двойник: live-сопоставление ТМС](../subprojects/wms_twin_3d.md): рейсы/ворота/СТ/топология сверены с живым API, read-only адаптер, находки по данным (DOCK, CONDITION, WARE_ID) и решение по долгому available-sts.
- [Последний результат1178](../database/retailcase_ni052_departure_temperature_20261014.md): actual33636/load3.125/depart3.75/rollback/replay/qty0, report35/screens47–48, boundedSQL13.857ms.
- [Departure1172 /SQL1173](../database/retailcase_ni052_departure_temperature_20261014.md): actual one-clock3.75/manual confirm/replay/rollback/DEPARTqty0; slow675ms rewrite prepared.
- [Prepared1170–1171: температура выезда](../database/retailcase_ni052_departure_temperature_20261014.md): separate current confirmation, original root journal/one departure clock/no repeat stock; apply pending.
- [Installed loading thermal1165–1167](../database/retailcase_ni052_loading_temperature_design_20261014.md):6/0, currentnativeVALID/errors[], same-root guard/scoped read; positive physical case and departure next.
- [Prepared1162–1163: температура общей погрузки](../database/retailcase_ni052_loading_temperature_design_20261014.md): native pre-effect recheck/atomic immutable fact/scoped read/typed API/UI; apply pending.
- [Physical loading thermal design1160](../database/retailcase_ni052_loading_temperature_design_20261014.md): saved LIVE sharedload/depart source, same-root manual confirmation and pre-effect recheck; not applied.
- [Delivered1158: профиль машины/автоукладка](../database/retailcase_ni022_vehicle_temperature_20261014.md): original native owner, exact feasibility, current API/UI, screenshots45/46/report34; next physical thermal admission.
- [NI02.2 температурный профиль1150–1151](../database/retailcase_ni022_vehicle_temperature_20261014.md): existing versioned fleet profile/API/UI, exact capability intersection; prepared, no physical admission.
- [3D-двойник склада и транспорта](../subprojects/wms_twin_3d.md): новое Vite-приложение twin/wms_twin_3d (R3F, единый TwinState, tick 10 Гц, мок-симуляция WMS/TMS, каркас live-адаптера ТМС).
- [Принципы цифрового двойника склада + транспорта](../concepts/warehouse_transport_digital_twin_principles.md): 14 принципов — проекция без записи, событийная модель EPCIS, сквозные ID, ворота как стык склада и рейса.
- [Auto layout V2 /1148](../components/retailcase_ni021_auto_preparation_20261013.md): temperature-compatible places/current ranges UI; old V1 saved receipts unchanged.
- [Auto layout temperature compatibility1147](../components/retailcase_ni021_auto_preparation_20261013.md): prepared currentSKU ranges/source signature, incompatible/unknown separation; no vehicle temperature guess.
- [NI02.2 current temperature view delivered1145](../components/retailcase_ni022_source_layout_20261011.md): existingSKU rules/exact ranges/unknown vehicle/API1144/report33; SQL rewritten21.437ms26buffers/noDDL.
- [NI02.2 thermal requirements1140](../components/retailcase_ni022_source_layout_20261011.md): prepared existing SKU ranges/current scope/legacy vehicle label; no invented temperature admission.
- [RETAILCASE — единая входная страница](../subprojects/retailcase.md): полноеТЗ57, картаисходников, архитектура, текущий план55 и изменения1113–1158/report30–34.
- [Auto→existing trip assignment1131](../components/retailcase_ni021_auto_preparation_20261013.md): current receipt link and explicit original TMS capacity review prepared; no second writer.
- [QC physical label delivered1130](../components/retailcase_ni051_control_label_20261012.md): actual CASE barcode/CASEID/current20/canonical freeze/report31/screen42/no stock effect.
- [QC physical CASE alias1126](../components/retailcase_ni051_control_label_20261012.md): prepared readonly canonical source resolver/current rights/ambiguous refusal; native command unchanged.
- [NI02.1 dev delivered1125](../components/retailcase_ni021_auto_preparation_20261013.md): actual2135/mixed2places/exact36EA/race/rollback/replay/report30/screen41; plan52, allfullsprints remain open.
- [NI02.1 implementation1117](../components/retailcase_ni021_auto_preparation_20261013.md): расчёт/API/UI, actual mm→m³, locks/shared writer; live acceptance pending.
- [NI02.1: новый автоматический расчёт](../components/retailcase_ni021_auto_preparation_20261013.md): разрешение владельца, единый legacy writer, явные пределы и точная whole-box укладка.
- [Ownerdecision1108: NI02.1 auto](../components/retailcase_ni021_preparation_readiness_20261011.md): свежего SQLнет, самостоятельная безопасная реализация разрешена; existing writer/current constraints, plan51.
- [Checkpoint1106: восстановление QC](../components/retailcase_ni051_control_label_20261012.md): shared intent/currentGET/archive/last50 scans/report29/screen38/plan50; allspints open.
- [QC scan draft1104](../components/retailcase_ni051_control_label_20261012.md): bounded separate renderer/profile-aware evidence and per-scan correction before confirmation.
- [QC recovery1100](../components/retailcase_ni051_control_label_20261012.md): shared command storage + separate contractvalidator/read-only recovery; runtime pending.
- [Checkpoint1098: волна и контроль](../components/retailcase_ni033_wave_workspace_20261013.md): currentCASE20/13/QCactions/read-onlylinkedARM/report28/screens34+37/plan49; fullsprints open.
- [QC navigation1095](../components/retailcase_ni051_control_label_20261012.md): explicit linked panel opens existing folded tools after auth; screenshot35 is queue, not QC proof.
- [QC workspace1094](../components/retailcase_ni051_control_label_20261012.md): linked readonly status, separate scan/weight stages and exact response/pending scope guards.
- [Wave next actions1092](../components/retailcase_ni033_wave_workspace_20261013.md): current CASE carrier/cell/version and existing QC/composition links; currentwave553 pendingcontrol, no status bypass.
- [Checkpoint1089: несколько мест СТ](../database/retailcase_ni072_place_selection_20261013.md): migrations012/013VALID, HU+CASE/twoTOP/P20H20/guardedsharedWAIT/report27/screen33/plan48.
- [Execute shared target1087](../database/retailcase_ni072_shared_wait_target_20261013.md): fresh registered WAIT task proof under Root locks, retained A_DONE/B pending.
- [Planning boundary1085](../database/retailcase_ni072_shared_wait_target_20261013.md): native private planning flag or registered physical WAIT task, no generic metadata bypass.
- [Shared waiting target1082](../database/retailcase_ni072_shared_wait_target_20261013.md): guarded shared zone for current defer HU; retained1154/1155 before resume.
- [CASE cohort1077](../database/retailcase_ni072_place_selection_20261013.md): prepared currentmembership/cargo proof for bothHU/CASE, compatibleoldmanifestlessplans, no openWAITbaseline.
- [Place selection1076](../database/retailcase_ni072_place_selection_20261013.md): prepared sameST multiTOP/HU+CASE/atomicperplace/currentmanifest; capture1075/livepending.
- [Checkpoint1074: глубокое HU](../database/retailcase_ni072_nested_hu_wait_20261013.md):1152DONE1TOP/twolevels/P20H20, ROWbusy20840.191sec, alreadywaitingno writes/report26/screen32/plan47.
- [Operation scope1071](../database/retailcase_ni072_nested_hu_wait_20261013.md): under-fence metadata/RootID collision guard prepared, currentnestedruntime preserved.
- [Already waiting1070](../database/retailcase_ni072_nested_hu_wait_20261013.md): prepared no newHUtask/stock if alreadyatWAIT, deep1069 actualdone.
- [Checkpoint1068: целое HU в ожидание](../database/retailcase_ni072_nested_hu_wait_20261013.md): migration010/011VALID, actual1149DONE1HU/twoCASE20/P20H20/replay/queue/report25/screen31, plan46.
- [Replay1063](../database/retailcase_ni072_nested_hu_wait_20261013.md): original1149/1HU alreadyPLANNED; replay now finalRootoutboxcache, correction prepared/no duplicate.
- [Lock-scope1061](../database/retailcase_ni072_nested_hu_wait_20261013.md): exact ST scalar/NOWAIT20840 and ancestor scalar correction prepared after timeout/no commit.
- [Wire1060](../database/retailcase_ni072_nested_hu_wait_20261013.md): helperVALID, packedretainedsource, Rootcontractversion correction012 before trialretry.
- [Clock1059](../database/retailcase_ni041_repack_clock_20261013.md): actual slottedrepack refused by oldclock enum, prepared minimal correction, P20H20 retained.
- [Correction1056](../database/retailcase_ni072_nested_hu_wait_20261013.md): newhelper compile separator fixed in011, runtime pending.
- [Вложенный HU в ожидание1055](../database/retailcase_ni072_nested_hu_wait_20261013.md): PREPARED original HU_PLAN_MOVE/whole frozen source/no metadata bypass; live pending.
- [Пагинация1050](../components/retailcase_order_execution_workspace_20261013.md): scoped headerbound/keyset/negativelegacy/24report/30screen, NI03.3 in_progress.
- [Продолжение1044: заказы по текущему складу](../components/retailcase_order_execution_workspace_20261013.md): scoped list/detail/exactquantity, report23/screen29, plan45; продолжать до завершения.
- [Checkpoint1039: выбранная позиция приёмки](../components/retailcase_receiving_history_20261013.md):alias+line/currentprofiles/closedsource/labeldisabled/report22/screens27–28.
- [Checkpoint1033: исполнение заказа и текущий CASE](../components/retailcase_order_execution_workspace_20261013.md):current CASE10FF10/старый3+1/состояния/UOM/scopedfacts/report21/screens24–26.
- [Checkpoint1014: CASE slot и карточка места](../components/retailcase_hu_workspace_20261013.md):1001VALID/CTFF10/P20H20/claim224/read/recovery;report20/screens22–23.
- [CASE slot binding1001](../database/retailcase_ni041_case_slot_binding_20261013.md): prepared reuse binder/current actual-row order, live pending.
- [Checkpoint999: HU и исполнение CASE](../database/retailcase_ni041_hu_case_binding_20261013.md):993VALID/1138DONE1HU/20EA/996detach8+12/H20; новый UI/report19/screenshots19–21.
- [NI04.1 HU CASE binding993](../database/retailcase_ni041_hu_case_binding_20261013.md): prepared originalmatryoshka/one activeFFversion owner/frozen tree bindings, live pending.
- [Checkpoint991: два CASE однойСТ](../database/retailcase_ni072_multi_case_wait_20261013.md):986VALID/987 actual12+8, WHT1136/1137DONE1 each/P20H20/siblingsource preserved, report18.
- [NI07.2 multiCASE986](../database/retailcase_ni072_multi_case_wait_20261013.md): prepared per-place frozen source/one ST/allCASE/bounded200lots, live pending.
- [Checkpoint984: связанный CASE](../database/retailcase_ni033_case_bound_move_20261013.md):974/981VALID, current CASE12 ожидание→контроль→ожидание/CT4FF4/task1132/journal12EA; report17.
- [CASE повторное ожидание981](../database/retailcase_ni072_case_wait_identity_20261013.md): prepared original-index-compatible self-task identity/explicit CASE plan, retained history.
- [NI03.3 CASE binding974](../database/retailcase_ni033_case_bound_move_20261013.md): prepared sameTX original FF version on generic CASE movement; capturedcurrent973, live pending.
- [Checkpoint972: CASE в ожидании](../database/retailcase_ni072_case_wait_20261013.md):1110/1111 DONE1CASE/P12H12+P8H8, actual967/HTTP971, report16/screenshot18; полныйNI07.2 открыт.
- [CASE ожидание965](../database/retailcase_ni072_case_wait_20261013.md): actual1110DONE1CASE/P12H12/rollback/replay; add WHT lot journal, final harness outbox corrected.
- [CASE ожидание963](../database/retailcase_ni072_case_wait_20261013.md): immutable plan registered; sync lookup shadowing correction before movement.
- [CASE ожидание961](../database/retailcase_ni072_case_wait_20261013.md):953 compiledVALID, retained source picked/deferred; runtime scalar correction, movement pending.
- [NI07.2 CASE ожидание953](../database/retailcase_ni072_case_wait_20261013.md): prepared additive CASE_TASK_ID/existing CASE_CARRIER_MOVE + WHT same TX, live pending.
- [Checkpoint950: история приёмки](../components/retailcase_receiving_history_20261013.md):935–947 current scope/keyset/history/damaged intent; report15/screenshots16–17, ручной выбор не подтверждён.
- [Checkpoint934: исполнение заказа](../database/retailcase_ni033_order_execution_20261013.md):925 VALID/current snapshot, original3/0 и3/1/HTTP926, receipt930–933 recovery; report14/plan37, browser unavailable.
- [NI03.3 execution925](../database/retailcase_ni033_order_execution_20261013.md): prepared current native order/warehouse/single readonly snapshot; quantity writer unchanged.
- [Checkpoint916: SAP receiving](../database/retailcase_ni011_supply_lines_20261013.md):905 VALID/908+911 perline+amend+reversal, report13/screenshots14–15, plan36/manual UI pending.
- [NI01.1 строки SAP905](../database/retailcase_ni011_supply_lines_20261013.md): explicit v2/shared canonical legacy SKU row; prepared, live pending.
- [Checkpoint893: очередь волны](../components/retailcase_ni033_wave_queue_20261013.md): lean header/current actor snapshot, actual889/browser888/JS891, report12/architecture reduced.
- [Checkpoint885: допуск отбора](../database/retailcase_ni033_pick_scope_20261013.md):877 VALID; scoped read/native/replay actual879/881, UI shared intents/три панели/browser403; report11/gatePASS.
- [NI03.3 pick-scope877](../database/retailcase_ni033_pick_scope_20261013.md): prepared reuse current WAVE access/readonly preview; actual pending.
- [Checkpoint875: same-source доставка](../database/retailcase_ni032_same_source_bindings_20261013.md):866/869/872 VALID, actual1099 DONE20/no next/owner12+8; related20+12 PASS, report10.
- [NI03.2 binding closure872](../database/retailcase_ni032_same_source_bindings_20261013.md): prepared exact expected coverage/all own incoming;869VALID, old execution rightly rolled back.
- [NI03.2 shared-binding869](../database/retailcase_ni032_same_source_bindings_20261013.md): prepared aggregate admission;866 VALID, failed867 before physical issuance/owncleanup.
- [NI03.2 same-source866](../database/retailcase_ni032_same_source_bindings_20261013.md): prepared existing full binding closure/one physical source; live proof pending.
- [Checkpoint864: исполнение волны](../components/retailcase_ni033_wave_workspace_20261013.md): existing native/API, scoped pending/recovery, выбор волны и реальные links; read/browser403, report09.
- [Checkpoint856: частичная общая подача](../database/retailcase_ni032_shared_capacity_20261013.md): native852 VALID; actual1096/1097 DONE20/12, резервы12/8/14, replay/owncleanup; отчёт08.
- [NI03.2 shared capacity852](../database/retailcase_ni032_shared_capacity_20261013.md): prepared one physical incoming perFULL cohort; partial shared849 requeue/native actual pending.
- [Checkpoint848: общая паллета и две подачи](../components/retailcase_ni032_shared_arrival_20261013.md): actual840/845 DONE20+8/owner12+8+10, owncleanup, report07/browser1087; sum200-bound847.
- [Checkpoint839: последовательные источники](../database/retailcase_ni032_sequential_sources_20261013.md): applied834/836, actual835/837 PASS/owncleanup, currentNI03.2; report06/Qwen, до20:00MSK.
- [NI03.2 sequential sources834](../database/retailcase_ni032_sequential_sources_20261013.md): prepared reuse original continuation; live apply и свежий случай ожидают.
- [Checkpoint831: очередь ожидания по ссылке](../components/retailcase_warehouse_task_ui_20261013.md): browser1/task1080 DONE3EA, report05/screenshot08, gatePASS; до20:00 MSK.
- [Продолжение827–829: актуальная карточка заданий](../components/retailcase_warehouse_task_ui_20261013.md): fresh status/progress guard, JS828 PASS, scan layout; дедлайн20:00 MSK.
- [Checkpoint826: рабочая очередь и точные количества](../components/retailcase_warehouse_task_ui_20261013.md): gate825 PASS, HTTP86/qtystrings, formatter9digits; report04, browser preset не сертифицирован.
- [Рабочий UI заданий и точные количества](../components/retailcase_warehouse_task_ui_20261013.md): server shipping filter86, native exact strings, direct task1080/browser, recovery824; report04 и открытые ветви.
- [Checkpoint808: карточка ожидания и выбор рейса](../components/retailcase_st_trip_picker_20261013.md): browser807 DONE3EA, HTTP806/sourceoutbox4670, report03; preset click остаётся открытым.
- [NI07.2 форма переноса и recovery800](../components/retailcase_st_trip_picker_20261013.md): original TMS picker + protected pending + archive/current read, report02 и Qwen.
- [Выбор рейса при переносе СТ](../components/retailcase_st_trip_picker_20261013.md): существующие рейсы, даты/район/код магазина, реальный браузер и отчёт.
- [NI07.2 checkpoint788: штатное ожидание и рабочий UI](../database/retailcase_ni072_waiting_tasks_20261013.md): actual task1080 DONE/SYNCED P3/H3/3units6codes, HTTP785 и реальные screenshots; новый shared-mode case/полный спринт открыты.
- [NI07.2 waiting tasks772: контракт перед применением](../database/retailcase_ni072_waiting_tasks_20261013.md): typed existing TASK_COMPLETE/TRANSFER_CORE, immutable origin, no second stock writer; actual evidence pending.
- [NI07.2 checkpoint764: ячейка ожидания](../database/retailcase_ni072_waiting_cell_20261012.md): native настройка/API/форма, same-warehouse guard, case762 P3/H3, HTTP769 optional сохранён, SQL768 решение; typed перенос ещё открыт.
- [NI07.2 checkpoint759: граница задания ожидания](../database/retailcase_ni072_prepared_deferral_20261012.md): current748 replay PASS, generic MANUAL rightly refused; next typed source handler, P3H3 preserved.
- [NI07.2 checkpoint747: перенос после отбора](../database/retailcase_ni072_prepared_deferral_20261012.md): native743/746 VALID, actual745 flat prepared ST/P3H3/rollback/replay; physical waiting move/CASE/HU remain.
- [NI07.2 checkpoint740: восстановление подписи](../database/retailcase_ni072_shipping_inspection_20261012.md): архив damaged intent + current authorised review reread до новой команды; JS syntax PASS.
- [NI05.3 checkpoint736: страницы мест магазина](../components/retailcase_ni053_store_pages_20261012.md): existing bounded keyset/current receiver/foreign cursor422/form next100; native page732 и TS PASS.
- [NI05.3 checkpoint728: восстановление приёмки](../components/retailcase_ni053_receipt_recovery_20261012.md): damaged intent blocked/archive+server reread/current scope/unchanged body; parser и TS PASS.
- [Checkpoint724: магазин UNIT/BOX/PALLET](../database/retailcase_ni053_store_aggregation_20261012.md): shared resolver, actual717 accepted3+3/original6keys9codes; UI718, scope722, независимые отрицательные ветки открыты.
- [NI06.1 checkpoint715: продолжение смешанной группы](../database/retailcase_ni061_group_continuation_20261012.md): existing HU task/custody/ST/QC/whole load P0; store aggregation остаётся открыта.
- [NI07.2 checkpoint700: независимый осмотр](../database/retailcase_ni072_shipping_inspection_20261012.md): native VALID, реальная пара подписей/replay/conflicts; форма подключена, день не закрывается.
- [NI07.2 checkpoint694: подписи осмотра](../database/retailcase_ni072_shipping_inspection_20261012.md): prepared независимые chief/dispatcher заявления к frozen review, current source/role, no quantity/day closure; native apply/UI ещё ожидают.
- [NI01.1 checkpoint690: SAP-приёмка внутренней паллеты](../database/retailcase_ni011_internal_receipt_identifier_20261012.md): native686 VALID, actual688 UID47/P3H0/3units6codes/PUT DONE/SSCC NULL; old689 replay unchanged.
- [NI05.1 checkpoint682: этикетка допуска и красный тег](../components/retailcase_ni051_control_label_20261012.md): прежний native QC, текущая подпись/actor, stale409/no-store; raw UI и Qwen682, физическая печать открыта.
- [NI01.1 checkpoint678: склад этикетки](../components/retailcase_ni011_receipt_label_access_20261012.md): native scope для issue/HTML/ZPL/confirm/USED; actor contract; label fixture отсутствует.
- [NI06.1 checkpoint676: группа UNIT + BOX + PALLET](../database/retailcase_ni061_group_aggregation_20261012.md): native667/674 VALID, actual673 P3H0 each / old6units9codes / rollback / HTTP675; plan28.
- [NI06.1 checkpoint667: агрегационная приёмка группы](../database/retailcase_ni061_group_aggregation_20261012.md): reuse общего native validator; итоговый положительный кейс673 указан на странице.
- [NI06.1 checkpoint664: продолжение межскладского списка](../components/retailcase_ni061_group_queue_20261012.md): прежний API/экран, текущие WARE/actor, bounded keyset; многорядная приёмка открыта.
- [NI06.2 checkpoint660: восстановление передачи возврата](../components/retailcase_ni062_custody_recovery_20261012.md): повреждённый intent блокирует отправку, архив + серверное перечитывание, защита смены контекста/другой вкладки.
- [Checkpoint629: возврат по агрегации коробки](../database/retailcase_ni062_return_aggregation_20261012.md): complete mixed-profile dev cycle, existing UI, PALLET identity limitation explicit.
- [NI06.2: агрегаты возврата](../database/retailcase_ni062_return_aggregation_20261012.md): prepared619, existing resolver + exact approved code matrix, aggregate-only no unit fallback, lifecycle fences retained.
- [Checkpoint616: существующий складской инвариант](../database/retailcase_ni052_loading_20261010.md): current load core ST/LOAD WARE=dock WARE, same dock on departure; no invented multiWARE-TT subsystem, plan26.
- [Checkpoint611: коррекция нормативов без второго согласования](../database/retailcase_ni071_normative_correction_20261012.md): signed delta through existing LOGIST/FINANCE, concurrent one credit, original107.25/current0, existing allocation, exact source search; still residuals.
- [NI07.1: нормативная коррекция](../database/retailcase_ni071_normative_correction_20261012.md): prepared598–599, existing signed expense and independent approvals reused; original cost never recognised twice.
- [Checkpoint595: деньги и источники счёта](../database/retailcase_ni071_transport_recognition_20261012.md): recognition582/rounding594 applied VALID, original invoice load sources592, bundle595 maintained; monetary correction/multiWARE remain.
- [NI07.1: округление статьи](../database/retailcase_ni071_transport_rounding_20261012.md): prepared594, existing quantity×rate then HALF_UP2, retained107.25 unchanged, source/constraint checkpoint.
- [Checkpoint591: нормативные расходы проведены](../database/retailcase_ni071_transport_recognition_20261012.md): actual race one107.25, same-TX outbox, exact HTTP replay, existing billing/day board; planrevision24, remaining deltas open.
- [NI07.1: денежное проведение Q26](../database/retailcase_ni071_transport_recognition_20261012.md): prepared582, shared native preview/conduct, original cost-run header + once-only departure claim + same-TX outbox.
- [Checkpoint581: формула Q26 переиспользована](../database/retailcase_ni071_transport_cost_preview_20261012.md): vehicle+points+unload, difficult rolling+loader; legacy hours do not create new costs.
- [Checkpoint580: транспорт по фактам](../database/retailcase_ni071_transport_cost_preview_20261012.md): archived departure/unload, explicit norm basis, exact107.25 rollback-only preview; paid hours/money recognition remain open.
- [NI07.1: единица выгрузки](../database/retailcase_ni071_unload_norm_basis_20261012.md): явные POINT/PLACE и ставка паллеты; migration572 checkpoint, старые точные повторы сохранены.
- [Checkpoint564: версии класса автопарка](../database/retailcase_ni071_vehicle_source_20261012.md): actor/fleet permission/current base hash, one concurrent v1, immutable v2, rollback v3; source-on-departure installed, actual case next.
- [NI07.1: класс автомобиля фиксируется на выезде](../database/retailcase_ni071_vehicle_source_20261012.md):native559/561/564 applied, version/base-hash protected profiles and existing fleet UI; actual departure source case pending.
- [Checkpoint558: действующая панель передачи тары расширена](../database/retailcase_ni063_damage_custody_20261012.md): выбор исходника/текущие подписи/точное восстановление; source557/TS PASS, отдельный портал не создаётся.
- [Checkpoint555: повреждённая тара вернулась и списана](../database/retailcase_ni063_damage_custody_20261012.md): исходник DAMAGE сохраняется в подтверждённых передачах; один winner списания, поздний rollback атомарен; goods unchanged.
- [NI06.3: происхождение повреждённой тары](../database/retailcase_ni063_damage_custody_20261012.md):552 применена,553/554 адресный цикл/конкуренция/откат; связь DAMAGE → OFFER/ACCEPT → складское списание в прежнем ядре.
- [Checkpoint551: действующий справочник тарифов](../database/retailcase_ni071_transport_tariff_sources_20261012.md): vehicle/hour/point, точные строки, исправлен старый GET; architecture657 PASS,550 TS/UTF8/native VALID.
- [Checkpoint550: формы транспортных норм и восстановление выгрузки](../database/retailcase_ni071_transport_norms_20261012.md): существующий native API, точный повтор операции, история30; malformed unload recovery сохраняет исходник и сверяется с сервером.
- [Checkpoint549 unloading/norms](../database/retailcase_ni053_unloading_facts_20261012.md): native539/544/API542, actual customer3/start-finish/manual, source-clock day1/1/open0; versioned tariffs529/534 and published history/UI. Planrev19.
- [Публикация транспортных норм](../database/retailcase_ni071_transport_norms_20261012.md): native529/534 applied, versioned source snapshot/period/currency/size/unload;550 publication/history UI.
- [Транспортный тариф: правильный источник](../database/retailcase_ni071_transport_tariff_sources_20261012.md): valuation stoim_tt differs from carrier tariff; existing PRICE catalog/readonly source candidates, no arbitrary fee.
- [NI07.1 checkpoint522](../database/retailcase_ni071_cost_periods_20261012.md): actual CASE2.75/ordinaryBOX2.25, one source claim, shared native dates, historical5 lines13.50 preserved; planrevision18.
- [Checkpoint511 и продолжение](../runbooks/retailcase_active_work.md):actual BOX start/mixed-date single-load finance next; exact existing fixture replay rules/current API509.
- [Актуальный план RETAILCASE, revision17](../requirements/retailcase_delivery_v55/implementation_plan.md):12Oct18increments/1addressed-implemented+17remaining; group delivery, aggregation cancellation, exception returns, period revision+invoice summary.
- [Редакции периода и сводка затрат](../database/retailcase_ni071_revision_summary_20261012.md):495–505 same-month revisions/deterministic date+version/native stale refusal/actualBOX1 charge3 frozenv2/scoped exact invoice/trip groups.
- [Возврат отказа и повреждений](../database/retailcase_ni062_exception_returns_20261012.md):472–492 existing return owners/three caps/SAPv2/real custody/quarantine/tasks/supplier departure+disposal; buyer3/missing2 preserved.
- [Локальная отмена агрегации](../database/retailcase_ni043_aggregation_lifecycle_20261012.md):450–465 точный original BOX+ancestor invalidation/native scan guard/metadata journal/no P effect/concurrent HTTP/replay/SAP fresh3.
- [Полная доставка многотоварного места](../database/retailcase_ni061_group_delivery_20261012.md):428–444 twoSKU3each/originalST→groupreceipt/1HUtask/custody/onward/LOAD/DEPART/STOREbothbuyer3; sourceFFonce/6oldkeys9codes/HTTP replay.
- [Размещение многотоварного места](../database/retailcase_ni061_group_placement_20261012.md):417–425 originaltask1HU/2commoditymoves3EA/old6keys9codes/nativeproof/rollback-replay/typedAPI/rawUI; custody/onward next.
- [Приёмка многотоварного места](../database/retailcase_ni061_group_receipt_20261012.md):403–412 exacttwoST/twoSKU3each/6oldunits9codes/one rootreceipt/restoredTOP/rollback-replay; placement next.
- [Два физических цикла недостачи](../database/retailcase_ni061_recurrent_physical_20261012.md):390–399 samekey/loss-found→buyer→REUSE→newshipment→loss-found→buyer2; original6codes/no rebirth.
- [Маркированный REUSE и частичное CASE](../database/retailcase_ni062_marked_reuse_20261012.md):385–388 BOX3/original3keys6codes→return→P3H0/eligible;383CASE7 accepted3/missing2/refused1/damaged1/noP.
- [Приёмка маркированного CASE покупателем](../database/retailcase_ni053_marked_case_20261012.md):379–380 exact archivedCASE/7EA14codes/.225weightboundary/3photos/nonadmin/actualaccepted7/oneoutbox/no stock;377actualassembly-date cost3.00.
- [Консолидация найденного товара](../database/retailcase_ni061_recovery_consolidation_20261012.md):367–374 original1+found1+1/3ST/oneTOP/6oldcodes/actualSTOREbuyer3/FF3once/rollback-replay.
- [Настройка расчётного периода и точные источники](../database/retailcase_ni071_assembly_period_20261012.md):362–365 explicitWAREpolicy/CASEclock/no naive date/currentversion/concurrentwinner/nativeforgeddate refusal; originalBOXcost reused.
- [Точный момент начала CASE](../database/retailcase_ni033_case_start_instant_20261012.md):361 same start/event/TSTZ/immutable/rollback; legacy shift zone unknown.
- [Месячная ставка и измеренная CASE в биллинге](../database/retailcase_ni071_monthly_case_20261012.md):353–359 shared.5 inside existing2.5BOX norm/history; actualsmallCASE cost1×2.5 and independent expense2.01 on7EA/.35KG.
- [Смешанная консолидация и интерфейс матриц](../database/retailcase_ni061_mixed_consolidation_20261012.md):345–351 marked3/6codes+ordinary3 inoneTOP→STOREeach3; perSKU/profile UI/adminTS/archPASS.
- [Маркированная консолидация по карточкам SKU](../database/retailcase_ni061_marked_consolidation_20261012.md):333–344 twoST/oneTOP/6units, matrices2+1/9codes, perlotSTORE3each/staleversions denied.
- [Консолидация обычных межскладских СТ](../database/retailcase_ni061_ordinary_consolidation_20261012.md):327–332 twoST×3EA/oneTOP/twoimmutable dispatch/actualSTORE bothorders3; marked multi-leaf next.
- [Перепланирование принятого целого HU](../database/retailcase_ni061_nested_replan_20261012.md):321–323 SAP omitted quantities retain born unit amounts; atomic cancel-replan 1HU without movement.
- [Полная доставка вложенного места](../database/retailcase_ni061_nested_completion_20261012.md):317–320 existing wholeHU task1/3EA, top custody, same-tree secondleg/customer3, physical-versus-stock read models.
- [Межскладская приёмка матрёшки](../database/retailcase_ni061_nested_receiving_20261012.md):314 actual firstleg316/sameTOP-BOX/3oldunits6codes/2newlinks/rollback-replay/P3; wholeHU placement next.
- [Матрёшка второго межскладского плеча](../database/retailcase_ni061_nested_onward_20261012.md):312–313 actualTOP/BOX/STOCK3/oneplace/LOAD-DEPART-STORE/customer3/sourceFF3once; scoped current bindings.
- [SAP-агрегации межскладской приёмки](../database/retailcase_ni061_sap_aggregation_scan_20261012.md):311 exact applied original order-line/versions; actual2scans/3units/6codes; SAP CLOB import fixed.
- [Агрегационные сканы межскладской приёмки](../database/retailcase_ni061_aggregation_scan_20261012.md):310 actual2scans→3oldunits/6codes/P3H0/native rollback/replay; nonSAP sender composition reused.
- [Режим сканирования межскладской приёмки](../database/retailcase_ni061_flexible_unit_mode_20261012.md):309 UNIT_OR_AGGREGATION принимает точные QR единиц; BOX/PALLET не обходятся.
- [Отмена сообщения о находке](../database/retailcase_ni061_recovery_cancel_20261011.md):307–308 actualapprovedcancel/rollback/replay/history/quota+samekey replacement; concurrentreceive-cancel200/409/oneeffect.
- [Доставка после частичной находки](../database/retailcase_ni061_partial_redelivery_20261011.md):306 actual1+1+1 originaltasks/ST/QC/load/depart/STORE; buyer3/originalFF3once/three lineages.
- [Частичная находка недостачи](../database/retailcase_ni061_partial_recovery_20261011.md):305 actualmarked lost2→found1+1, exactkeys/profiles/rollback/replay/globalnet0/read-case-selection/UI; placement-redelivery/cancellation next.
- [Повторные события недостачи](../database/retailcase_ni061_recurrent_loss_20261011.md):304 APPLIED event+unit keys/history2+2 retained/native active-loss admission; physical secondcycle pending.
- [Повторная доставка найденного остатка](../database/retailcase_ni061_recovery_redelivery_20261011.md):302–303 originalST/QC/LOAD/DEPART/STORE reused; buyer1+2=3/originalFF3once/history2-found2-net0; qualitygatePASS.
- [Размещение найденного груза](../database/retailcase_ni061_recovery_placement_20261011.md):301 existingTASK_COMPLETE/common cellpolicy/ordinary+marked2 conserved/no buyercredit.
- [Текущая работа RETAILCASE](../runbooks/retailcase_active_work.md): onramp12Oct/current native309/app307/planrev13/remaining functional scope.
- [Быстрый поиск контейнеров ячейки](../database/retailcase_ni081_container_cell_20261011.md):178 sparse index84 entries/native count112→0.825ms,7-cell same-snapshot equality/no P change.
- [Упаковка в занятом слоте](../database/retailcase_ni041_slot_repack_20261011.md):177 actual411/one merged claim/tare2/P-H unchanged/late rollback/concurrent API/unpack reversal; sparse container-cell index next.
- [Тара внутри матрёшки](../database/retailcase_ni063_nested_tare_20261011.md):176 explicit retained CASE book/native scope/scoped read; outbound archived handover positive remains pending.
- [CASE между слотами](../database/retailcase_ni041_case_relocation_20261011.md):175 actual409/CASE1048 native rollback/concurrent HTTP/no P-H effect, source released.
- [Повторное планирование остатка](../database/retailcase_ni032_remaining_plan_20261011.md):174 existing original4/shipped3→plan1, concurrent SOFT winner, scoped native locks/no P effect.
- [Частичное исполнение одной строки](../database/retailcase_ni033_single_order_partial_20261011.md):173 original4/shipped3/remaining1, same planline/different PT, mixed404/rollback/concurrent receipt; no new allocator.
- [Смешанное завершение волны](../database/retailcase_ni033_mixed_wave_20261011.md):172 preserved SHIPPED3/pending1/native rollback/concurrent403/UI; real old item-scan gate reused.
- [Потребность исходной строки](../database/retailcase_ni033_line_demand_20261011.md):171 same old pool math/targeted per-line read/current source snapshot; no new allocator.
- [Отмена пустого CASE](../database/retailcase_ni033_empty_case_20261010.md):170 existing return owner/atomic H release/rollback/ТСД; actual tare book refusal→release→wave399 completion; physical goods unchanged.
- [Явное завершение возвращённой волны](../database/retailcase_ni033_wave_defer_20261010.md):169 same native owner/current scope/replay; closed401/402 with unfulfilled order demand retained; no stock changes.
- [Возвращённое CASE в завершении волны](../database/retailcase_ni033_wave_return_diagnostic_20261010.md):168 current actor/WARE/read snapshot; historical1/physical0; existing pool preserves demand1; no finish bypass.
- [Идемпотентное закрытие CASE](../database/retailcase_ni033_case_close_20261010.md):167 preserved terminal states/command journal/actual HTTPCASE1037/rollback/P2H1; own cancelled-wave decisions pending.
- [Склад правил маркировки и недостач CASE](../database/retailcase_ni033_case_policy_short_scope_20261010.md):166 same native scope/current SKU card/short list, no new marking engine.
- [Текущий склад команд CASE](../database/retailcase_ni033_case_command_scope_20261010.md):165 native actor/right/WARE before replay and after actual mutex wait, same reader helper, P unchanged.
- [Текущий склад чтения CASE](../database/retailcase_ni033_case_read_scope_20261010.md):164 original queue/detail/currentactorWARE/same snapshot/query extraction/bounded histories.
- [Общий предварительный контроль транспорта](../database/retailcase_ni081_transport_preflight_20261010.md):163 same native capacity rules/read-only plan+manual/current scope/UI, strict admission unresolved.
- [Расписание существующего VRP](../database/retailcase_ni081_vrp_schedule_20261010.md):162 actual OR-Tools cumul/own service/return/archive633, fallback unknown, no strict admission.
- [Варианты покрытия нагрузки](../database/retailcase_ni081_workload_recommendations_20261010.md):161 person-hours/window advice, form fill only, actual CASE20/4h, no operational admission.
- [Маршрут кандидатов и режим диапазона](../database/retailcase_ni081_candidate_scope_20261010.md):160 scoped newfaces/wholeSKU demand/currentdrain mode/oldreplay retained; cell-prefix commitment indexes.
- [Большой ответ внешней доставки](../database/retailcase_outbox_clob_response_20261010.md):159 native CLOB over32K/exactnumeric+Unicode/aware leaseUTC/no realACK.
- [Утверждение диапазона и вымывание](../database/retailcase_ni081_range_apply_20261010.md):158 original assignment/native volume/current source/atomic publication/old commitments preserved/future refill stopped/empty closure.
- [Сохранённое предложение диапазона](../database/retailcase_ni081_range_proposal_20261010.md):157 immutable draft/source/actor/cancel/replay; sameID uniqueness without stock fence; approval/drain next.
- [Рекомендация диапазона и затрат](../database/retailcase_ni081_range_recommendation_20261010.md):156 same-snapshot whole-pallet candidates/explicit gross and cost assumptions/old range retained/no apply.
- [Восстановление ответа после перезапуска](../database/retailcase_outbox_response_recovery_20261010.md):155 durable local outcome before native finish/recovery without provider resend/disabled adapter can finalize.
- [Захват и завершение outbox](../database/retailcase_outbox_lease_20261010.md):154 aware lease/generation/stale-response fencing/atomic finish/manual audit; private concurrent case/no stock.
- [Ошибка адаптера остаётся в повторе](../database/retailcase_outbox_response_20261010.md):153 responseERROR/HTTP503→requestERROR/eventRETRY1/raw38digits preserved/no realACK.
- [Действующий пользователь общего ядра](../database/retailcase_stock_actor_admission_20261010.md):152 active RUSERS before replay/after locks/body-onlyVALID/exact old receipt restored/no stock.
- [История планового выхода](../database/retailcase_ni081_attendance_history_20261010.md):151 original aware records/approver/cancellation/relational chain/paginated depth bound/current warehouse/read-only.
- [Атомарное изменение планового выхода](../database/retailcase_ni081_attendance_replace_20261010.md):150 source cancellation+new plan one UOW/future only/late rollback and concurrent one winner/current lineage/no stock.
- [Типизированные границы native-команд](../architecture/retailcase_typed_native_boundaries_20261010.md):149 concrete DTO/public ports/same-cursor staging/old ARM URI/cache retained; full quality gatePASS499files0cycles79debt.
- [Общий запрет старых проводок PREPARED](../database/retailcase_cutover_adapters_20261010.md):148 ten adapters ACTIVE-only/native-first legacy tails removed/13 casesPASS/debt118/stock unchanged.
- [Синхронизация задания читает проводку](../database/retailcase_task_sync_readonly_20261010.md):147 PREPARED effect executor removed/ACTIVE proof only/original829 retry unchanged/7 boundary casesPASS.
- [Удалён старый путь завершения задания](../database/retailcase_task_single_writer_cleanup_20261010.md):146 native root only/SAP cancel-replan current scope/internal pallet ID;3 cutover cases PASS.
- [Ёмкость действующего диапазона](../database/retailcase_ni081_range_capacity_20261010.md):145 original face/cell/native volume budget/withdrawal blockers; actual508 volume0/P20H20/no apply.
- [Склад пользователя складского задания](../database/retailcase_ni081_task_scope_20261010.md):144 current active actor/assignee WARE, root replay authorization, old829 replay exact/no new quantity.
- [Источники потребности для диапазона](../database/retailcase_ni081_slotting_demand_20261010.md):143 original pool/secured overlap/period/old stock/incoming/forecast consumption/read-only scenario/no zero demand claim.
- [Настройка прежнего слотирования атомарна](../database/retailcase_ni081_pickface_config_20261010.md):142 native assign+extended one CONFIG fence/current WARE/Decimal/occupied drain refusal/actual rollback/P20H20 unchanged.
- [ARM-расчёт сохраняет фактические операции](../database/retailcase_ni081_operation_plan_20261010.md):141 native original12 stages/replay IDs/no DELETE/current fact scope/history guard/actual33530 no stock.
- [Утверждённое окно прежней волны](../database/retailcase_ni081_wave_time_20261010.md):140 aware version/replay/stale refusal/monitor reads actual approval/shift effect/P20H20 unchanged.
- [Устойчивое создание кластера](../database/retailcase_ni081_cluster_retry_20261010.md):139 native operation/source snapshot/concurrent one TT33528/replay after cancellation/savepoint/React pending.
- [Единое проведение и атомарный кластер](../components/retailcase_single_writer_cluster_20261010.md):138 native reuse/one UOW/actual rollback and SAP replay/zero cycles; durable cluster retry next.
- [Ручное изменение машины и плана рейса](../database/retailcase_ni081_trip_edit_20261010.md):137 shared prospective capacity/vehicle-before-TT/current actor; smaller vehicle409, departed date protected, no stock.
- [Атомарное применение существующего транспортного плана](../database/retailcase_ni081_atomic_plan_20261010.md):136 one-TX native TT/ST/manual capacity, concurrent plan632→TT33523 once, later-route rollback/driverNULL, timing and vehicle edits next.
- [Проект общего контроля транспортного плана](../database/retailcase_ni081_transport_plan_design_20261010.md): existing solver/constructors retained.
- [Нагрузка и план выхода персонала](../database/retailcase_ni081_workload_20261010.md):134 native norm/aware person roster;135 current CASE20/4person-hours vs2 planned/deficit2/no duplicate person/no stock; approved reschedule and subwarehouse next.
- [Проект ресурсного монитора](../database/retailcase_ni081_workload_design_20261010.md): existing personnel retained, additive norm/attendance only.
- [Прогноз по исполненным грузам](../database/retailcase_ni081_forecast_20261010.md):133 immutable native projection/CASE20/top2/warehouse scope/UTC mean/no stock; resources and plan validator next.
- [Состав и происхождение паллеты](../database/retailcase_ni043_composition_reader_20261010.md):132 same-snapshot P/H/physical units/multiple profiles/original inventory-MES-SAP source/signature-bound pages.
- [Проект прогноза](../database/retailcase_ni081_forecast_design_20261010.md):133 derived history only, native root unchanged.
- [Табачный GTIN и честный режим внешнего обмена](../database/retailcase_ni043_regulatory_runtime_20261010.md):130 contextual rawGTIN01/serial21/native3/replay;131 defaultdisabled/pending preserved/explicit simulation never legalACK/existing outbox reused.
- [QR штук и складская область пересчёта](../database/retailcase_ni043_unit_capture_20261010.md):128/129 current operator profiles/UNIT physical3 codes6/P3H0/no manifest/stale409/replay; current actor foreign read/birth/count/create403, native kernelsVALID.
- [Актуальный склад исполнителя MES](../database/retailcase_ni043_mes_scope_20261010.md):127 APPLIED/core+rootVALID/current nonadmin wrongWARE403/P0 then ownWARE native P3H0/replay; no new stock writer.
- [Маркированный выпуск MES по составу отправителя](../database/retailcase_ni043_mes_manifest_20261010.md):126 native order98/FGmovement120/current source/capture/P3H0/physical3/use1/HTTP replay, existing commands preserved.
- [Внутренний идентификатор и регуляторный SSCC](../database/retailcase_ni043_internal_identifiers_20261010.md):125 HTTP current nonadmin, UID39 retained, absent or separate proven SSCC, P3H0/replay/wrong mode409/foreign403.
- [Состав маркированного груза от отправителя](../database/retailcase_ni043_sender_manifest_20261010.md):124 APPLIED, graph4/scans2/physical3/codes6/P3H0/replay/current profile; native non-SAP source, no fabricated SAP receipt or government ACK.
- [Итоговая межскладская доставка исходному заказу](../database/retailcase_ni061_final_delivery_20261010.md):123 APPLIED, original shipped3 stays3/final accepted3/first-to-final lineage/no stock repeat, ordinary two-leg slice end-to-end; marked/nested/packing remain open.
- [Прежняя СТ второго межскладского плеча](../database/retailcase_ni061_onward_20261010.md):122 APPLIED, native constructor/rows/existing assignment/whole3 load and depart/original customer64 unchanged/P0H0/no second fulfillment; final receipt next.
- [Ответственность первого межскладского плеча](../database/retailcase_ni061_custody_20261010.md):121 APPLIED, actual119 receipt/native release/history DEPARTED retained/activeUID released/P3H0 unchanged/replay; onward ST next.
- [Межскладское задание к воротам](../database/retailcase_ni061_placement_20261010.md):120 APPLIED, existing task829 DONE/SYNCED/native P3H0 conserved/receiving0/outbound3/replay; onward custody/ownership next.
- [Физическая приёмка межскладского груза](../database/retailcase_ni061_receiving_20261010.md):119 APPLIED, original unload0/native target receipt3H0/event1/SAP pending1/replay/source0; onward existing task/leg next.
- [Связь существующих межскладских плеч](../database/retailcase_ni061_two_legs_20261010.md):118 APPLIED, actual departed standalone cargo/original ST/existing target TT/docks/deadlines/replay/no stock birth; physical receipt next.
- [Завершение расследованного расхождения](../database/retailcase_ni062_case_closure_20261010.md):117 APPLIED, original two findings/current independent KRO/CLOSEDv5/SAP pending/replay/no quantity, open obligations/foreign case denied.
- [Общая сверка исполнения](../components/retailcase_ni072_reconciliation_20261010.md):116 current consistent Oracle snapshot/day-aware facts/current queues/P-H-unit conflicts/ERP pending, no writes/day close.
- [Часовые пояса Oracle и дневные факты](../incidents/oracle_naive_timestamps_20261010.md): server−04/session+03/DB+00; naive fields excluded from daily counts, actual TZ facts used.
- [Финансовые факты в прежнем outbox](../database/retailcase_ni071_outbox_20261010.md):115 same-TX finance/event, deterministic projection9/retry0, scoped generic XML export/EXPORTED without SAP ACK.
- [Поздняя коррекция расходов](../database/retailcase_ni071_correction_20261010.md):114 APPLIED, linked signed credit/dual phases/current original total recheck/stale second denied/net0/history/no goods.
- [Распределение расхода на фактический товар](../database/retailcase_ni071_allocation_20261010.md):113 APPLIED, original approved10.01/exact source weights/cents/replay/vehicle denial, Decimal boundary exact; existing invoice extra lines.
- [Допрасход: логист и финансовый контроль](../database/retailcase_ni071_expenses_20261010.md):112 APPLIED, original TT10.01GEL/independent phases, vehicle4.00 only/no goods, included-rate work denied.
- [Стоимость физической коробки рейса](../database/retailcase_ni071_box_cost_20261010.md):111 APPLIED, existing actual BOX1/frozen2.50GEL/v1 despite futurev2/replay/no second charge; original invoices preserved.
- [Списание возвратного брака](../database/retailcase_ni062_disposal_20261010.md):110 APPLIED, separate act/independent Root/exact blocked1/P0H0/event1/loss original store/outbox1/replay.
- [Документальная передача поставщику](../database/retailcase_ni062_supplier_handover_20261010.md):109 APPLIED, departed108/source/independent SC/replay/outbox1/no second P; manual evidence.
- [Поставщик: прежняя СТ и фактическая погрузка](../database/retailcase_ni062_supplier_dispatch_20261010.md):108 APPLIED, exact placed return1/native ST/load/P0H0/replay/departure; supplier receipt distinct.
- [Исправная коробка возвращена в отбор](../database/retailcase_ni062_reuse_boxes_20261010.md):107 APPLIED, own SAP source BOX24→actual store→approved return→blocked receipt/proof1x24→existing task/picking24/eligible/replay.
- [Oracle native JSON в SAP обмене](../incidents/oracle_native_json_sap_20261010.md): actual ARTMAS/supply/receipt bridge fixed, native dict/list and text supported, reserved raw bind removed.
- [Недостача тары магазина и автомобиля](../database/retailcase_ni063_holder_loss_20261010.md):106 APPLIED, original debt1→0/deadline retained; pending vehicle claim blocks transfer then reject restores1; driver UI.
- [Складская недостача тары](../database/retailcase_ni063_warehouse_tare_loss_20261010.md):105 APPLIED; claim physical3/free2, independent writeoff2/free2, reject releases suspicion; goods unchanged.
- [Недостача тары существующей волны](../components/retailcase_ni063_tare_forecast_20261010.md):104 current CASE/type/free/shortage, pending returns separate, API actual2/free1/short1.
- [Тара самостоятельной FULLPAL](../database/retailcase_ni063_fullpal_tare_20261010.md):103 APPLIED, original STOCK/current cell/BOOK/existing single load/current driver accept, warehouse0 vehicle1.
- [Тара погруженного места](../database/retailcase_ni063_booked_handover_20261010.md):102 APPLIED, exact actual root load/booked claim/driver accept, warehouse0 vehicle1, goods not repeated.
- [Пригодная тара в сборке](../database/retailcase_ni063_tare_assembly_20261010.md):101 APPLIED, actual4 booked/fifth refused/cancel free4, existingCASE1020 snapshot; real sessionSTART/cargo-handover next.
- [Повреждение и списание тары](../database/retailcase_ni063_tare_resolution_20261010.md):100 APPLIED; real GOOD2→DAMAGED2/independent writeoff1/debt1 originaldue, no goods stock; planning next.
- [Сроки и долг тары](../database/retailcase_ni063_tare_deadlines_20261010.md):099 APPLIED; immutable policy/explicit timezone/FIFO, actual old2 settled/new2 unchanged by futureconfig; NEXT_DELIVERY independent case open.
- [Баланс оборотной тары](../database/retailcase_ni063_tare_ledger_20261010.md):098 APPLIED; actual6 out/4 back/store2, two actors/concurrent4+4→4, no goods P effect; deadlines next.
- [Размещение возврата](../database/retailcase_ni062_return_putaway_20261010.md):097 APPLIED, existing WT823 DONE/SYNCED, P1H0, immutable placement/SAP pending; capacity SQL4867→3.540мс.
- [Склад принял возврат](../database/retailcase_ni062_return_receiving_20261010.md):096 APPLIED, actual supplier returns1+2/blocked P3H0/shared barcode/typed STORE_RETURN header/no purchase; placement/REUSE/marked next.
- [Магазин передал — водитель принял](../database/retailcase_ni062_return_custody_20261010.md):095 APPLIED, authenticated binding/two actors/current trip/scans/custody VEHICLE; no stock birth, warehouse receipt next.
- [Вывоз возврата существующим рейсом](../database/retailcase_ni062_return_transport_20261010.md):094 APPLIED, source/SAP receiving ware/current TT/conservative capacity, outbox/no P; actual pickup next.
- [SAP возврат из магазина](../database/retailcase_ni062_sap_return_20261010.md):093 APPLIED, XML source/recipient/raw bytes/exact replay, existing file gateway; no purchase/P birth or real SAP ACK.
- [Разрешение возврата магазина](../database/retailcase_ni062_return_approval_20261010.md):092 APPLIED, original accepted/cumulative cap/concurrent2+2→2, no stock birth; SAP/logistics next.
- [Расследование расхождения](../database/retailcase_ni062_case_work_20261010.md):091 APPLIED, два заключения/independent KRO/version/replay, no second stock; return SAP remains open.
- [Приёмка в исполнении заказа](../database/retailcase_ni053_order_delivery_20261010.md):090 bounded read-only actual2+missing1/full3/weight-case, original demand/shipment retained; shared partial owner split unresolved.
- [Весовой допуск магазина и акт](../database/retailcase_ni053_weight_admission_20261010.md):089 APPLIED; current scale+three different originals/real BOX tolerance, actual non-admin9/upper11/act/replay/no second stock.
- [Масса физических коробок](../database/retailcase_ni053_load_boxes_20261010.md):088 APPLIED; same actual root load/frozen BOX2KG/half1/API replay/P0; mandatory missing-proof denial.
- [Устойчивое показание магазина](../database/retailcase_ni053_scale_capture_20261010.md):087 APPLIED; dedicated gateway/original packet/stability/calibration/replay, synthetic actual API only; hardware/receipt admission pending.
- [Расхождения при приёмке](../database/retailcase_ni053_discrepancy_20261010.md):086 APPLIED; accepted2/missing1/extra1, exact replay/open obligations/outbox/no second P; driver counters and dispatcher dossier.
- [Фотоархив приёмки](../database/retailcase_ni053_photo_archive_20261010.md):085 APPLIED, original JPEG/PNG/hash/source/receiver, actual upload/retry/recovery/refusals/audit0; mandatory weight admission next.
- [Регистр имён прав](../database/retailcase_permissions_case_20261010.md):084 APPLIED, normal uppercase admin grant works in API/Oracle; real non-admin store binding and deactivation passed.
- [Приёмка обычного места магазином](../database/retailcase_ni053_store_barcode_20261010.md):083 APPLIED, authenticated/address-bound full ordinary receipt3/replay/no second quantity, driver component; weight/photo/marked/partial remain open.
- [Очистка Oracle lease](../incidents/oracle_metadata_pool_state_20261010.md): metadata timeout poisoned package state; same-session recovery passed, mini-max restarted OK.
- [Адрес физического места](../database/retailcase_ni053_destinations_20261010.md):082 APPLIED, frozen ST address/current locked recheck, loaded address edits denied; store receipt next, targeted case pending.
- [Ранее списанное HU: фактическая погрузка](../database/retailcase_ni052_reconciliation_20261010.md):081 APPLIED, original manifest/epoch/source link, actual HTTP load/departure/replay/no second journal; standalone history pending.
- [Назначение СТ и конкуренция](../database/retailcase_ni052_trip_serialization_20261010.md):080 APPLIED, one legacy writer/TT→ST, direct write guard, actual wait/recheck/cancel passed.
- [Пересчёт: модульная граница](../database/retailcase_inventory_observation_module_20261010.md): typed port/infrastructure, actual HTTP birth/count/replay/conflict/cleanup passed.
- [Самостоятельная погрузка / QC без списания](../database/retailcase_ni052_single_loading_20261010.md):078/079 APPLIED; actual CASE/FULLPAL FKs, independent12+8/load/departure/replay; old auto flag no longer consumes on control.
- [Фактическая погрузка и выезд](../database/retailcase_ni052_loading_20261010.md):077 APPLIED; upper HU one load fact/P0H0/replay, pending ST blocks trip, separate departure no second posting; API/ARM connected; growing history lookups indexed.
- [Факт погрузки и выезд: задание](../database/retailcase_ni052_loading_design_20261010.md):077 design; existing TT/ST/dock reused, root atomic load fact and separate departure, no duplicate assignment.
- [CASE в отдельном слоте](../database/retailcase_ni041_case_slot_20261010.md):076 APPLIED; actual CASE identity/FK, native12+8/unpack P20/H20/replay/no fake PP, existing move frees claim, own cleanup passed.
- [FULLPAL в верхнем HU](../database/retailcase_ni041_fullpal_hu_shipping_20261010.md):075 APPLIED; existing ST/physical FULLPAL binding survives intact movement, exact whole tree shipment, P/H0/replay and scoped nested history passed.
- [Товарная паллета и пустая тара](../database/retailcase_ni041_stock_leaf_20261010.md):074 APPLIED; own P5/H2/replay/remeasure/stale denial passed, empty carrier/claim cleanup; stock measured claim binds physical composition.
- [Версия товарного состава](../database/retailcase_ni042_composition_epoch_20261010.md):073 APPLIED; correction/restore permanently revokes old QC, reservation/intact move retains epoch; v1 requires recontrol, rollback forward only.
- [Физическая версия количества](../database/retailcase_ni042_physical_epoch_20261010.md):072 APPLIED; P changes advance epoch, HARD-only does not; quantity restoration keeps newer epoch, protected unit digest foundation for measured stock leaves.
- [Смена слота целого HU](../database/retailcase_ni041_slot_relocation_20261010.md):071 APPLIED; shared place writer, same-cell slotB→C/P10/H2/no quantity journal/replay+sync; nested departure history narrowed, independent acceptance pending.
- [Вскрытие в отдельный слот](../database/retailcase_ni041_slotted_unpack_20261010.md):069/070 APPLIED; two actual tasks/claims, P10/H2 unchanged/same reserve/new child slot/no quantity journal/replay+sync; multi-leaf fact key corrected.
- [Вскрытие в слот: решение](../database/retailcase_ni041_slotted_unpack_design_20261010.md):next bounded slice, two actual placement tasks/claims, quantity unchanged; not installed.
- [Несколько HU в ячейке](../database/retailcase_ni041_multi_hu_slots_20261010.md):068 APPLIED; distinct slots/current+planned aggregate SI load, two tasks/P10/H2/100kg3m3/replay; slotted unpack and same-cell transfer pending.
- [Отгрузка верхнего CASE-HU](../database/retailcase_ni041_hu_shipping_20261010.md):067 APPLIED; one root/actual existing ST core, CASE12+8/P0/H0/replay, historical preview and freed place; ordinary leaves/routes/independent acceptance pending.
- [Контроль CASE и упаковка](../database/retailcase_ni051_case_control_20261010.md):065/066 APPLIED; actual existing statuses/events, independent BOTH, nested auto deferred, unpack revokes both admissions; upper HU shipment next.
- [Выборка и полная сверка](../database/retailcase_ni051_sampling_20261010.md):064 APPLIED, sticky sample/root PLAN, ordinary exact barcode/UOM/event proof, failed findings revoke old approval, mandatory rescan and QR preserved; CASE status/labels next.
- [Независимый QC](../database/retailcase_ni051_independent_control_20261010.md):063 APPLIED, real picking actors, admin self-check denied, other controller/BOTH deferred auto/shipment/replay passed; sampling next.
- [Уникальные марки QC](../database/retailcase_ni051_mark_quality_20261010.md):062 APPLIED;3 physical units/6 CRPT+EGAIS codes, weight/waiver/count-only/foreign/missing/duplicate denied; existing registry/API/ARM, controller/aggregation next.
- [SI масса и допуск QC](../database/retailcase_ni051_weight_policy_20261010.md):061 APPLIED; explicit KG/BASE policy, actual composition sum and half-lightest-box inclusive tolerance; cached legacy weight/3.5 no longer used by QC root.
- [QC актуального состава](../database/retailcase_ni051_quality_binding_20261010.md):060 APPLIED, existing scan/weight→semantic stamp→SHIP gate; legacy flags/stale/edit-restore/failure denied. SI tolerance/roles/mark coverage next.
- [Partial target supply](../database/retailcase_ni032_partial_target_supply_20261010.md):059 APPLIED, target3/H3 + existing whole20/H17 -> target23/H20/free3, CASE12+8/replay/capacity denial passed; only unissued source work can rebind.
- [Oracle JSON array replacement](../concepts/oracle_json_array_semantics.md): use explicit overwrite=true when updating an element; put defaults to insertion.
- [Multi-UID target supply](../database/retailcase_ni032_multi_target_supply_20261010.md):058 APPLIED, one root batch replaces storage HARD12+8 from target11+9, shared UID/version accounting, no physical replenishment; CASE/replay/cleanup passed.
- [Whole CASE-HU staging](../database/retailcase_ni041_hu_staging_20261010.md):057 APPLIED, reuses existing system control/staging policy for closed CASE-only trees; native20/H20/replay passed, ordinary stock excluded.
- [Owner and HU closure](../database/retailcase_owner_and_hu_closure_20261010.md):056 APPLIED, same-order target coverage, bounded actual-wave fulfillment, HU10000-unit bound and sorted CASE real-row locks; narrow changed cases passed.
- [HU cell limits/settings](../database/retailcase_ni041_hu_cell_limits_20261010.md):055 APPLIED, topology-cell aggregate limits and existing warehouse height-unit configuration; one-place bound retained.
- [CASE inside warehouse HU](../database/retailcase_ni041_hu_case_20261010.md):054 APPLIED, existing CASE12+8 under one HU, whole20/H20 and nested standalone move denied; top-place shipping next.
- [HU physical slot](../database/retailcase_ni041_hu_slots_20261010.md):053 APPLIED, existing task frozen SI measurements/current slot/one parent claim; leaf5/H2/replay/scan and bounds passed, multi-place/CASE next.
- [HU existing warehouse task](../database/retailcase_ni041_hu_tasks_20261010.md):052 APPLIED, plan/assign/start/complete1HU with leaf5EA/H2, resource/sync/replay; physical slots next.
- [Whole HU movement/API/UI](../database/retailcase_ni041_hu_move_20261009.md):051 APPLIED, top/box/leaf5/H2 movement, owner/replay/blocked/nested cases passed; physical slot/task/CASE adapters next.
- [HU packing/unpacking](../database/retailcase_ni041_hu_tree_20261009.md):050 APPLIED, existing pallet identity and single-parent versioned links; P/H5/2 unchanged, cycles/duplicate parent/nested P denied. Whole movement next.
- [Складское HU дерево](../database/retailcase_ni041_hu_design_20261009.md):NI04.1 implementation started; reuse existing pallet/CASE identities, separate warehouse/regulatory composition; design only before DDL.
- [Фактическое завершение волны](../database/retailcase_ni033_wave_finish_20261009.md):049 APPLIED, monitor blockers + root DONE after shipped facts/no HARD; dev FULLPAL/replay passed; CASE variants open.
- [Целевой запас вместо повторной подачи](../database/retailcase_ni032_target_supply_20261009.md):048 APPLIED, atomic own HARD replacement, blocked target/replay/CASE12+8; existing continuation worker extended.
- [Общая подача и несколько ячеек](../database/retailcase_ni032_shared_supply_20261009.md):044–047 APPLIED; native CASE12+8/one pallet and two physical-source groups/two dynamic faces; target HARD rebalance next.
- [NI03.3 FULLPAL](../database/retailcase_ni033_fullpal_20261009.md): 040–043 APPLIED, physical pallet→existing ST→pinned whole shipment, own HARD fix and covered-plan closure; full scope open.
- [Альтернативные ячейки](../database/retailcase_ni032_alternative_faces_20261009.md): 039 APPLIED, existing dynamic assignment/CASE routing/BASE norm and shared durable source intent; multi-face split remains open.
- [Допуск отбора NI03.3](../database/retailcase_ni033_execution_20261009.md): 038 APPLIED, separate prepare/release, real replenishment→coverage→release/replay; alternative capacity routing next.
- [NI03.3 execution](../database/retailcase_ni033_execution_20261009.md): 032–037 APPLIED; BASE shipment, original-demand-preserving partial ST, shift/incident instants; full sprint scope remains open.
- [NI03.2 replenishment lifecycle](../database/retailcase_ni032_replenishment_lifecycle_20261009.md):021–024 APPLIED, generic CASE binding, cumulative facts и mini/MAX cycle/API/UI; remaining sprint scope открыт.
- [NS21 общий SOFT пул](../database/retailcase_soft_pool_20261009.md):019–020 APPLIED, policy/API/UI, concurrent pool и atomic existing wave HARD/replay; остальной NI03.2 в работе.
- [Исходники NI03.2](../components/retailcase_ni032_source_map.md): владельцы modules, composition port, Oracle manifest, ARM scripts и worker lifecycle.
- [Worker восстановления CASE](../runbooks/retailcase_short_recovery_worker.md): dev runtime, lease/frozen intent/restart, роли и эксплуатационные ограничения.
- [NI03.2 исполнение и восстановление](../database/retailcase_ni032_task_recovery_20261009.md): в работе с 13:45 MSK; 008–018 APPLIED, partial/mark scans/recovery/capacity/resources; оставшийся функциональный объём открыт.
# TMS Wiki Index
- [NI03.1 source eligibility](../database/retailcase_ni031_stock_eligibility_20261009.md): установлен общий Oracle допуск/явный DIRECT, planner и locked command rechecks, причины в UI/API; dev cases passed, P=H=0, общий architecture gate имеет прежний debt. Текущий NI03.2 в работе.
- [RETAILCASE plan revision 11](../requirements/retailcase_delivery_v55/implementation_plan.md): 8 направлений/18 остаточных спринтов, текущий NI03.2 в работе; stock cutover закрыт, 68 NS/363 сценария сохранены.
- [database/retailcase_stock_posting_cutover_20261009.md](../database/retailcase_stock_posting_cutover_20261009.md): актуальный статус — RABAEV ACTIVE, B0 сохранён, compatibility OFF, registry 25/6/0; реальные replay/concurrency/rollback cases прошли.
- [database/retailcase_stock_posting_case_shipment_20261009.md](../database/retailcase_stock_posting_case_shipment_20261009.md): 197–207, CASE → существующая СТ, whole-carrier shipment, защита packed stock и Decimal MES; APPLIED, registry 23/6/2, PREPARED.

- [database/retailcase_stock_posting_case_20261008.md](../database/retailcase_stock_posting_case_20261008.md): 159–169, физический CASE carrier/HARD, QR и durable ТСД, whole carrier move; PREPARED, полный переход открыт.

- [database/retailcase_stock_posting_revision_20261008.md](../database/retailcase_stock_posting_revision_20261008.md): 151–158, REVIZION EA/BOX и создание паллеты через ядро, atomic row projection, Decimal/durable WinForms; PREPARED, без cutover.

- [database/retailcase_stock_posting_receipt_inventory_20261008.md](../database/retailcase_stock_posting_receipt_inventory_20261008.md): компоненты 131–150; сторно, native inventory, metadata fences, замена автоматической приёмки существующим SAP экраном; 19 ADAPTED / 5 RETIRED / 7 UNCONVERTED, PREPARED.

- [database/retailcase_stock_posting_continuation_20261008.md](../database/retailcase_stock_posting_continuation_20261008.md): компоненты 121–130, импорт и пересчёт инвентаризации, outbox состава, повторы WinForms/sync/MES и исправление вызовов API; 47 pairs, 10 ADAPTED / 21 UNCONVERTED, PREPARED.

- [database/retailcase_dev_stock_reset_20261008.md](../database/retailcase_dev_stock_reset_20261008.md): owner-authorized reset; stock and journal 0, existing documents retained, PREPARED.

This is the maintained knowledge map for the TMS repository.


## Работа с документацией

- [runbooks/markdown_preview.md](../runbooks/markdown_preview.md): Markdown Preview Enhanced и текстовый редактор.

## Общий стандарт розничной логистики

- [Опросник WMS табачных хабов — редакция 2.0](../requirements/tobacco_regional_hubs/supplier_questionnaire_v2/questionnaire.md): 18.09.2026, 100 вопросов; помарочный учёт, собственники, SAP и Track & Trace.
- [requirements/tobacco_regional_hubs/README.md](../requirements/tobacco_regional_hubs/README.md): отраслевой профиль региональных табачных хабов 17.09.2026, 52 требования и вопроса.
- [requirements/retail_convenience_standard/README.md](../requirements/retail_convenience_standard/README.md): стандарт магазинов у дома, 17.09.2026, WMS/TMS требования, опросники и GAP.

- [incidents/oracle_apply_unhandled_exception_20261008.md](../incidents/oracle_apply_unhandled_exception_20261008.md): OracleApply error handling repaired; fixed runtime DLL used by stock installer.

- [database/retailcase_stock_posting_handlers.md](../database/retailcase_stock_posting_handlers.md): Components through 130: native inventory, event bridge, native move/shipment and MES, exact UOM, receipt/putaway and wave HARD; 10 ADAPTED / 21 UNCONVERTED, PREPARED, no B0/cutover.

- [database/retailcase_stock_posting_extension_20261008.md](../database/retailcase_stock_posting_extension_20261008.md): native MES/picking/wave, inventory command, own shipment, JSON binds; 47 pairs VALID, PREPARED, no physical acceptance/cutover.
- [incidents/oracle_stock_json_bindings_20261008.md](../incidents/oracle_stock_json_bindings_20261008.md): ORA-40573 corrected; rollback-only attempt rejected dirty transaction; no physical acceptance claim.

## RETAILCASE — межскладской подвоз и cross-dock

- [Локальное администрирование ORCL](../runbooks/retailcase_oracle_local_admin.md): существующая OS-сессия, SYSDBA без сохранения пароля; три grants RABAEV выданы. [Инцидент VirtualBox](../incidents/oracle_live_snapshot_20261008.md): live snapshot был избыточным для установки пакетов, дальнейшие обратимые изменения выполняются с source checkpoint/rollback.

- [Реализация проводки 2.0](../database/retailcase_stock_posting_implementation.md): 08.10.2026, очистка dev выполнена, foundation и runtime 016 APPLIED; 9 package + 9 body VALID, grants выданы. Coordinator/planner/manual move/signed legs/outbox установлены. PREPARED, новых operations 0, 31 legacy writer UNCONVERTED. Обратимые следующие изменения — source checkpoint/rollback без VM snapshot; полного cutover ещё нет.

- [ТЗ достоверных остатков и единой проводки](../requirements/stock_posting_core_tz.md): 07.10.2026, редакция 2.0. Математика P/H, перенос резерва, однозначный stock key, полный порядок fences/anchors и матрица существующих таблиц, whole-operation rollback/replay; 42 сценария будущей приёмки. Карантин через недоступные ячейки. Один cutover, compatibility default OFF; реализация/мощность ещё не подтверждены.
- [Целевой контракт базы для проводки](../database/retailcase_stock_posting_target.md): подтверждённые metadata ограничения текущей RABAEV и проектируемые изменения; новое ядро/DDL не установлены.

- [runbooks/retailcase_ni03_task_effect.md](../runbooks/retailcase_ni03_task_effect.md): NI03 начат — существующее warehouse completion/domain effect объединено транзакцией, WAVE movement через RRL_EVENTS, частичный резерв/residual и durable replay; 010 установлена в RABAEV. Остальной NI03 не закрыт.

- [Текущий NI03 и история рекомендации по проводке](../database/retailcase_ni03_task_effect.md): явная PL/SQL-команда/журнал предложены ранее; последующее решение владельца — один cutover всей системы и compatibility OFF по умолчанию, см. новое ТЗ.

- [components/retailcase_global_reuse_analysis_20261007.md](../components/retailcase_global_reuse_analysis_20261007.md): глобальное сопоставление текущего WMS/TMS и предложений; все 15 процессов/21 справочник, аудит новых стыков и найденных dev-заглушек.
- [components/retailcase_capability_matrix_20261007.md](../components/retailcase_capability_matrix_20261007.md): 35 возможностей с исходниками и решением reuse/extend. Вложенные SSCC уже есть в CRPT-агрегации; складской жизненный цикл не завершён.

- [components/retailcase_order_trip_reuse.md](../components/retailcase_order_trip_reuse.md): SAP подключён к существующим ORDERS/SBORKA writers и PLANNED fulfillment; назначение через прежний TMS API/TRANSTASK_ID, migration 009 в RABAEV. Auto-split dev stub требует оригинального body.

- [runbooks/retailcase_ni01_sap_retail.md](../runbooks/retailcase_ni01_sap_retail.md): NI01 baseline implemented with gaps, 001–007 в RABAEV; общий допуск stock/прямой отбор/сквозной состав в NI03–NI05. Промышленная приёмка не проводилась.

- [Основной план RETAILCASE: NI01–NI08 revision 11](../requirements/retailcase_delivery_v55/implementation_plan.md): актуальная очередь 18 остаточных спринтов, текущий NI03.2 в работе. Ядро stock ACTIVE/compatibility OFF; TMS/VRP/Ганта/billing повторно не создаются; 68 NS/363 сценария сохранены.
- [components/retailcase_approved_code_analysis.md](../components/retailcase_approved_code_analysis.md): анализ утверждённых исходников, карта существующих механизмов и необходимых стыков; 434 source hashes и 23 Oracle source definitions, без новых тестов.
- [sources/retailcase_code_baseline_proposal_20261007.md](../sources/retailcase_code_baseline_proposal_20261007.md): источники утверждены владельцем; текущие локальные файлы с незакоммиченными изменениями, корневой WindowsApplication2, RABAEV.
- [components/retailcase_existing_wms_reuse.md](../components/retailcase_existing_wms_reuse.md): первоначальный разбор старой WMS, затем сверенный по утверждённому baseline.
- [components/retailcase_source_structure.md](../components/retailcase_source_structure.md): фактическая структура и модульное развитие; минимум 80% ресурсов на функционал.
- [requirements/retailcase_delivery_v55/README.md](../requirements/retailcase_delivery_v55/README.md): план доработок редакции 57; основная очередь NI01–NI08, каталог NS00–NS67, старые оценки сняты.
- [runbooks/retailcase_ns00_environment.md](../runbooks/retailcase_ns00_environment.md): ядро NS00 реализовано в RABAEV, source review APPROVE_SOURCE; дополнительные прогоны/cold install остановлены, временная копия Oracle выключена.
- [architecture/retailcase_technology_stack_20261007.md](../architecture/retailcase_technology_stack_20261007.md): приняты FastAPI/Python, React/TypeScript и Oracle; мощность не объявлена подтверждённой.
- [roadmap/retailcase_requirements_to_production.md](../roadmap/retailcase_requirements_to_production.md): прежний порядок анализа/выпуска; текущая очередь — NI01–NI08.
- [requirements/retailcase_business_processes/restart_context.md](../requirements/retailcase_business_processes/restart_context.md): текущая редакция 57 и утверждённый baseline; [open_questions.md](../requirements/retailcase_business_processes/open_questions.md) — решения Q01–Q28.
- [requirements/retailcase_business_processes/README.md](../requirements/retailcase_business_processes/README.md): редакция 57, 15 процессов, 21 справочник; приёмка SAP, маркировка/данные RABAEV; [Word](../requirements/retailcase_business_processes/Retailcase_business_processes_v57.docx), [проверка документа](../requirements/retailcase_business_processes/editorial_review_v57.md).
- [requirements/retailcase_retail_selection/README.md](../requirements/retailcase_retail_selection/README.md): retail RFP 16.09.2026.
- [roadmap/retailcase_crossdock_first.md](../roadmap/retailcase_crossdock_first.md): прежний cross-dock план, не заменяет текущий NI-план.
- [requirements/retailcase_crossdock_increments.md](../requirements/retailcase_crossdock_increments.md): исторические срезы CD00–CDP и критерии интеграции.
- [roadmap/retailcase_crossdock_agent_map.md](../roadmap/retailcase_crossdock_agent_map.md): исторические назначения CD.
- [tools/retailcase_orchestrator/README.md](../../tools/retailcase_orchestrator/README.md): локальный state-machine runner; автоматические прогоны не запускать вопреки текущему поручению.



- [roadmap/retailcase_agent_delivery_plan.md](../roadmap/retailcase_agent_delivery_plan.md): актуальная детализация — 10 архитектурных + 28 функциональных спринтов, S0 и два пилота; модели, сроки, токены, API/электричество и время владельца без амортизации.
- [Каталог 41 индивидуального ТЗ](../requirements/retailcase_sprints/index.md), [общий договор приёмки](../requirements/retailcase_sprint_contract.md), [запуск агентов](../runbooks/retailcase_agent_launch.md): bounded tickets, независимые тесты, установка и stop rules.
- [sources/retailcase_agents_20260915.md](../sources/retailcase_agents_20260915.md): цены/официальные источники, уже купленный незапущенный сервер 2 × 16 ГБ, допущения и локальная проверка сметы.
- [requirements/retailcase_ui_workplaces_tz.md](../requirements/retailcase_ui_workplaces_tz.md): ТЗ 15 рабочих мест; переиспользование WMS/TMS, состояния, права и приёмка.
- [requirements/retailcase_ui_quality_tz.md](../requirements/retailcase_ui_quality_tz.md): два независимых прохода, осмотр, вес и допуск по версии состава.
- [requirements/retailcase_ui_reachtruck_tz.md](../requirements/retailcase_ui_reachtruck_tz.md): быстрый одноэкранный ТСД водителя ричтрака.
- [requirements/retailcase_ui_reachtruck_dispatch_tz.md](../requirements/retailcase_ui_reachtruck_dispatch_tz.md): диспетчер ричтраков, очередность задач, ресурсы и безопасное переназначение.
- [roadmap/retailcase_ui_subsprints.md](../roadmap/retailcase_ui_subsprints.md): 23 законченных функциональных подспринта; A1/A2/A2.Q/A3 отдельно, ERP-интеграция первой.
- [Галерея и 25 рисунков](../../wiki-raw/retailcase_ui_20260915/README.md): 15 рабочих мест, варианты А/Б, offline QA; не внедрённые экраны.
- [requirements/retailcase_gap_analysis_20260915.md](../requirements/retailcase_gap_analysis_20260915.md): анализ актуального ТЗ 1.3 / XML 1.1.0 и локального кода, GAP и противоречия требований.
- [architecture/retailcase_minimal_extension.md](../architecture/retailcase_minimal_extension.md): минимальное расширение TMS/WMS без замены ядра, решение по сущностям и транзакциям.
- [roadmap/retailcase_architecture_sprints.md](../roadmap/retailcase_architecture_sprints.md): отдельные архитектурные инкременты A1/A2/A2.Q/A3 и критерии приёмки.
- [roadmap/retailcase_functional_sprints.md](../roadmap/retailcase_functional_sprints.md): функциональные этапы F1–F7 со ссылкой на 23 подспринта, AT-01…36 и пилот.
- F1 функционального плана начинается с двустороннего XML API ERP↔TMS: адреса/артикулы и OrderManifest на входе; статусы сборки, межскладского перемещения, пути и приёмки магазина — на выходе.
- [sources/retailcase_20260915.md](../sources/retailcase_20260915.md): новые документы Drive, снимок рабочего дерева, свежие offline-проверки и ограничения доказательств.

Start here for a fresh session:

- [overview.md](../overview.md): project map, current focus, and boundaries
- [repositories/index.md](../repositories/index.md): target GitHub repository and four-subrepository model
- [branches/index.md](../branches/index.md): four logical branches of the project
- [runbooks/project_onramp.md](../runbooks/project_onramp.md): first-5-minutes orientation
- [sources/index.md](../sources/index.md): raw source catalog

## Logical Branches

- [branches/01_oracle_plsql_core.md](../branches/01_oracle_plsql_core.md): Oracle schema, PL/SQL procedures, tables, functions, and core business rules
- [branches/02_csharp_desktop_client.md](../branches/02_csharp_desktop_client.md): main C# WinForms operator application
- [branches/03_terminal_contour.md](../branches/03_terminal_contour.md): handheld/scanner terminal client, terminal server, and operation confirmation flow
- [branches/04_external_integrations.md](../branches/04_external_integrations.md): `SUPERMAG` / `Sfera`, imports, exports, and staging

## Subprojects

- [subprojects/windowsapplication2.md](../subprojects/windowsapplication2.md): legacy WinForms WMS/TMS desktop application
- [subprojects/oracle_schema.md](../subprojects/oracle_schema.md): reconstructed Oracle schema and deployment scripts
- [subprojects/wms_terminal_web.md](../subprojects/wms_terminal_web.md): modern Web/PWA terminal application replacing the legacy terminal OS client
- [subprojects/tms2_current_status.md](../subprojects/tms2_current_status.md): reboot anchor for the active TMS-2 workstream, Sprint hardening status through Sprint 95, Wave 3 Business Factor Trace, release gates, v2 handoff commit `446903b`, routing provider evidence, MAP/VRP test geocode fixture, planner auto-plan fix, risks, and next pilot steps

## Architecture

- [architecture/retailcase_modular_development_contract.md](../architecture/retailcase_modular_development_contract.md): договор модульности; действующий режим ресурсов/проверок определяется последним поручением владельца.

- [architecture/tms2_system_map.md](../architecture/tms2_system_map.md): architecture map for the active TMS-2 transport replacement, covering frontend, FastAPI, service layer, Oracle objects, blocks, API contracts, and verification paths
- [architecture/wms_mes_traceability_edd.md](../architecture/wms_mes_traceability_edd.md): engineering design document for the WMS+MES+Traceability target architecture with Mercury and Honest Sign separation
- [architecture/wave_resource_execution_evidence_architecture.md](../architecture/wave_resource_execution_evidence_architecture.md): accepted architecture decision that wave is the central operational object, people/equipment tasks use the resource model, TSD facts synchronize through warehouse-task sync or case-pick events, and every business process requires evidence-driven testing

## Database Mirror

- [database/retailcase_ns00_fixture.md](../database/retailcase_ns00_fixture.md): 22 owned строки NS00 в RABAEV, без DDL.
- [database/retailcase_track_trace_requirements.md](../database/retailcase_track_trace_requirements.md): договор данных маркировки редакции 57 в RABAEV.

- [database/index.md](../database/index.md): local wiki mirror of the Oracle `RABAEV` schema and change discipline
- [database/oracle_change_protocol.md](../database/oracle_change_protocol.md): required workflow for Oracle structure changes
- [database/tms2_oracle_contract.md](../database/tms2_oracle_contract.md): Oracle contract for TMS-2, including real legacy table columns, DML function call rules, schema drift notes, and migration status
- [database/feed_factory_traceability_schema.md](../database/feed_factory_traceability_schema.md): schema mirror for feed-factory traceability, Mercury/CRPT lifecycle, API audit/replay, wave stock movement ledger, regulatory journal migrations, warehouse topology 038/039, linear pick-route invariant migration 040, warehouse map canvas/slot migration 041, and Oracle publish invariant package 042
- [../db/clean_install/README.md](../../db/clean_install/README.md): from-zero Oracle install kit with separate structure, settings, fixtures, profiles, and verification scripts for isolated `RABAEV` installations

## Incidents

- [incidents/tms2_known_failures.md](../incidents/tms2_known_failures.md): known TMS-2 failure modes and fixes, including Oracle DML function calls, billed-trip protection, planner schema drift, Gantt schema drift, and VRP partial success

## Concepts

- [concepts/external_integration_supermag.md](../concepts/external_integration_supermag.md): `SUPERMAG` / `Sfera` as external ERP source
- [concepts/legacy_rights_model.md](../concepts/legacy_rights_model.md): legacy `RUSERS` / `USER_GROUP` / `RIGHTS` model used by admin pages
- [concepts/oracle_environment.md](../concepts/oracle_environment.md): recommended Oracle environment and schema separation
- [concepts/api_method_library.md](../concepts/api_method_library.md): maintained `api-med` catalog of API methods, permissions, parameters, side effects, readiness checks, and verification, including the warehouse-map state API
- [concepts/regulatory_adapter_audit.md](../concepts/regulatory_adapter_audit.md): audit/replay rules for real Mercury and Honest Sign adapters
- [concepts/tserver_api_registry.md](../concepts/tserver_api_registry.md): legacy terminal API commands and `CALL_SPF` procedure registry
- [concepts/ui_interaction_rules.md](../concepts/ui_interaction_rules.md): общие правила всплывающих подсказок, контекстной help-системы и визуального обозначения будущих/заглушечных UI-элементов
- [concepts/wiki_operating_model.md](../concepts/wiki_operating_model.md): how this repository uses the Karpathy wiki pattern

## Runbooks

- [runbooks/retailcase_agent_tooling.md](../runbooks/retailcase_agent_tooling.md): проектные MCP и skills; новые подключения не требуются.

- [../scripts/README.md](../../scripts/README.md): local Windows launch scripts for WMS API, admin frontend/raw UI reference, and terminal Web/PWA app
- [runbooks/tms2_local_verification.md](../runbooks/tms2_local_verification.md): local verification runbook for TMS-2 ports, Oracle env, migrations, functional tests by block, skip interpretation, encoding checks, and frontend smoke
- [runbooks/tms2_release_acceptance.md](../runbooks/tms2_release_acceptance.md): final TMS-2 release acceptance runbook, including the 446/234 final full gate, Wave 3 factor trace, v2 neighbor acceptance through the final handoff pass `130 passed, 7 skipped`, Sprint 8 mutating apply evidence, live routing smoke, 2000-row frontend NFR smoke, and fresh slow SQL decision
- [runbooks/tms2_prod_migration_checklist.md](../runbooks/tms2_prod_migration_checklist.md): production migration checklist for TMS-2, including the corrected prod migration sequence, prod exclusions for dev fixtures, applied-object checks, rights checks, rollback notes, and post-gate slow SQL review
- [runbooks/tms2_pilot_checklist.md](../runbooks/tms2_pilot_checklist.md): 5-day parallel-operation pilot checklist for transport dispatch, MAP/VRP, billing, Day 0 release freeze, daily reconciliation, incident logging, stop criteria, and success criteria
- [runbooks/tms_mcp_servers.md](../runbooks/tms_mcp_servers.md): local MCP servers for wiki recall, repository search, Oracle schema metadata, Playwright, and Docker/routing checks
- [runbooks/slow_sql_review.md](../runbooks/slow_sql_review.md): mandatory slow SQL/SKV review after every meaningful case, load test, release gate, and pilot rehearsal, with required remediation decisions
- [runbooks/create_api_server.md](../runbooks/create_api_server.md): recommended API server stack and migration plan from `Tserver`
- [runbooks/evidence_driven_process_testing.md](../runbooks/evidence_driven_process_testing.md): обязательный runbook для evidence-driven приемки бизнес-процессов: сценарий, модель данных, runner, Oracle/API инварианты, ARM/TSD screenshots, reports
- [../api/wms_api_server/README.md](../../api/wms_api_server/README.md): first Python FastAPI implementation for WMS/TMS API and `Tserver` compatibility
- [runbooks/warehouse_task_domain_sync_operations.md](../runbooks/warehouse_task_domain_sync_operations.md): эксплуатационная инструкция для мониторинга `RRL_WAREHOUSE_TASK_SYNC`, разбора ошибок и retry
- [runbooks/db_app_compatibility_check_2026_05_11.md](../runbooks/db_app_compatibility_check_2026_05_11.md): compatibility check for Oracle, C# desktop client, and `Tserver`
- [runbooks/oracle_recovery_2026_05_11.md](../runbooks/oracle_recovery_2026_05_11.md): Oracle VM recovery context and restore point after flashback repair
- [runbooks/project_onramp.md](../runbooks/project_onramp.md): how to orient before changing code or docs

## Roadmap

- [roadmap/strategic_development_plan.md](../roadmap/strategic_development_plan.md): strategic plan for DB compatibility, API boundary, queueing, Android terminals, and regulated integrations
- [roadmap/tactical_implementation_plan.md](../roadmap/tactical_implementation_plan.md): tactical execution plan for feed-factory traceability, API, file exchange, and adapters
- [roadmap/wms_mes_traceability_strategic_plan.md](../roadmap/wms_mes_traceability_strategic_plan.md): approved strategic plan for WMS+MES+Traceability implementation
- [roadmap/wms_mes_traceability_tactical_plan.md](../roadmap/wms_mes_traceability_tactical_plan.md): tactical sprint plan for traceability spine, outbox, adapters, admin UI, MES, shipment, and recall
- [roadmap/picking_wave_implementation_plan.md](../roadmap/picking_wave_implementation_plan.md): strategic and tactical implementation plan for picking planning, wave picking, reservations, admin UI, terminal execution, and WMS bridge
- [roadmap/current_checkpoint_2026_05_18.md](../roadmap/current_checkpoint_2026_05_18.md): current reboot checkpoint, tactical plan, strategic plan, warehouse-task implementation, wave Minimax auto-trigger, shelf-life source selection, and wave loading-zone staging/UI status
- [roadmap/current_checkpoint_2026_05_20.md](../roadmap/current_checkpoint_2026_05_20.md): recovered crash checkpoint for the warehouse digital twin, latest model-only evidence, React admin replay, and next stabilization steps
- [roadmap/wave_replenishment_queue_change_plan_2026_05_19.md](../roadmap/wave_replenishment_queue_change_plan_2026_05_19.md): strategic and tactical change file for queued same-SKU wave replenishment, dynamic/generic pick-face release, readiness API, tests, risks, and next implementation steps

## Requirements

- [requirements/bom_production_block_tz.md](../requirements/bom_production_block_tz.md): Russian technical assignment for MES BOM/recipe management, primary recipes, validity periods, and production-order integration
- [requirements/case_pick_tsd_tz.md](../requirements/case_pick_tsd_tz.md): Russian technical assignment for picker TSD case picking of customer pallets, ARM monitoring/dispatch, wave-launch SSCC generation, address-level `PALLET_TYPE`, pick routes, scan settings, shorts/write-offs, inventory tasks, offline mode, and control workflow
- [requirements/case_pick_wave_load_test_tz.md](../requirements/case_pick_wave_load_test_tz.md): Russian technical assignment for load/model testing of a case-pick wave: 7 clients, 78 customer pallets, clean warehouse fixture, pick-face replenishment, picking stages, runtime evidence, screenshots, and presentation artifacts
- [requirements/feed_factory_mercury_crpt_tz.md](../requirements/feed_factory_mercury_crpt_tz.md): Russian technical assignment for feed-factory production, raw-material usage, Mercury, Honest Sign, aggregation, and shipment modes
- [requirements/finished_goods_admin_tz.md](../requirements/finished_goods_admin_tz.md): Russian technical assignment for the finished-goods admin page: SKU settings, warehouses, production batches, pallets, SSCC, and stock
- [requirements/large_warehouse_minute_simulation_tz.md](../requirements/large_warehouse_minute_simulation_tz.md): Russian technical assignment and first model-only implementation note for a 12-hour real-warehouse digital-twin load test with 50 clients, 10 waves, 1000 SKU, 1500 pick faces, urgent-only dynamic/overflow pick-face cells, minute-by-minute movement simulation, collision detection, resource shortage analysis, screenshots, and warehouse animation page
- [requirements/large_warehouse_map_drawing_tz.md](../requirements/large_warehouse_map_drawing_tz.md): Russian technical assignment for an Excel-like lightweight 2D editor for drawing large warehouse maps at `35 x 90 x 6` scale, assigning cell roles, zooming/panning, multi-area bulk selection, level-persistent selection, format painter, context help, fractional pick-face split presets with visual split lines, and publishing drafts into topology
- [requirements/large_warehouse_map_real_warehouse_binding_tz.md](../requirements/large_warehouse_map_real_warehouse_binding_tz.md): Russian technical assignment for binding the large warehouse map editor to real Oracle warehouses; now includes DB-backed canvas/camera APIs, empty-camera unavailable default, bootstrap canvas from existing DB cells, selected-area standard layouts, sticky sidebar format painter, audited detailed context help plus a module instruction modal, explicit pick/storage fractional slot preset controls with Canvas split-line rendering, side-flyout context menu variants including full-size pick/storage and pick `2/1..3/4` plus custom `V/G`, storage-slot capacity/order editing, preview-only topology projection, optimistic draft diff/locking for cells plus canvas metadata/objects/passages/links, draft pick-route order preview, route validation/publish draft evidence, Sprint 18 performance/evidence hardening, Sprint 19 Oracle publish invariant pack, Sprint 20 DB-backed save/load API switch, Sprint 21 projection-to-topology persistence, Sprint 22 route rows to Oracle pick route, Sprint 23 Oracle publish action, Sprint 24 UI publish controls with visual evidence, Sprint 25 published warehouse reload, and Sprint 26 final acceptance checkpoint
- [requirements/large_warehouse_map_functional_testing_tz.md](../requirements/large_warehouse_map_functional_testing_tz.md): Russian technical assignment for functional acceptance testing of the large warehouse map on an existing Oracle warehouse without canvas: create canvas, two cameras, up to 10 gates, about 1500 storage cells per camera, pick cells across 6 levels, mixed route patterns in one camera, save/publish/reload evidence, full UI label/help audit, functional completeness conclusions, usability conclusions, and the follow-up TZ for screen/menu optimization.
- [requirements/large_warehouse_map_functional_testing_result_2026_05_23.md](../requirements/large_warehouse_map_functional_testing_result_2026_05_23.md): functional audit result for the large warehouse map: Playwright UI test passes 19/19 checks, fixes visual pick-address labels on canvas and preserves selection after route draft rebuild, with a recommendation to run full publish/reload only on a controlled Oracle fixture.
- [requirements/large_warehouse_map_publish_reload_fixture_result_2026_05_23.md](../requirements/large_warehouse_map_publish_reload_fixture_result_2026_05_23.md): acceptance result for the `Publish/Reload Fixture` sprint: isolated `WARE_ID=0` publishes `canvas=35`, `topology=19`, and `route=117`, then reloads warehouse state with 19/19 PASS checks, 144 route rows, and zero storage/non-pick route rows.
- [requirements/large_warehouse_map_projection_bulk_save_fix_2026_05_23.md](../requirements/large_warehouse_map_projection_bulk_save_fix_2026_05_23.md): architecture fix result for warehouse-map projection persistence: replacing fake per-row `execute_many` and per-cell sequence calls with real `executemany` plus batched sequence allocation reduced a 5042-cell topology save from about 762 seconds to 3.9 seconds, with two-camera publish/reload evidence.
- [requirements/large_warehouse_map_two_camera_scale_result_2026_05_23.md](../requirements/large_warehouse_map_two_camera_scale_result_2026_05_23.md): two-camera scale acceptance result after the bulk-save architecture fix: `3000` storage cells, `1202` pick cells, `5042` topology cells, two cameras, one camera link, route publish/reload, and `projection/save-to-topology = 2002 ms`.
- [requirements/large_warehouse_map_fixture_cleanup_idempotency_result_2026_05_23.md](../requirements/large_warehouse_map_fixture_cleanup_idempotency_result_2026_05_23.md): fixture cleanup and idempotent retry result for warehouse-map acceptance: archive canvas API, `FX-/TC-` cleanup tool, repeat two-camera scale run, and HTTP retry returning existing topology/route instead of creating duplicates.
- [requirements/large_warehouse_map_operation_idempotency_result_2026_05_23.md](../requirements/large_warehouse_map_operation_idempotency_result_2026_05_23.md): production idempotency-key result for warehouse-map canvas save, topology projection, route save, and publish; migration `043` adds Oracle columns/indexes, API smoke proves repeated requests return the same ids, and the two-camera 5042-cell scale fixture still passes.
- [requirements/large_warehouse_map_publish_reload_ux_result_2026_05_23.md](../requirements/large_warehouse_map_publish_reload_ux_result_2026_05_23.md): publish/reload UX polish result for the large warehouse map: ribbon and left panel now expose the full Canvas DB -> Topology DB -> Route DB -> Publish Oracle -> Reload workflow, show operation idempotency keys/statuses, and pass visual smoke plus backend idempotency regression.
- [requirements/large_warehouse_map_full_ui_functional_acceptance_result_2026_05_23.md](../requirements/large_warehouse_map_full_ui_functional_acceptance_result_2026_05_23.md): full UI functional acceptance result for the large warehouse map on a non-zero Oracle warehouse: excludes `WARE_ID=0`, passes 19/19 UI audit checks, publishes/reloads a two-camera 5042-cell fixture on `WARE_ID=1`, verifies idempotency retries, and marks the next strategic gate as final model invariant review.
- [requirements/large_warehouse_map_final_model_invariant_review_2026_05_23.md](../requirements/large_warehouse_map_final_model_invariant_review_2026_05_23.md): final model invariant review for the large warehouse map: confirms canvas remains a planning/layout object, published topology/route are the operational source, storage slots stay out of pick routes, explicit publish is validated by Oracle, idempotency keys protect retries, and the next strategic gate is release checkpoint and cleanup.
- [requirements/large_warehouse_map_release_checkpoint_cleanup_2026_05_23.md](../requirements/large_warehouse_map_release_checkpoint_cleanup_2026_05_23.md): release checkpoint and cleanup result for the large warehouse map: identifies warehouse-map commit scope versus unrelated dirty worktree material, documents fixture production guards, tightens API method documentation, and marks the release checkpoint accepted pending explicit commit scope review.
- [requirements/large_warehouse_map_current_status.md](../requirements/large_warehouse_map_current_status.md): reboot anchor for the active LargeWarehouseMap / `warehouse-map` workstream: current scope, `3000`-only port rule, half-day green evidence, known remaining gaps, and fresh-session checklist.
- [requirements/large_warehouse_map_zero_warehouse_ban_2026_05_23.md](../requirements/large_warehouse_map_zero_warehouse_ban_2026_05_23.md): zero warehouse ban result for the large warehouse map: deletes live `RRL_WARES.ID=0` and related warehouse-map/topology/route fixture rows, adds Oracle positive-id constraints, updates API validation to reject `ware_id=0`, and records live apply/verify/smoke evidence for migration `044`.
- [requirements/large_warehouse_map_release_scope_review_2026_05_23.md](../requirements/large_warehouse_map_release_scope_review_2026_05_23.md): release scope review for the large warehouse map: names the warehouse-map files to include, unrelated worktree files to exclude, the minimal final release gate, and the next strategic move toward commit/PR packaging.
- [requirements/large_warehouse_map_excel_canvas_actions_tz.md](../requirements/large_warehouse_map_excel_canvas_actions_tz.md): Russian technical assignment for expanding warehouse map canvas actions by Excel analogy: every working function must have a left-menu action and a context-menu tree duplicate, `Сохранить канвас` must exist in both places, Excel functions are mapped to needed canvas-map analogs with proposed icons and priorities, the first implementation checkpoint adds an Excel-like `Главная` ribbon as a third fast entry point, `Excel Actions 2` adds parity for editing/filters/navigation/validation, `Excel Actions 3` compacts the ribbon/context menu while adding template/layout and multi-pattern route actions, and the 2026-05-26 fixes scope `Регулярный склад` and fractional pick/storage generation to the active selection when one exists.
- [requirements/large_warehouse_map_ui_test_plan_2026_05_26.md](../requirements/large_warehouse_map_ui_test_plan_2026_05_26.md): UI regression and end-to-end acceptance checklist for warehouse-map drawing, stale-state warehouse switching, selection-scoped templates, draft/canvas save, route build, Oracle publish, reload, negative cases, and the 2026-05-27 half-day green run.
- [requirements/mes_production_completion_prompt.md](../requirements/mes_production_completion_prompt.md): prompt for implementing MES production completion through a movement journal and controlled legacy WMS bridge
- [requirements/mes_raw_shortage_replenishment_tz.md](../requirements/mes_raw_shortage_replenishment_tz.md): Russian technical assignment for BOM raw-material shortage calculation and transfer tasks from raw warehouse to production
- [requirements/modern_terminal_app_tz.md](../requirements/modern_terminal_app_tz.md): Russian technical assignment for the modern Web/PWA terminal app replacing the legacy terminal OS client
- [requirements/tms2_planner_explain_panel_tz.md](../requirements/tms2_planner_explain_panel_tz.md): technical assignment for the TMS-2 MAP/VRP calculation explanation side drawer with metrics, solver parameters, calculation steps, vehicle utilization, warnings, backend explain contract, and acceptance tests
- [requirements/tms2_acceptance_matrix.md](../requirements/tms2_acceptance_matrix.md): strategic acceptance matrix for TMS-2 Sprint 1-95, mapping user flows to API, Oracle contracts, tests, infrastructure/NFR decisions, gaps, and release gates
- [requirements/picking_planning_tz.md](../requirements/picking_planning_tz.md): Russian technical assignment for customer-order picking planning, reservations, customer rules, route/dock context, and shipment-part splitting
- [requirements/raw_material_admin_tz.md](../requirements/raw_material_admin_tz.md): Russian technical assignment for the raw-material admin page: raw SKU settings, raw warehouses, and stock by selected warehouses
- [requirements/resource_management_module_tz.md](../requirements/resource_management_module_tz.md): Russian technical assignment for a separate resource-management module covering reachtrucks, KIKA, forklifts, trolleys, pickers, loading teams, cooking, packing, shifts, sessions, dispatch, and plan-fact Gantt
- [requirements/warehouse_resource_planning_tz.md](../requirements/warehouse_resource_planning_tz.md): Russian technical assignment for warehouse resources, reachtruck/KIKA equipment, driver shift login, task dispatch, planned Gantt, factual Gantt, and plan-fact load analysis
- [requirements/warehouse_tasks_reachtruck_tz.md](../requirements/warehouse_tasks_reachtruck_tz.md): Russian technical assignment for common warehouse tasks, reachtruck-driver execution, wave pick-face replenishment, and full-pallet loading-zone staging
- [requirements/warehouse_task_domain_sync_tz.md](../requirements/warehouse_task_domain_sync_tz.md): Russian technical assignment for synchronizing completed warehouse-task facts back into MES, wave, picking, and shipment domains; current runtime covers wave replenishment, wave full-pallet staging, MES raw supply, and finished-goods placement
- [requirements/warehouse_topology_pick_route_tz.md](../requirements/warehouse_topology_pick_route_tz.md): Russian technical assignment and implementation checkpoint for warehouse topology and pick-route administration as rare versioned master-data processes, with graphical generation, route publishing, recommendations, gate-distance matrix, dock/staging separation, split pick-face slots, stable route-area selection UX, test-ready admin UI, PL/SQL/API contracts, and digital-twin integration
- [requirements/warehouse_topology_acceptance_tz_2026_05_22.md](../requirements/warehouse_topology_acceptance_tz_2026_05_22.md): tactical May 22 acceptance scope for topology admin, warehouse topology API, Oracle route invariants, and visual evidence screenshots
- [requirements/wave_case_pick_replenishment_tz.md](../requirements/wave_case_pick_replenishment_tz.md): Russian technical assignment and current runtime checkpoint for replenishing pick-face cells under wave case picking, including `MINIMAX`, immediate replenishment, queued same-SKU drops, urgent-only dynamic/generic pick-face release, layout optimization, pallet/half-pallet, and fill-to-volume strategies
- [requirements/wave_client_e2e_acceptance_scenario.md](../requirements/wave_client_e2e_acceptance_scenario.md): Russian client acceptance scenario for wave creation, pick-face replenishment, direct rack/full-pallet picking, case picking, readiness, free/physical stock evidence, TSD video fixation, negative checks, and automation
- [requirements/wave_picking_tz.md](../requirements/wave_picking_tz.md): Russian technical assignment for wave picking, hard reservations, pick-face replenishment, launch dialog, and wave execution
- [requirements/wave_picking_admin_tz.md](../requirements/wave_picking_admin_tz.md): Russian technical assignment for the wave-picking admin page, launch dialog, rights, monitoring, and operational controls
- [requirements/wave_user_scenarios_functional_tz.md](../requirements/wave_user_scenarios_functional_tz.md): Russian technical assignment for functional user-scenario checks: assembling a wave from orders, replenishing pick faces, direct rack/full-pallet picking, case picking, 10x replenishment collision, and truck shipment readiness/dispatch

## Control Files

- [WIKI_SCHEMA.md](../WIKI_SCHEMA.md): root wiki schema and maintenance rules
- [log.md](../log.md): append-only wiki maintenance log
- [../AGENTS.md](../../AGENTS.md): agent-facing onramp for future sessions

- [Задания локальной Qwen по NI01](../../задания%20на%20проведение%20тестов/NI01/README.md): восемь пакетов; подготовлены без запуска тестов.
- [NI02 — импорт заказов магазинов SAP](../runbooks/retailcase_ni02_store_orders.md): in_progress, неизменный заказ/календарь/позднее ожидание; migration 008 в RABAEV.

- [database/retailcase_stock_posting_article_20261008.md](../database/retailcase_stock_posting_article_20261008.md): версия упаковки ARTICULS и прекращение автоматического движения при переназначении ячейки.

- [database/retailcase_stock_posting_native_quality_20261008.md](../database/retailcase_stock_posting_native_quality_20261008.md): 180–196: native QC/отгрузка, durable терминал, measured EA inventory, pending-short guard и FULL_PALLET bridge; PREPARED, cutover открыт.

- [database/retailcase_ni032_shifts_admission_20261009.md](../database/retailcase_ni032_shifts_admission_20261009.md):025–030 APPLIED; MAIN/DUTY, versioned SHORT/CCTV, ABC B/batch admission, durable whole-pallet remaining demand, idle worker confirmed. NI03.2 in_progress.

- [database/retailcase_ni033_physical_fulfillment_20261009.md](../database/retailcase_ni033_physical_fulfillment_20261009.md):031 APPLIED; physical CASE→existing ST.PICKED/provenance, atomic return reset, exact order progress API/UI. NI03.3 started; NI03.2 residual retained.

- [Серийные весовые коробки](../database/retailcase_ni042_weight_box_capture_20261011.md):179 native GS1 netKG/current SKU flag/existing physical registry/P9.8/unit1/replay/no duplicate birth; SAP/CASE next.

- [SAP-приёмка весовой коробки и ключ задания](../database/retailcase_ni042_weight_box_sap_20261011.md):180 actual XML→P9.8/unit1/replay;181 fixes global SAP PUTAWAY collision, non-SAP uniqueness preserved.

- [Весовая коробка в CASE](../database/retailcase_ni042_weighted_case_20261011.md):182 server-derived9.8KG/existing CASE single writer/native own HARD/TSD durable retry; exact box capacity next.

- [Брутто, объём и маркированная весовая коробка](../database/retailcase_ni042_box_dimensions_20261011.md):183 existing physical metadata, exact4.25/4.5 and marked CASE9.8/gross10.1/current QR/composition/native cleanup; hardware/external ACK separate.

- [Вместимость весовых коробок](../database/retailcase_ni042_box_capacity_20261011.md):184 actual physical volume/current bounded conservative KG budget, original replenishment19.6→CASE9.8 without BOX conversion; unknown dimensions refused.

- [QC по фактическому брутто коробок](../database/retailcase_ni051_physical_box_mass_20261011.md):185 native expected10.1 for actual net9.8/current independent WEIGHT2/replay; partial-box mass refused, SCAN still required.

- [Общий пакет весов](../database/retailcase_ni042_scale_packet_20261011.md):186 original store archive uses one validator/stable samples/UTC/zero/replay unchanged; [складской пост](../database/retailcase_ni042_warehouse_scale_design_20261011.md) next.

- [Складской архив весового поста](../database/retailcase_ni042_warehouse_scale_20261011.md):187 addressed device/current dedicated sender/CASE version/stable10.1/immutable replay/no P-H; native consumption next.

- [Показание весов в проводке CASE](../database/retailcase_ni042_scale_use_20261011.md):188 once-only GROSS proof/root transaction/NET9.8/exact replay; loose NET next.

- [Точный NET-отбор на весах](../database/retailcase_ni042_scale_net_20261011.md):189 current unmarkedKG/native root/TSD,190 rollback+concurrent one winner; remaining demand preserved.

- [Допуск массы исходного заказа](../database/retailcase_ni042_order_weight_policy_20261011.md):191 SKU default15/exact versioned setting/original10 vs picked9.6/current preview; explicit decision next.

- [Завершение по допуску массы: разработка](../database/retailcase_ni042_weight_decision_design_20261011.md):192 existing short approval/native snapshots/current planned order resources; current demand waiver next.

- [Явное завершение по допуску массы](../database/retailcase_ni042_weight_decision_20261011.md):192 existing native short owner/exact9.6/10/signed approval/H release/rollback+replay; demand waiver next.

- [Потребность после принятого отклонения: разработка](../database/retailcase_ni042_weight_demand_design_20261011.md):193 pure current waiver/return-aware original pool math; no stock write.

- [Потребность после принятого отклонения](../database/retailcase_ni042_weight_demand_20261011.md):193 current.4 waiver/original10 preserved/return reopens10/no stock write.

- [Восстановление публичных DTO inventory](../incidents/retailcase_inventory_contract_overwrite_20261011.md):192 mistaken facade overwrite repaired before193 stock case; API exports/quality confirmed.

- [Выбор последней целой весовой коробки: разработка](../database/retailcase_ni042_weight_box_planning_design_20261011.md):194 actual candidates/current order source/native shared plan scope; admission/apply next.

- [Предварительный выбор целой коробки](../database/retailcase_ni042_weight_box_planning_20261011.md):194 actual8/12 vs original10/default15/current source/ARM table; explicit approval/apply next.

- [Согласованный выбор последней коробки: разработка](../database/retailcase_ni042_weight_box_choice_design_20261011.md):195 immutable current selected box/role-separated approval/source replay/no stock; existing plan use next.

- [Согласование последней целой коробки](../database/retailcase_ni042_weight_box_choice_20261011.md):195 approval-only exact8-vs10/default15 unchanged/immutable source/replay/cancel/no P-H; existing plan use next.

- [Выбранная коробка в существующем плане: разработка](../database/retailcase_ni042_weight_choice_plan_design_20261011.md):196 old plan/SOFT exact target/source/atomic private binding/original request retained.

- [Коробка в существующем плане](../database/retailcase_ni042_weight_choice_plan_20261011.md):196 original10/planned8/SOFT8/atomic rollback/concurrent one plan/cancel history; exact HARD pin next.

- [Проект закрепления коробки](../database/retailcase_ni042_weight_unit_pin_design_20261011.md):197 existing native HARD owners/exact physical key/no new writer.

- [Точный резерв весовой коробки](../database/retailcase_ni042_weight_unit_pin_20261011.md):197 original10/actual8or12/exact HARD key/full replenishment/CASE pick/replay/native return; demand accounting next.

- [Проект потребности после целой коробки](../database/retailcase_ni042_weight_choice_demand_design_20261011.md):198 pure pending vs fulfilled deviation/current original order/return reopening.

- [Потребность после целой коробки](../database/retailcase_ni042_weight_choice_demand_20261011.md):198 pending separately/actual8 waiver2/actual12 original10/return reopens10/no stock rewrite.

- [Проект pick-by-line](../database/retailcase_ni042_direct_receiving_design_20261011.md):199 existing DIRECT source/existing plan/HARD/CASE/unstarted putaway ownership; residual200.

- [Проект размещения DIRECT-остатка](../database/retailcase_ni042_direct_residual_design_20261011.md):200 existing replan/current exact remainder/native handoff proof/no active allocations.

- [Прямой отбор из SAP приёмки](../database/retailcase_ni042_direct_receiving_20261011.md):199 actual20→12/8/no replenishment/atomic putaway handoff/rollback; [остаток на размещение](../database/retailcase_ni042_direct_residual_20261011.md):200 original20/actualCASE12/storage8/outbox8.

- [Маркированный pick-by-line](../database/retailcase_ni042_marked_direct_20261011.md):201 realSAP physical12/codes24/5+7/exact QR/EAN409/no replenishment/no govACK; categoryB existing029 reused.

- [Проект финального веса малой коробки](../database/retailcase_ni042_small_final_weight_design_20261011.md):202 per-type mandatory child QC/current metadata owner; final scale archive next.

- [Финальный вес малой коробки](../database/retailcase_ni042_small_final_weight_20261011.md):202 child type requires current WEIGHT under warehouse NONE/gross.400/tare.100/net.300/exact DTO/version; standard box label and addressed capture next.

- [SSCC малой коробки](../database/retailcase_ni042_case_sscc_20261011.md):203 shared allocator/immutable original CP/GS1 print/scan confirmation/native admission/currentCASE6; addressed final scales next.

- [Архив финального веса коробки](../database/retailcase_ni042_final_scale_20261011.md):204 existing archive/current SSCC/empty.100+final.400/net.300/current composition/first-fill tare gate;205 native QC once-use next.

- [Финальное показание в исходном QC](../database/retailcase_ni042_final_qc_20261011.md):205 native once-use/rollback/concurrent one winner/current WARE before replay/actual.400−.100=.300/TEST visible/TSD+controller UI; no P-H.

- NI04.2/205: компактная100×70мм SSCC-этикетка CASE использует исходный генератор; сохранёнA6 приёмки, DPI203/300/600, физическая печать в пилоте.

- [Контроль коробки внутри матрёшки](../database/retailcase_ni042_small_hu_20261011.md):206 own v3 cargo proof retained through pack/move/unpack; unweighed child blocked and real7→6 restoration revokes; ordinaryv2 preserved.

- [Масса коробки в рейсе и магазине](../database/retailcase_ni042_case_mass_20261011.md):207 actual6EA/.400+.outer1=1.4/native load rollback/replay/frozen CASE identity and original store tolerance.

- [Приёмка малого измеренного CASE магазином](../database/retailcase_ni053_small_weight_receipt_20261011.md):208 existing weight/photo flow accepts6 at1.2/source1.4/tolerance.2 with three views/nonadmin/replay; UI frozen box mass.

- [Исполнение выданного линейного маршрута](../database/retailcase_ni042_route_sequence_20261011.md):209 native min unfinished rank/backtrack gate, actual two cells/issued order stable/TSD resumes; no second planner.

- [Этап укладки выданного CASE](../database/retailcase_ni042_stack_stage_20261011.md):210 versioned SKU BASE/MAIN/TOP frozen at issue; correct route picks, inverse route refused before stock; existing CASE owner.

- [Маркированная малая коробка в паллете](../database/retailcase_ni042_marked_small_20261011.md):211 actual7 goods/14 codes vs source5/10, own QR+weight retained/native HU load/departure; no fabricated legal aggregation.

- [Выгрузка самостоятельного места до выезда](../database/retailcase_ni052_unload_20261011.md):212 same native root/original -6/new +6/P6H6, restored HARD and fresh QC; history retained, matryoshka/marked extension next.

- [Возврат исходных кодов при выгрузке](../database/retailcase_ni052_unload_units_20261011.md):213 exact original7 units/14 codes/P7H7, UNIT locks and fingerprint, native cleanup; whole HU next.

- [Выгрузка двухуровневой матрёшки](../database/retailcase_ni052_unload_hu_20261011.md):214 outer+inner+CASE7/14 codes/P7H7, new links2/old links2 retained/native rollback/concurrency; slots/FULLPAL/tare custody next.

- [Выгрузка в фактически занятый слот](../database/retailcase_ni052_unload_slot_20261011.md):215 original measured2.45kg/.125m3/OCCUPIED214/native DONE931/SYNCED, same HARD slot and late capacity rollback.

- [Возврат тары исходной погрузки](../database/retailcase_ni063_load_recovery_20261011.md):216 original transfer/accepted vehicle return/new HELD1, current scope and immutable lineage; same whole slotted unload7/14codes passed.

- [Разгрузка целой паллеты](../database/retailcase_ni052_unload_fullpal_20261011.md):217 same original binding/task/UID, native -3/+3/P3H3, current FF version and fresh QC before reload.

- [Повторная загрузка паллеты](../database/retailcase_ni052_fullpal_reload_20261011.md):218 fresh item QC3 before same original task/UID reload; native-3/P0H0/replay; direct links to existing QC.

- [Отмена непринятой передачи тары](../database/retailcase_ni063_offer_cancel_20261011.md):219 immutable cancellation, same ACCEPT mutex/current scope/no balance change; original booked FULLPAL reoffer and actual acceptance.

- [Возврат тары HU и целой паллеты](../database/retailcase_ni063_hu_recovery_20261011.md):220 original driver→warehouse accepted1/new HELD original UID, same goods unload+3/P3H3; existing CASE proof preserved.

- [Повторная передача тары одной погрузки](../database/retailcase_ni063_recovery_lineage_20261011.md):221 two actual cycles/same LOADED source, bounded lineage/total tare1/native unload+3/P3H3/history retained.

- [Текущие слоты всех выгружаемых корней](../database/retailcase_ni052_unload_all_slots_20261011.md):222 current published topology for CASE/HU/FULLPAL; actual STOCK slot221/10kg1.5m³/DONE949/SYNCED/P3H3.

- [Погрузка освобождает исходный слот](../database/retailcase_ni052_single_slot_release_20261011.md):223 same existing SINGLE native-3/P0H0/slot221 free/rollback restores original occupancy949/task history retained.

- [Текущий склад самостоятельной погрузки](../database/retailcase_ni052_single_scope_20261011.md):224 current nonadmin own preview/load; foreign current warehouse read/new command/saved replay403, native-3 once.

- [План редакции12](../requirements/retailcase_delivery_v55/implementation_plan.md):217–224 actual fullpal/tare/current slots/warehouse scope; existing receiving pallet suggestions retained, next NI06.1 marked original source.

- [Маркированное основание межскладского плеча](../database/retailcase_ni061_marked_source_20261011.md):225 actual marked FULLPAL3/codes6/pick-QC-load-depart/original unit fingerprint/immutable plan manifest/no target stock.

- [Приёмка прежних маркированных единиц](../database/retailcase_ni061_marked_receive_20261011.md):226 original225->native targetP3H0/units3 codes6/same identity/version8/current scope/rollback/concurrent one winner.

- [Размещение маркированной межскладской паллеты](../database/retailcase_ni061_marked_placement_20261011.md):227 same original task953 DONE/SYNCED/receiving0/outbound3H0/same units3 codes6/version9/real resource session.

- [Маркированная паллета во втором плече](../database/retailcase_ni061_marked_onward_20261011.md):228 original ST641364/QC6/nativeLOAD-3/sameunits3codes6/ISSUED10/TT33543DEPARTED/no secondFF.

- [Уникальные QR при окончательной приёмке](../database/retailcase_ni053_marked_recipient_20261011.md):229 original marked two-leg order2030 finalaccepted3/unreceived0/sameunits3codes6/no goods/GovACK/current receiver/React scanner.

- [Сохранность обработчиков общего ядра](../architecture/retailcase_stock_dispatch_contract_20261011.md): генератор bundle отклоняет потерянные compile/execute вызовы установленных владельцев команд; текущая229 сборка сохранена локально.

- [Маркированные единицы в расхождении](../database/retailcase_ni053_marked_disposition_20261011.md):230 original order2031 accepted2/missing1/exact physical-key facts/version10/legacy case/no goods or GovACK; original code index reused.

- [Согласование возврата конкретных маркированных единиц](../database/retailcase_ni062_marked_approval_20261011.md):231 accepted-only pool/exact unit allocation/no duplicate approval/legacy229 full proof/current role/no P-H effect.

- [Ответственность после полной приёмки](../database/retailcase_ni053_final_custody_20261011.md):232 same-TX custody release/manual old receipt/no goods rewrite/partial keeps vehicle capacity.

- [Передача маркированного возврата](../database/retailcase_ni062_marked_custody_20261011.md):233 exact approved1unit/2QR/separate store-driver/current binding/backhaul within existing capacity/no stock.

- [Маркированный возврат принят складом](../database/retailcase_ni062_marked_receiving_20261011.md):234 original1key/2QR/P1H0/blocked cell/same birth codes/version11/current return UID/one stock event.

- [Прежнее размещение маркированного возврата](../database/retailcase_ni062_marked_placement_20261011.md):235 original957/DONE-SYNCED/P1H0/same codes/unit12/eligibilityBLOCK/current cached plan scope.

- [Маркированный возврат списан по акту](../database/retailcase_ni062_marked_disposal_20261011.md):236 original1key2QR/P0H0/same codes/independent act/CRPT-EGAIS notificationsPENDING/no legalACK.

- [Прежняя СТ маркированного возврата поставщику](../database/retailcase_ni062_marked_supplier_20261011.md):237 original1unit/2QR/958/ST641370/33547/P0H0/same codes/shared RegulatoryAPI notificationsPENDING.

- [Фактические сроки межскладского подвоза](../database/retailcase_ni061_phase_timing_20261011.md):238 one snapshot/current scope/aware phase timestamps/Decimal delays/active queue and bounded history/no stock.

- [Решение по задержанному подвозу](../database/retailcase_ni061_dispatch_decision_20261011.md):239 immutable WAIT-DEFER/current33551/original33550/expected cargo gate/old961-ST641375-QC-load-depart/same3units6codes.

- [Административное температурное решение](../database/retailcase_ni061_thermal_20261011.md):240 current SKU-cell ranges/manual8.125/HOLD-PROCEED/immutable963 mode2-4/native move refusal/same task release/no sensor fiction.

- [Поздняя СТ после погрузки и два источника](../database/retailcase_ni022_late_loaded_assignment_20261011.md):241 same additive owner preserves loaded641383/adds641384/frozen capacity/33558 two roots20kg/current200kg2places/board2-1blocks2-2ready.

- [Атомарное перепланирование не начатого задания](../database/retailcase_ni061_task_replan_20261011.md):242 original root command/970cancelled972created/old2-4/new2.5-3.5/rollback/concurrent one active/current edit replay403/P3H0.

- [Ошибка подвоза и новое назначение](../database/retailcase_ni061_incident_20261011.md):243 one immutable incident-DEFER/original33562-current33563/WAIT keeps incident/scoped history50/later original975receipt3 linked/no stock deduction.

- [Чтение складских заданий по текущему складу](../database/retailcase_ni081_task_read_20261011.md):244 one READ ONLY current view-WARE/task-native scope/list-sync filters/family checks/current changedWARE-revoked rights403/no writes.

- [Отмена освобождает свой рабочий ресурс](../database/retailcase_ni081_cancel_resource_20261011.md):245 same metadata TX/current task edit-WARE/conditional session release/CANCELLED fact/repeat stable/other pointer preserved/session40restored/no qty.

- [Предварительный контроль сохраняет свою погруженную СТ](../database/retailcase_ni081_retained_preflight_20261011.md):246 same read snapshot/exact active physical proof/current trip; foreign-new-departed blocked/no stock.

- [Временная занятость ARM](../database/retailcase_ni081_time_preflight_20261011.md):247 explicit legacy wall region/same read snapshot/vehicle-driver conflicts/open fact remains occupied/Gantt form/no operational admission.

- [Утверждение времени ARM: проект решения248](../database/retailcase_ni081_trip_time_design_20261011.md): original source hash/immutable version/current scope/CFG-TT; implementation in progress.

- [Утверждённый часовой пояс ARM](../database/retailcase_ni081_trip_time_20261011.md):248 native immutable version/sourcehash/current scope/late rollback/one HTTP winner; original new TT planned status fixed; no stock/admission.

- [Рейсы в разных часовых поясах](../database/retailcase_ni081_cross_zone_20261011.md):249 native source-valid approval perTT/absolute overlap/safe candidate superset/changed approval blocked/no stock.

- [Ограничение опубликованной занятости: проект250](../database/retailcase_ni081_time_resource_design_20261011.md): same native approval/CFG-X absolute envelopes/bounds; implementation pending.

- [Атомарная публикация занятости](../database/retailcase_ni081_time_resource_20261011.md):250 same native approval/CFG-X/current source-valid envelope/driverORvehicle/concurrent different TT one winner/end=start accepted/no goods.

- [Снимок погрузки текущего склада](../database/retailcase_ni052_loading_read_20261011.md):251 real actor/current view-WARE/one READONLY/original load+journal proof/scoped history/no stock.

- [Регуляторная очередь в сверке склада](../database/retailcase_ni072_regulatory_scope_20261011.md):252 sourcewarehouse/currentrootAPPLIED/messagecounts/notgovACK/functional index180→12.917ms.

- [DEFAULT нового рейса](../database/transport_planned_default_20261011.md):253 correctUnicode plannedstatus/alloriginalcallers future/no oldmassrepair/directrollback; corrected earlier source attribution.

- [Дневные факты заданий](../database/retailcase_ni072_task_times_20261011.md):254 existingawarestart/newimmutableDONEclock/same row TX/rollback+repeat/task979/day1-1/oldtimestamps unclassified/no stockwriter.

- [Плановый ключ времени: проект256](../database/retailcase_ni081_time_source_design_20261011.md): execution state separates from materialplan/V2 fullsource/legacy notendorsed; implementation pending.

- [Склад и рейс одним снимком](../database/retailcase_ni081_coordination_20261011.md):255 originaltime/loading/incoming/placementproof/currentreadycutoff/shared cursor/publicboundary/Gantt/noadmission.

- [Ключ материала временного плана](../database/retailcase_ni081_time_source_20261011.md):256 excludesexecution/frozenfullV2material/oldlegacyreview/explicitallloadedproof/currentplan remains afterload/depart.

- [Перерывы в цепочке рейса](../components/retailcase_ni081_driver_rest_20261011.md):257 explicitREST/continuousdrive/missingroute/typedGantt/singletrip parameters only.

- [Планы водителя за день](../components/retailcase_ni081_driver_day_20261011.md):258 same current snapshot/source-approved ownzones/exact midnight/combine trips/unknowns/Gantt.

- [Длительность конкретного маршрута](../database/retailcase_ni081_route_input_20261011.md):259 originalOPS/manualestimate/materialsource/replay/atomicregenerate/Gantt.

- [Приёмка SAP: доступ и укладка](../components/retailcase_ni011_receipt_layout_20261011.md):260 scoped same snapshot originalsource/261 count/manualexactlayout/no newstockwriter.

- [Восстановление приёмки](../components/retailcase_ni011_receipt_recovery_20261011.md):262 durable original perOPrequest/codes/reload/currentauth/rootreplay;263 chooseproposalquantity before actualscans.

- [Календарь магазина и отложенная потребность](../database/retailcase_ni022_calendar_20261011.md):264 native datesOPEN/CLOSED/history/currentWARE/retainedPENDING_CALENDAR/sourceJSONbind fix/rawUI.

- [Текущий склад SAP-источника](../database/retailcase_ni022_source_scope_20261011.md):265 nativeWARE/actor/sharedCONFIG4/legacyprepare/current scoped snapshot/no splitter.

- [Служебная учётная запись SAP-шлюза](../database/retailcase_sap_gateway_actor_20261011.md):266 actualworker actor registration/leastprivilege/sourcewideonly/real localXML archive replay.

- [Решения ERP по исходным заказам](../database/retailcase_ni022_erp_admission_20261011.md):267 native atomic admission/rejection, immutable source demand, file gateway and current worklist.

- [Готовность SAP-заказа к прежней СТ](../components/retailcase_ni021_preparation_readiness_20261011.md):268 current source/calendar/deadline/packaging diagnostics, historical splitter source found but not applied.

- [Журнал рассмотренных дневных сверок](../database/retailcase_ni072_review_20261011.md):269 immutable captured report/version/replay/locked outcome recovery/history; open obligations preserved, no false day closure.

- [Назначение нескольких паллет одной СТ](../database/retailcase_ni022_multi_st_20261011.md):270 scalar-row bug fixed in existing native assignment, partly loaded group preserved/frozen; actual2pallets sameST assigned.

- [ARTMAS масса и размеры → прежняя подготовка СТ](../components/retailcase_ni011_artmas_logistics_20261011.md):271 exact unit mapping/current native configuration, actual assumedERP48→2originalST pallets→existing33571 planning only.

- [Частичные изменения единиц ARTMAS](../components/retailcase_ni011_artmas_sparse_units_20261011.md):272 preserve ratio/omittedUoMs/EAN, unknown unproven unit atomic rejection.

- [Точный пересчёт единиц SAP в Oracle](../database/retailcase_ni011_exact_source_20261011.md):273 rational1/3 uses existing native math/current source policy; supply actor-WARE before replay/sharedCONFIG4.

- [Раздельные ресурсы импорта поставок SAP](../database/retailcase_ni011_supply_resources_20261011.md):274 globalSRX removed, original receipt document anchors/current originalWARE, independent source0.032s.

- [СТ и занятость грузовой зоны в дневной сверке](../database/retailcase_ni072_shipping_register_20261011.md):275 dated existing member cursor/current native load proof/declaredcells occupancy/frozen review;737→14ms and3782→27ms, coverage not falselycomplete.

- [Атомарный перенос неотобранной СТ](../database/retailcase_ni072_st_defer_20261011.md):276 прежнее назначение/неизменяемая причина/версия/исходный SAP сохранён; фактические две паллеты и конкурентный победитель.

- [Граница переноса СТ](../database/retailcase_ni072_st_defer_design_20261011.md): первоначальный проект276; окончательная реализация и ограничения описаны в странице переноса.

- [Точная упаковка трети заказа](../database/retailcase_ni022_exact_pallet_share_20261011.md):277 исправлено округление1/3, прежняя подготовка дала3паллеты24EA/1box/10kg из72EA.

- [Укладка SAP в прежнюю СТ](../components/retailcase_ni022_source_layout_20261011.md):278 существующая норма/целые коробки/изменяемые паллеты/старый writer/durable command и ожидающий resolve.

- [Время дорожной матрицы](../database/retailcase_ni081_road_duration_20261011.md):279 providerduration вместо50км/ч, nullнеzero, явный ROAD_PROFILE/SPEED basis; localroadproviders unavailable.

- [Проект источника маршрута V3](../database/retailcase_ni081_route_material_v3_design_20261011.md):280 зафиксирован пробелV2 и граница сохранения физической истории.

- [Длительности остановок текущего рейса](../components/retailcase_ni081_road_legs_20261011.md):281 existingV3/currentpairmatrix/unknowns/explicitdepot/oldRouteInput fieldfill;41→5мс.

- [Дорожные минуты в прежнем OR-Tools](../components/retailcase_ni081_vrp_profile_times_20261011.md):282 onecallback/displaymatrix/profilebasis/fallback known, actualsolver25мин→arrival75.

- [Очередь приёмки возвратов с продолжением](../components/retailcase_ni062_return_receiving_queue_20261011.md):283 currentWARE/right/singleRO/litepage+selectedfullproof/nativeREUSE reused/foreignconfig403.

- [Восстановлен прежний OSRM/Valhalla](../runbooks/retailcase_routing_recovery_20261011.md):284 готовые карты/существующие контейнеры healthy/реальные directional times/digestpin/1000mcoverage guard.

- [База отправления склада](../database/retailcase_ni081_warehouse_depot_20261011.md):285 existing-address reference, native version/CONFIG6/sourceV4, real concurrent200/409; depot unset pending owner.

- [Проект базы отправления](../database/retailcase_ni081_warehouse_depot_design_20261011.md):285 reference boundary and current route invalidation.

- [База в текущей оценке рейса](../database/retailcase_ni081_trip_origin_read_20261011.md):286 configuredcurrentorigin/same snapshot, missingbase UNKNOWN/null, currentHTTP passed.

- [Окна доставки прежних СТ](../database/retailcase_ni081_delivery_windows_20261011.md):287 sourceV5 existingwindows/norms/earliestcurrentroute/table, missingdataUNKNOWN; no admissionclaim.

- [Проект окон доставки](../database/retailcase_ni081_delivery_windows_design_20261011.md):287 originalwindow boundaries/current source invalidation.

- [Общая сводка склада и рейса](../database/retailcase_ni081_coordinated_route_20261011.md):288 same snapshot currenttime/driverday/rest/windows/load, ordinarytrip fixed; no departureauthorization.

- [Ранний допуск годного возврата](../database/retailcase_ni062_reuse_approval_20261011.md):289–290 existingnativehelper beforepickup/current source preview/BOX24 positive-source vsremaining0; no freshphysicalclaim.

- [Проект раннего допуска REUSE](../database/retailcase_ni062_reuse_approval_design_20261011.md):289 deterministic batch/BOX blockers movedbeforepickup.

- [Частичная межскладская приёмка](../database/retailcase_ni061_partial_receiving_20261011.md):291 ordinarysinglepallet expected3→accepted1/short2, freshUID/native+PUT/concurrent200-409; carrier remainsopen.

- [Проект частичной приёмки](../database/retailcase_ni061_partial_receiving_design_20261011.md):291 onefinalshortreceipt/uniquesretained/markedsubset+resolution separate.

291 rollback clarified: retainedhistory refuses beforechanges; oldnativepayloadguard/cloneguard restored, additivecolumns retained.

- [Маркированная частичная приёмка](../database/retailcase_ni061_marked_partial_20261011.md):292 chosen1/2profiles from3/6codes, samecore+PUT, remaining2ISSUED/shortageopen.

- [Проект точного маркированного подмножества](../database/retailcase_ni061_marked_partial_design_20261011.md):292 preservebirth/codes/currentversions andno falsecustodyrelease.

- [Закрытие расследования после полной приёмки](../database/retailcase_ni061_incident_close_20261011.md):293 explicitcurrentTargetDispatcher/reason/evidence/native append-only/no stock; old243 full recovery, partial292 refused.

- [Проект закрытия расследования](../database/retailcase_ni061_incident_close_design_20261011.md):293 one incident/one closure, full applied receipt required.

- [Сверка недостающего товара](../database/retailcase_ni061_shortage_reconciliation_20261011.md):294 declared/accepted/short2, exact marked missing subset/currentstates/codecounts/one scoped snapshot.

- [Проект подтверждения недостачи](../database/retailcase_ni061_shortage_disposition_design_20261011.md):295 loss book and current resources;296 explicit acceptedfragment custody next.

- [Проект движения после недостачи](../database/retailcase_ni061_partial_custody_design_20261011.md):296 accepted+confirmedshort accounting without false fullreceipt.

- [Окончательная приёмка частичного межскладского товара](../database/retailcase_ni053_partial_final_receipt_20261011.md):297 reused STORE qty1, original3/accepted1/unreceived2/confirmedloss2, explicit UIDlineage/oneowner/no guess.

- [Поиск приёмки по исходной погрузке](../database/retailcase_ni053_lineage_lookup_20261011.md):298 missing source index/NL,70.349ms6278buf→20.529ms146buf total3, exactfull/partialprojection preserved.

- [Проект корректирующей приёмки найденного товара](../database/retailcase_ni061_loss_recovery_design_20261011.md):299-300 preserveloss history/sourcecodes/one nativeUOW; next actualP2.

- [Корректирующая приёмка найденного товара](../database/retailcase_ni061_loss_recovery_receiving_20261011.md):300 samecore actualP2/newUID/old2units4QR/all6codes retained/quarantine/no customerACK.
- [Многопериодное начисление NI07.1](../database/retailcase_ni071_cost_periods_20261012.md): checkpoint512, отдельные ставки по датам / один источник / исторические строки сохранены; применение ожидается.
- [Часы физической сборки BOX](../database/retailcase_ni041_box_packing_clock_20261012.md): checkpoint516, новое первое сканированное вложение через ядро / неизменяемый цикл, без выдуманных старых дат.
- NI07.1 checkpoint518: shared native CASE/BOX assembly resolver prepared; see packing clock page.
- NI07.1 checkpoint534: current norm actor/grant source/head order, auth before saved replay; see transport norms page.
- [Факты выгрузки магазина](../database/retailcase_ni053_unloading_facts_20261012.md): checkpoint539, system start/actual method-loader/atomic existing receipt finish; application pending.
- Unloading checkpoint544: stock lock clean-plan order before savepoint, actual543 retained/no writes yet; see unloading page.

- [NI03.2: частичная замена нескольких резервов](../database/retailcase_ni032_multi_binding_partial_20261012.md): prepared631, existing native continuation, no new quantity writer.

- [Checkpoint635: несколько резервов одной подачи](../database/retailcase_ni032_multi_binding_partial_20261012.md): native631 applied VALID, actual632 owner6+6→target8H8/source8H4, cleanup633, original replay preserved.

- [NI08.1: непрерывное вождение между рейсами](../components/retailcase_ni081_cross_trip_continuity_20261012.md): existing driver-day/rest rule shared, midnight not rest, domain637/TS/architecture PASS; actual legal duty unverified.

- [NI06.2: сохранённая исходная паллета](../database/retailcase_ni062_preserved_pallet_20261012.md): prepared639/640, exact whole original identity/unit matrix, existing single writer and transaction.

- [Checkpoint648: исходная паллета возврата](../database/retailcase_ni062_preserved_pallet_20261012.md): native639 VALID/actual643 oldUID P3H0/3keys6codes, currentUI/plan27; original identity guard supersedes629 only for unchanged whole pallet.

- [NI07.2: полнота классификации грузовой зоны](../components/retailcase_ni072_shipping_coverage_20261012.md): existing published topology/current catalog, same snapshot, diagnostics; actual650 rollback/stock preserved, no physical survey/day close claim.

- [NI07.2: перенос без потери исходного дня](../database/retailcase_ni072_deferred_day_register_20261012.md): prepared652, existing journal/cursor/member proof reused, additive day index.

- [Checkpoint654: исходный день перенесённой СТ](../database/retailcase_ni072_deferred_day_register_20261012.md): index652 VALID, retained653 two NULL-date members/cursor/current target/rollback; currentNI07.2.

- [Единый код профиля маркировки](../components/retailcase_marking_profile_contract_20261012.md): producer/scanner80-byte contract reused, current configured names no longer blocked by API60, selective draft correction.

- RETAILCASE, 13.10.2026, 20:00 МСК: актуальное состояние и ограничения продолжения — [[../runbooks/retailcase_active_work]]; остановка по сроку, полный комплект спринтов ещё открыт.

- [Выгрузка обычной паллеты1316](../database/retailcase_ni053_stock_pallet_unload_20261014.md): исходный frozen loading proof для ROOT_STOCK_TYPE; prepared.


- [Prepared native weekly store windows](../database/retailcase_ni081_store_weekly_windows_20261014.md): complete ST precedence, same-day closed/interval semantics, DST refusal, source V7; root apply pending.







- [Повторное ревью C0049](../components/retailcase_roles_initial_review_20261014.md): область конкретного назначения роли, эффективные права команд и первый сквозной срез; runtime не менялся.

- [Предложение: роли, KPI и надёжные команды](../concepts/retailcase_roles_kpi_command_proposal_20261014.md): additive назначения с областями, определения KPI и восстановление по operation_id; ожидает согласования владельца.


- [Подтверждение нуля складских весов](../database/retailcase_warehouse_scale_zero_progress_20261015.md): APPLIED15/0,15 native checks +6 actual HTTP calls, encrypted6/47 focused; immutable ZERO/current lease signal, QA cleanup, без capture/товарного эффекта.



- [Матрёшка и смешанная консолидация](../concepts/retailcase_nested_hu_consolidation_20261015.md): дерево уже native; отдельные gaps ASM→QC, outer SHIPPING_GROSS, температура и subtree приёмка нескольких магазинов; следующий AK06-C/E +AK08.

- [Уточнение HU QC/складов/прав](../concepts/retailcase_nested_hu_consolidation_20261015.md#уточнение-контроль-после-упаковки-не-требует-цикла-распаковки): per-ST QC внутри упаковки существует; parentQC/scopedHU/arbitrary ASM interWARE ещё не доказаны.

- [Граница межскладской CASE-консолидации](../concepts/retailcase_nested_hu_consolidation_20261015.md): существующий interWARE HU owner STOCK-only; assembledCASE bridge — отдельная работа F2.
