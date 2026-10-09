# ORA-40573 в новой проводке

08.10.2026, RABAEV/orcl. Родитель: [[../database/nicora_stock_posting_extension_20261008]].

Oracle скомпилировал SELECT, использующий x.get_string(...) с PL/SQL JSON_OBJECT_T, но при выполнении compile_count вернул ORA-40573. Установка VALID не доказывала работоспособность команды.

В 16 runtime components методы JSON вычисляются перед статическим SQL и передаются typed local NUMBER/VARCHAR2/CLOB binds. Изменения представлены canonical SQL и фазой 114 с checkpoint/rollback; повторное применение и recompile завершились без ошибок. Raw sources сохранены.

Повторная попытка прошла прежнее место и остановилась на DIRTY_TRANSACTION: тест делал предварительный DML. Это нарушение самого тестового сценария. Предварительная запись ACTIVE откатилась, глобальная база осталась PREPARED, stock/events/operations 0. Нельзя объявлять проведёнными физический count, replay или concurrency.

Скрипт scripts/stock_posting_sql_json_binds.py — source maintenance, не runtime SQL callback. --emit выдаёт JSON для штатной UTF-8 записи PowerShell; --apply не используется при ограничениях Windows file broker. Inventory smoke теперь требует настоящий ACTIVE; постоянную активацию ради smoke до конверсии остальных writers не выполнять.
