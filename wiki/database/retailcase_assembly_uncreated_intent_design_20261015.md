# Assembly never-created intent · durable abandonment design

READ-ONLY DESIGN по root-поручению. Ни DDL, ни ASM body не изменены; latest ASM source временно принадлежит warehouse-request owner. Проблема: definitive bad-scan409 не создаёт STEP, однако UI правильно сохраняет исходный неизменный pending intent. Простое удаление localStorage/замена operation_id может допустить поздний commit первого OPEN.

## Новый узкий контракт

Отдельная команда ABANDON_NEVER_CREATED с новым abandon_operation_id, kind OPEN_SESSION|OPEN_STEP, original actor/task/session/step/stockoperation identity, сохранённым canonical original payload/SHA и reason. Сервер вычисляет SHA сам, не принимает browseractor. Native проверяет текущего assigned operator и warehouse scope. Tombstone хранится неизменно в отдельном RRL_ASM_INTENT_ABANDON с original payload/author/reason/savedreceipt/time; записи не удаляются.

Под чистой транзакцией CONFIG X + original OP10 для OPEN_STEP (для OPEN_SESSION отдельный namespaced session-intent OP10) →CASE locks native ждёт текущую попытку, затем проверяет отсутствие SESSION/STEP/STEP_USE/связанной canonical stockoperation. Любая существующая либо неопределённая операция даёт EXISTS_RECONCILE_REQUIRED/OUTCOME_REVIEW: уже созданная работа не отменяется. Только доказанное отсутствие после locks фиксирует ABANDONED. Для OPEN_SESSION сейчас нет stock operation_id; его нельзя выдумать или приравнять ко всей истории CASE.

Все последующие исходные open_session/open_step обязаны проверять tombstone повторно ПОСЛЕ metadata fences/CASE lock и до insert. Иначе read-before-wait создаст гонку. Предпочтительно общий новый native begin builder для OPEN/ABANDON с полным OP10→CASE порядком. Минимальный переходный вариант — новый ABANDON builder плюс recheck внутри прежних OPEN: их общий CONFIG X уже сериализует записи; доказать двумя соединениями. Нельзя добавить OP10 после старого metadataROW20 и нарушить lock order.

Tombstone scope включает original actor+CASE+kind+intent identity, чтобы пользователь со своим CASE не мог угаданным nonce отменить чужую будущую попытку. Для STEP проверяются originalstep_id И originalstockoperation_id: новое тело под любым прежним ID не воскресает. Identity смены actor/task не является точным повтором прежнего intent; API требует свежие непереиспользуемые nonce. Late OPEN с исходной областью получает терминальный ABANDONED, а не создаёт данные.

## UI и границы

Одна понятная операция «Исправить скан»: сохраняет новый abandon intent, получает durable ACK, лишь после ACK предлагает исправленный ввод с новыми IDs. При потере связи повторяется точный abandonoperation/body; 404/statusread и timeout сами по себе отсутствия не доказывают. Пока ACK не получен, прежний intent сохраняется. Если поздний OPEN успел commit, UI восстанавливает реальный SESSION/STEP и предлагает штатную RECON, не скрытое удаление. Offline не разблокирует редактирование исходной команды.

Для never-created intent не нужен физический recount/controller: товара/измерения/шага ещё нет, отсутствие доказывается native под locks. Существующий измеренный шаг требует двухстадийного HOLD/independentcontroller/реального GROSS reconciliation. APPLIED никогда не abandoned. FINISH/CLOSE и read-only malformed localstorage требуют отдельных контрактов; они не включаются этим инкрементом.

## Приёмка до применения

OPEN commit выигрывает race→ABANDON409 без tombstone; ABANDON выигрывает→поздний OPEN терминально запрещён; OPEN rollback→durable tombstone; потерянный abandonreply→тот же receipt; changedbody/sameIDs конфликт; currentrevoke/foreignactor/foreignCASE отказ; ни SESSION/STEP/USE/stockop при successfulabandon. Legacy DTO/hash/replay unchanged. Native source snapshots/paired rollback/constraints/ledger/INVALID0; real API и UI retry/offline tests; slowSQL identity point lookups/CONFIG wait attribution.

[[retailcase_assembly_recovery_20261015]], [[retailcase_case_scoped_write_audit_20261015]].
