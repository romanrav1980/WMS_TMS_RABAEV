# Legacy-группа и роль на другом складе

Статус dev APPLIED, native/HTTP classifier и текущие права PASS. Устраняет записанный GAP [[retailcase_assembly_scoped_execute_20261016]] / [[retailcase_inventory_task_scope_20261016]], не объявляет мигрированными все команды склада.

MIGRATION_ID `2026-10-16-additive-legacy-task-scopes`; [комплект](../../db/migrations/2026-10-16_additive_legacy_task_scopes/README.md), [before](../../reports/retailcase/2026-10-16/additive-legacy-task-scope/before/manifest.json).
Frozen manifest SHA `3c89b36cf52fe8313b25f654c138614cd777e9fc9bff4fc035442ce4c9715ba4`.

## Причина и контракт

Прежний helper исключал любого пользователя с flat case_pick_execute из scoped ветви. Поэтому назначение роли на чужой склад подавлялось наличием legacy-права. RRL_ACCESS_API.allowed уже различает legacy homeWARE/GLOBAL_ADMIN и явные роли; глобальную семантику RRL_HAS_WRIGHT менять не требуется.

`RRL_CASE_TASK_ACCESS.legacy_executor(task,actor)` определяет прежний допуск на фактическом homeWARE либо GLOBAL_ADMIN. На другом складе пользователь с flat-флагом проходит те же current-role/assignee/обычный счётный SKU/resource/ASM/close проверки, что и role-only исполнитель. Flat-флаг сам по себе не открывает чужой склад и не обходит ограничения marked/weighted.

Classifier подключён к canonical CASE pick, resource claim/start, close, ASM metadata и empty-tare intent. Мигрированные команды не требуют удаления legacy-группы. Старые transfer/report/manager действия не становятся мигрированными автоматически; интерфейс использует versioned CASE resource commands для scoped claim/start.

Inventory сохраняет standalone flat count на homeWARE/GLOBAL_ADMIN. Для foreignWARE явная роль становится дополнительным допуском, но count по-прежнему привязан к текущему assigned task/cell/article/revision. Наличие flat count не подавляет этот путь и не расширяет standalone count.

Общий flat metadata owner сохраняет permissions whitelist; порядок становится begin_plan→REV SHARE→CONFIG/rows. Это закрывает окно отзыва роли для metadata путей newly admitted foreign-flat actor. Старый end_change/reset контракт сохраняется; ASM имеет отдельную проверку владения своим планом.

## Проверка и откат

Только package sources:12 изменений,16 явно captured dependent body recompiles; before/after SHA и paired rollback. Сначала восстанавливаются dependent bodies, затем CASE spec/body; история и назначения не удаляются. Нового stock writer/таблиц/ролей нет. Подготовка offline, source checkpoint содержит неизменные зависимости; source drift останавливает применение.

## Фактическая проверка

[Readback](../../reports/retailcase/2026-10-16/additive-legacy-task-scope/root-readback.json):23 исходника SHA exact, ledger APPLIED, ERROR/INVALID0. API перезапущен без reload.

[Приёмка](../../reports/retailcase/2026-10-16/additive-legacy-task-scope/acceptance.json): исходный живой TEST operator ASM1140 временно получил flat case_execute; на своём складе legacy_executor1, после временного перевода homeWARE1 foreign без роли403, с явным WARE-role legacy0/scoped1. Session read/finish/close и canonical pick **replay** прошли, отзыв дал403, возвращённый homeWARE с flat снова200. Точная исходная homeWARE и отсутствие flat восстановлены; ASM/остатки/версии неизменны. Это положительные повторы существующей операции, не новая quantity проводка foreign-flat пользователя.

Свежий LC16-аудитор homeWARE1 с flat count и явной foreign ролью прошёл native admission/read по синтетическому assigned inventory task. Standalone foreign count отклонён; после отзыва роли task admission отвергнут. Синтетические строки28/29 существовали только в rollback TX, количественный owner не запускался. Direct native lot birth сохранил homeWARE denial с откатом. Новый role holder с CASE execute не признан исполнителем чужой CASE. Чистые metadata begin/end после release и two-connection exclusive REV fence прошли.

[Retirement/SQL](../../reports/retailcase/2026-10-16/additive-legacy-task-scope/retirement-sql.json):6 actual HTTP/6 Oracle-local пар, max272мс, INVALID0; LC16 пользователь DELETED, flat отозван, role inactive, grants revoked. Borrowed ASM role и исходный actor сохранены в исходном состоянии. Решение: PK/current-scope bounds и REV-before-CONFIG оставить; access/inventory owner проверяет планы classifier/membership на пилотном объёме, cache/index без измерений не добавлять.

Author review не заменяет независимую/аппаратную приёмку. Полная новая quantity/claim/start матрица foreign-flat и остальные transfer/report/manager команды остаются в общем checklist; этот инкремент не закрывает весь блок1.

## New quantity matrix 2026-10-16

CASE1142 completed new CLAIM/START, BOX24/EA1 pick and CLOSE/replay: foreign-home WARE1 flat plus explicit WARE20220394 role, classifier legacy0/scoped1. Actual HTTP CLOSE replay returned403 after role revocation while the flat right remained. See [[retailcase_hu_thermal_admission_20261016]]. Other manager/driver/finance/delegation guards remain open.
