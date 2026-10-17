# CASE scoped writes · read-only audit 15.10.2026

Исходный аудит был DESIGN/READ-ONLY и не менял роли, DDL или бизнес-данные. Позднее отдельный narrow CASE_PICK_CONFIRM kit прошёл review и APPLIED; его статус и границы приведены ниже. [USER_SOURCE snapshots +SHA](../../reports/retailcase/2026-10-15/scoped-case-audit/native-sources.json), targeted root/compiler/metadata call sites рядом. Источники прочитаны из текущего Oracle после assembly/recovery; позднейший forward kit должен переснять before, а не использовать этот audit как apply script.

## Фактическая граница

| Путь | Текущий допуск | Следствие |
|---|---|---|
| RRL_CASE_TASK_ACCESS.assert_scope | активный RUSERS; GLOBAL_ADMIN либо RUSERS.WARE_ID=CASE.WARE_ID; затем RRL_HAS_WRIGHT | назначения ACCESS_API не учитываются |
| RESOURCE_POLICY.context_json | helper выше + повтор flat execute/manage/targetexecute | resource/session/qualification/shift guards правильные, но assignment-only всё равно отвергается |
| CASE_PICK_CMD compile/execute | RESOURCE_POLICY COMPLETE; execute CASE_PICK_FORBIDDEN из RRL_HAS_WRIGHT; assignee override flatmanage | замены одного API dependency недостаточно |
| StockPosting root | CASE guard до replay и после locks; CASE_PICK_CONFIRM revisionSHARE сразу после begin_plan | singlewriter/replay/lock grammar уже правильная, её сохранять |
| StockMetadataTX +CaseActions.run_action | flat RRL_HAS_WRIGHT до metadata begin | scoped claim/start не достигают authoritative CASE helper |
| case_pick.py claim/start/confirm и label/type/weighted APIs | require_permission legacy group | identity-only native routes нужны после native допусков, не сами по себе |
| assembly/recovery | assigned operator сохраняется, но begin_meta/CASE helper/Recovery.lock_step flat | принятый native CASE scope следует переиспользовать и здесь отдельным coordinated increment |

Warehouse scoped VIEW и TASK_COMPLETE не означают поддержку CASE write. GLOBAL_ADMIN/legacy группы сохраняют существующую семантику; расширять RRL_HAS_WRIGHT назначениями без targetWARE нельзя: функция не знает область и может выдать глобальные права из локальной роли.

## Предлагаемый порядок

1. Узкий native `scoped_executor(task,actor)` для назначенного обычного count/unmarked CASE. RRL_ACCESS_API.allowed(case_pick_execute,WAREHOUSE,actualCASEWARE,owner=ASSIGNED_TO), activeuser/currentassignment и реальные resource/session/qualification/shift/currentWARE resource сохраняются. Legacy пути остальных CASE не расширяются автоматически. Условные flat checks в CASE access/resource/compiler/execute изменяются только для этого доказанного admitted branch. API identity+pure scoped preflight, canonical CASE_PICK_CONFIRM writer прежний. Execute и view не взаимозаменяются; SELF не даёт claim не назначенной работы.
2. Scoped ASSIGN/START — отдельный resources metadata owner с operation_id/currentversion/exact saved receipt/audit. Текущий CLAIM повторно пишет CLAIMED event, request не имеет operation_id; START сначала проверяет context и при существующем started_at возвращается. Требуется явный idempotent metadata контракт, не скрытое обнуление неизменяемого actual start. Manager assignment/transfer и worker self-start — разные права; target capability/physical session проверяются независимо от менеджера.
3. Labels/tare/assembly/recovery подключаются к тому же native CASE допуску отдельной матрицей. Dedicated scale sender не получает права stock actor. UNKNOWN/weighted/marked/HU/crosswarehouse scenarios не включаются без приёмки. Native helpers должны использовать pure allowed до strict begin_plan, revision SHARE после begin_plan до policy/resources и текущий guard под locks; assert_allowed до strict begin_plan создаёт dirty transaction.

Metadata begin builder использует существующие StockPlanHelper/StockLockAPI/CONFIG fence и полный порядок OP10→CASE20→session/resource; он не может просто добавить OP10 после старого StockMetadataTX ROW20. Нового stock writer или обхода physical/session guards не требуется.

## Обязательная приёмка следующего инкремента

Native-only SELF/WAREHOUSE/group, legacy compatibility, ownassigned positive CASE canonical callerrollback, foreignWARE+wrongassignee+executeA/viewB+expired/revoked role, replay currentauthorization, wrongresource/qualification/shift, two-connection revoke/operation race. API direct/browseractor rejection и отсутствие нового goods commit в TEST fixtures. SlowSQL review PK/current source predicates, bounded scans; индекс только при измеренном плане. Это plan, не заявленная live positive scoped CASE приёмка.

[[retailcase_task_scoped_complete_20261015]], [[retailcase_incremental_assembly_20261015]], [[retailcase_scoped_access_knowledge_20261014]].

## Подготовленный узкий CASE_PICK_CONFIRM kit

