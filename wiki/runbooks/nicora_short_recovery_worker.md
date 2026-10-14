# Локальное восстановление CASE shortages

09.10.2026. [[../database/nicora_ni032_task_recovery_20261009]].

Прежняя RABAEV/orcl, единое ACTIVE stock-ядро. Фоновый обработчик использует существующие SHORT/INVENTORY/WAVE/WAREHOUSE/CASE документы. Изменение количества выполняет только RRL_STOCK_POSTING_API. Схемы NICORA и дополнительного экземпляра базы нет.

Запуск из C:\projects\TMS:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-short-recovery.ps1 -Actor <существующий пользователь>`

Actor задаётся явно. В dev запущен admin; для постоянной эксплуатации настроить отдельного существующего пользователя с необходимыми правами, не переносить dev credentials. Текущие действия требуют case_pick_short_approve, pick_wave_launch, resource_dispatch_manage, warehouse_task_assign/execute и другие права соответствующего stock command.

Launcher запускает Python скрыто, использует старое локальное окружение, не печатает credentials. Повторный запуск сопоставляет PID и время старта из runtime/short_recovery/worker.json; второй процесс не создаётся. worker.out.log содержит результат обработки, worker.err.log — ошибки процесса. PID-файл сам по себе не использовать для завершения: PID может быть переиспользован. До остановки сверить processId/startedUtc.

Обработчик выбирает по одному WAIT_INVENTORY/WAIT_REPLENISHMENT в LAUNCHED волне, с lease45s и retry5s. После рестарта сохраняется frozen SOURCE operation/body. Закрытые/cancelled волны не обрабатываются. Нет свободного допущенного аудитора/ричтрака с позицией не старше300s → ожидание с причиной; назначение не меняет запас. Ошибки сохраняются в SHORT и доступны в recovery monitor. Исходный deadline не перезапускается.

Монитор: `http://127.0.0.1:8088/wms-admin/case-pick-management.html`; страницы inventory и warehouse tasks используют прежний admin shell. API recovery-shorts показывает состояние/срок/ошибку, replenishment-progress — фактическую подачу отдельно от остатка заказа. /api/resources — действующие ресурсы/сессии; resource-management.html использует реальные данные, demo только при явном demo=1.

Перед сменой Python handler или откатом Oracle сначала остановить worker в спокойной очереди; применить matching application code и миграции в обратном порядке. Откат не удаляет журналы/scan evidence/единицы. Некоторые rollback требуют отсутствия несовместимого retained state и могут отказать; отказ не обходить удалением истории.

В процессе разработки адресные fixtures выполняются с остановленным loop worker, затем worker запускается снова. Это исключает гонку fixture runner с самостоятельным background назначением; настоящая конкуренция проверяется отдельно по задаче.

Остаток эксплуатации: полноценный service supervisor, least-privilege account и промышленная duty/minimax policy ещё не подтверждены. Текущий скрытый локальный процесс — dev runtime, не Windows service и не обещание промышленной готовности.

Loop DB claim/reconnect ошибки журналируются без credentials, retry ограничен30s; PermissionError завершает процесс с кодом2. Graceful сигналы завершают цикл после текущей операции; принудительный Stop-Process требует штатного rollback/lease recovery и не является graceful API.

Штатная локальная остановка: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\stop-short-recovery.ps1. Команда сверяет PID/startedUtc и ставит worker.stop в runtime; процесс выходит после текущей итерации без принудительного разрыва commit. При очередной задержке ожидание может занять до30s плюс текущую операцию. Перед повторным start убедиться, что старый процесс завершён; launcher убирает старый marker только при отсутствии соответствующего running worker.
