# Сборка на весах: назначенный исполнитель и область склада

Статус: v3 и исправление порядка блокировок APPLIED в dev RABAEV/orcl; полный программный TEST ASM1140 и actual HTTP scopes PASS. Продолжение блоков 1–3 по поручению владельца. Не закрывает весь блок прав, смешанные HU или аппаратный пилот.

MIGRATION_ID: `2026-10-15-assembly-scoped-execute`.
SQL: [версионный комплект](../../db/migrations/2026-10-15_assembly_scoped_execute/README.md).
Checkpoint: [исходники и зависимости](../../reports/retailcase/2026-10-15/assembly-scoped-execute/).

## Контракт

Назначенный текущий оператор обычной немаркированной счётной CASE получает исполнение через действующее назначение роли на фактический склад/группу/SELF. Живой родитель HU, весовой или сериализованный SKU не получают этот путь. Конфигурация, управление, независимый контроль и ingest весов остаются отдельными полномочиями.

`RRL_ASM_META_SCOPE` доступен только `RRL_ASSEMBLY_SCALE_API`; повторяет native metadata fences и проверку текущего назначения до/после блокировок. Отдельного писателя количества нет. `CASE_PICK_CONFIRM` требует явный assembly_step_id и прежние assert_post/claim_post, доказательства, согласие, версию содержимого, устройство, дельту и однократный STEP_USE.

Metadata-вход scoped оператора требует чистую транзакцию. Отказ внутри чужой stock-транзакции не очищает чужой план. Порядок блокировок REV→CONFIG→CASE согласован с основной проводкой. Legacy rollback сохраняется.

Закрытие использует существующий native close UOW; Python проверяет текущую привязку сессии до и после блокировки CASE. Требуется одна текущая собственная OPEN-сессия, применённый шаг, отсутствие незавершённых шагов и BLOCKED/HOLD. ASM_FINAL не является shipping QC.

## Применение и проверка

Пакеты до изменения, schema/service, 15 зависимых package bodies, история и SHA сохранены. Комплект v3 явно перекомпилирует зависимости после замены спецификации и при rollback; неизменные исходники проверяются по SHA. Frozen manifest: `02875126bc2a25e98f6a4b031a1c1f8e4d8a5f58c9fd946e71deac149b7b4bfe`.

Проверки до native применения: Python close/binding 27 PASS; общий quality gate PASS (архитектура 1096 файлов/0 циклов, tooling 24, оба TypeScript). Это проверки автора, не независимая и не физическая приёмка.

Применение v3 завершено; отдельное native readback подтвердило 26 SHA исходников, ledger APPLIED, USER_ERRORS=0, INVALID=0 и неизменные семь историй. Прямой anonymous helper отклонён PLS-00904; неизвестный оператор и грязная scoped metadata-транзакция отклонены до эффекта. [Readback](../../reports/retailcase/2026-10-15/assembly-scoped-execute/root-readback-v3.json). API перезапущен без reload.

Требуются native positive workflow, отзыв/чужой оператор, повтор и изменённое тело, блокировки двух соединений, сохранность stock context, legacy negatives и разбор SQL. Rollback запрещён после изменения соответствующей истории; история не удаляется для обхода guard.

Исторический GAP v3: legacy flat execute исключал scoped helper целиком. [Additive classifier](retailcase_additive_legacy_task_scopes_20261016.md) теперь применён: homeWARE/GLOBAL сохраняют legacy, foreign actor проходит explicit-role gates. HTTP/replay/отзыв проверены; новый foreign-flat quantity сценарий и прочие команды ещё требуют матрицы совместимости.

## Исправление после положительного TEST

Свежий изолированный склад20220394/SKU AS16A35CEA92C27/CASE1140, ресурс64/сессия60; flat execute отозван до CLAIM/START, роль WAREHOUSE назначена. Только TEST-режим/имитация этикетки и массы; аппаратная приёмка не заявляется. Недостающая BOX conversion фикстуры добавлена, исходная волна571 продолжена с прежним launch operation_id; истории сохранены.

Открытие ASM остановлено защитой DIRTY_TRANSACTION: v3 выделял local_transaction_id(true) до begin_plan. Сессия ASM и количество не изменились. Применён body-only amendment `2026-10-16-assembly-metadata-lock-order`: begin_plan→REV→CONFIG, trusted helper проверяет прежнее legacy либо scoped право до/после fences; cleanup только собственного плана. [Комплект](../../db/migrations/2026-10-16_assembly_metadata_lock_order/README.md), [before evidence](../../reports/retailcase/2026-10-16/assembly-metadata-lock-order/before/manifest.json), [readback](../../reports/retailcase/2026-10-16/assembly-metadata-lock-order/root-readback.json). SHA frozen manifest `890957c1664a607fb255ddac6b22dbca14fc030e3e179767aff466dcf3feb509`.

## Фактическая программная приёмка

- Свежая CASE1140: WARE-role CLAIM/START→TEST tare→OPEN→AUTO consent→BEFORE/AFTER→READY→canonical CASE_PICK_CONFIRM/STEP_USE→CLOSE→manager ST binding→FINAL_GROSS request/claim/capture→FINALIZED. Перед commit количество/STEP_USE проверены с точным caller rollback. Один отбор 1EA, повтор не добавляет количество.
- Native negatives: чужой actor, отсутствие assembly_step_id, неверный consent; поздний/предшествующий claim измерительный интервал не принят. Новая валидная серия в текущем claim завершилась успешно; старые факты/ошибки сохранены.
- [12 actual HTTP](../../reports/retailcase/2026-10-16/assembly-scoped-execute/http-rights.json): WARE/SELF/current GROUP, отзыв, удаление членства, finish/close replay и изменённый finish body409. Все тестовые назначения отозваны.
- [Два соединения](../../reports/retailcase/2026-10-16/assembly-scoped-execute/rights-lock.json): exclusive REV останавливает metadata на2019мс/ORA54; контексты пусты, после снятия блокировки replay FINALIZED проходит, временный grant отозван.
- [SQL review](../../reports/retailcase/2026-10-16/assembly-scoped-execute/sql-review.json):12 Oracle/local пар, maxHTTP235мс,6 TX/denial slow records; cumulative top cursor means не p95. Решение: сохранить exact identity/50-step bounds/current native rights, новый индекс/cache не добавлять без pilot plan evidence; owner inventory/native ASM.

Все данные TEST, этикетка/масса имитированы; реальное OPC/hardware и shipping QC не приняты. Один новый склад/CASE/СТ изолированы; собственный товар остаётся для продолжения mixed-HU блока. Сессия ASM FINALIZED, CASE WAIT_CONTROL; ресурсная сессия60 пока сохранена для продолжения и подлежит закрытию при retirement фикстуры.

Свежий склад потребовал явной регистрации ACCESS_OBJECT и системной ячейки CPT_20220394 с lock key. Это требования onboarding; не обходить их прямым расширением доступа или auto-publish в quantity path. Зафиксировать отдельный product onboarding сценарий вместо неявной зависимости от заранее созданных складов.

Связи: [[retailcase_case_scoped_close_20261015]] · [[retailcase_incremental_assembly_20261015]] · [[../components/retailcase_queue_scoped_read_20261015]].
