# CASE return scope: неверная колонка в native guard

16.10.2026, устранено. Owner Codex. Рабочая Oracle снова ERROR0/INVALID0, новая CASE1149 прошла RETURN25EA/rollback/replay/REV. Это ошибка реализации, не ограничение пользовательского сценария.

## Причина и эффект

В новом scope guard использован `RRL_CASE_CARRIER_LOT.CELL`, которого нет. Колонка CELL из соседнего SQL по другой сущности ошибочно перенесена на таблицу связей без проверки её колонок. Реальная связь хранит LOT_UID, CASE_PICK_TASK_ID/LINE_ID и provenance; текущая ячейка определяется через RRL_REMAINS.

CREATE OR REPLACE сохранил body с compile errors. Точный source SHA совпал, но последующий USER_ERRORS/INVALID gate правильно остановил migration до ledger. До исправления зависимые CASE-команды не могли выполняться. Начавшийся TEST TYPE завершился ошибкой до проводки; отсутствие операции проверено, новая команда вместо неё не создавалась.

## Исправление

Не повторялся исходный DDL batch. Отдельный frozen `2026-10-16_case_return_scope_completion` проверил точные3 установленных source SHA и исправил одну body: LOT_UID → положительные остатки → фактическая CELL/WARE. Проверены ERROR0/INVALID0/3SHA и оба ledger. Та же TEST фикстура продолжена с прежним TYPE operation_id после доказанного отсутствия эффекта; последующий RETURN подтверждён10HTTP/25EA.

Артефакты: `reports/retailcase/2026-10-16/case-manager-scopes/{compile-failure-inspected.json,root-apply.json,root-apply.stdout.txt,root-apply.stderr.txt,completion-apply.json,completion-readback.json,return-acceptance.json}`. Исходный frozen kit не изменён. После следующей single-load миграции текущую цепочку проверяет `finish-gate/oracle-current.json`, а не повтор старого apply.

## Правило для следующих native изменений

1. Каждый новый alias.column сверять с wiki/schema mirror; если колонка не подтверждена, один bounded USER_TAB_COLUMNS по точному TABLE_NAME до генерации kit. Не выводить поля из похожего alias, имени таблицы или соседнего запроса.
2. Новые SELECT guards предварительно проверить отдельно в READ ONLY с bind-параметрами и нужными join keys. Source hash доказывает тождество текста, а не его компиляцию или бизнес-корректность.
3. DDL запускать без параллельного TEST factory. Продолжение бизнес-кейса — только после отдельного успешного source/USER_ERRORS/INVALID readback; shell не должен запускать следующий шаг после ненулевого exit code.
4. При compile failure сохранять before/after/ошибки, запретить повтор неопределённого batch, выполнить source-guarded forward repair. Сверять исходный operation_id, затем продолжать сохранённый кейс вместо создания нового склада/пользователя/операции.

См. [[../database/retailcase_case_return_scope_20261016]], [[../database/oracle_change_protocol]].