Статус **APPLIED** координатором: 8 statements/0 errors, независимая сверка 6 current USER_SOURCE exact, USER_ERRORS/globalINVALID=0, ledger APPLIED. Native SELF execute/resource/revoke callerrollback proof PASS на общем fixture1136; другие матрицы и committed replay перечислены ниже. [forward/paired rollback/checkpoint](../../db/migrations/2026-10-15_case_scoped_confirmation/), [read-only verifier](../../scripts/case_scoped_confirmation_verify_oracle.py). Проверка before: шесть actual USER_SOURCE совпали, USER_ERRORS/globalINVALID=0, ledger отсутствует. Независимый review и применение выполнены; проверка DDL не подтверждает native business acceptance.

`has_current_scoped_execute` проверяет текущего активного назначенного исполнителя и ACCESS_API с фактическим CASEWARE/SELF. Этот guard стоит до чтения APPLIED receipt: позднейший HU/состояние/политика исполнения не скрывают прежний canonical результат при неизменном текущем доступе. Отзыв назначения запрещает replay. Отдельный `scoped_executor` добавляет eligibility нового исполнения: все строки обычные EA1:1, без marked/serialized/weighted/profile, без активного HU/ASM и shipping. Наличие LEGACY_SBORKA_PALLET_ID само по себе не выключает допуск; текущий CASE_PICK создаёт CASE_CARRIER_LOT и не заполняет этот legacy ID, поэтому отдельная live проверка populated legacy CASE остаётся открытой. Старые flat/GLOBAL_ADMIN возвращаются в исходную ветвь со старой семантикой manager/target.

Resource COMPLETE и execute допускают только этот новый narrow branch; проверка реальной активной смены, квалификации CASE_PICK, resource/session/equipment/WARE и волны сохраняется. Scoped actor не получает manager fallback без физической сессии. CLAIM/START/TRANSFER/labels/tare/ASM этим kit не расширяются. Confirm API использует identity + pure READ ONLY native preflight; stock writer, команда и operation_id прежние. 7 focused API/preflight tests PASS; это не замена native rollback/replay/concurrency доказательствам.

Координатор разрешил отдельный общий DEV metadata fixture через текущих owners: WAVE567/CASE1136/LINE1139, приватный REUSE.RETURN:e6c16d0bbd, WARE13583852, P24/H1 после штатного резервирования, без warehouse physical TASK. Новый actor WHREQ15.OP, фактическая legacy группа WHREQ15.OP (ограничение 15 символов), qualified CASE_PICKER resource58, OPEN shift63, собственная ACTIVE session54 созданы; CASE штатно CLAIM/START: IN_PROGRESS/assignedWHREQ15.OP/resource58/session54/picked0/v2; прежний EMPTY остался CAPTURED с STALE current context, проверено warehouse owner. [Сохранённый stage](../../reports/retailcase/2026-10-15/scoped-case-audit/shared-resources.json). Goods PICK commit не разрешён, scoped quantity proof только caller rollback; последующие фазы отмечаются отдельно. Старые ASM1031/1032 не переоткрываются: их неизменяемая OPEN история и retired actors/devices сохраняются.

## Native acceptance общего CASE1136

[Native report](../../reports/retailcase/2026-10-15/scoped-case-audit/native-acceptance.json): 11 groups PASS. Native-only SELF исполнитель с реальной qualified resource/session сделал canonical CASE_PICK_CONFIRM P24/H1→P23/H0 и CASE_CARRIER_LOT; текущий guard остался разрешён и stored canonical result совпал. Все quantities, CASE/line, events/resource events, новые lots, operation/outbox затем точно откатились. Четыре временных metadata callerrollback проверки отказали при missing qualification, PLANNED shift, PAUSED session, resource foreignWARE; dedicated sender и чужой unassigned CASE не получили execute.

[Revoke concurrency](../../reports/retailcase/2026-10-15/scoped-case-audit/revoke-concurrency.json): второй Oracle session реально ожидал `enq: TM - contention` с BLOCKING_SESSION равным stock session. После quantity rollback ROLE_SAVE отключил ровно WHREQ15.CASE.EXEC v1→2, current guard/prepare отказали; штатное восстановление v3 сохранило историю. Затем по решению координатора восстановлено только temporary flat execute для следующего штатного ASM/absence этапа; SELF assignment/role v3 активны. Ни одного goods commit в этой suite нет.

Тест уточнил исходную гипотезу: strict clean begin_plan стоит до APPLIED replay, поэтому original prepare в уже dirty callerTX тоже правильно отказывает20843. Это требование сохранено. Настоящий clean-TX committed APPLIED replay после дальнейшего workflow проверяется отдельным разрешённым ASM этапом, здесь его нет. Demand1/cleanTX не позволяют честно показать второй durable partial pick; populated legacy carrier-ID, вся SELF/WARE/GROUP/expiry матрица и mixed legacy/native права также не заявлены закрытыми этим узким сценарием.

Первый native prepare обнаружил отсутствующий CPT_13583852 policy; отдельный ограниченный [[retailcase_case_transit_13583852_20261015]] metadata kit APPLIED до положительной suite. SlowSQL: последняя1h пусто; относимые Oracle shared-cursor averages ~9.6ms context, ~6.2ms function call и ~1.3ms CASE SKU closure. Решение: сохранить текущие CASE/PK predicates без нового индекса; это функциональный тест, не capacity/hardware acceptance. Native-only сценарий не заявляет HTTP/API audit proof.
