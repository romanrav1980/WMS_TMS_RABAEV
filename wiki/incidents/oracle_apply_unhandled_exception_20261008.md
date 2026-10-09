# OracleApply: необработанное исключение при ошибке SQL

08.10.2026. Владелец указал на аварийное завершение приложения OracleApply во время полного перехода остатков.

## Причина и исправление

SqlPlusLikeRunner при --stop-on-error повторно выбрасывал OracleException, а top-level Program.cs не перехватывал его. Ожидаемая остановка SQL-миграции превращалась в Unhandled exception процесса и могла вызывать системный отчёт Windows о падении.

[Program.cs](../../tools/oracle_apply/Program.cs) теперь перехватывает OracleException, ошибки входных файлов/параметров и прочие исключения. SQL/connection failure возвращает 1, input failure — 2. Автоматического повторения нет; уже выполненный Oracle DDL не объявляется откатанным. Connection string и exception object не печатаются.

Первая сборка в прежний obj получила CS2012 Access denied. Без удаления каталогов собрали в runtime/oracle_apply_build, с UseAppHost=false: build succeeded, 0 warnings / 0 errors. [Установщик](../../scripts/stock_posting_apply.py) использует именно новую DLL, а не прежний executable.

## Проверка и ограничения

[Контрольный SQL](../../db/migrations/2026-10-08_stock_posting_core/052_oracle_apply_error_case.sql) выполняет только raise_application_error, без DML/DDL. Получен обычный exit 1, без Unhandled exception/stack crash. Затем новая сборка успешно применила 056 и 059, exit 0.

Это исправление обработки ошибок CLI; SQL-ошибки всё равно требуют исправления причины и проверки затронутых objects. Оно не делает DDL транзакционным и не означает завершение полного stock cutover. PREPARED сохраняется.
