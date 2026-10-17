# AK06-A: scoped TASK_COMPLETE
MIGRATION_ID: `2026-10-15-warehouse-task-scoped-complete`. **APPLIED** root:12statements/0errors. Readback7spec/body exact; USER_ERRORS=0/globalINVALID=0. [[components/retailcase_task_scoped_write_increment_20261015]], [[components/retailcase_warehouse_scoped_reads_20261015]].

## Контракт
Новый путь использует существующее warehouse_task_execute, область WAREHOUSE/SELF, фактический ASSIGNED_TO=actor и ordinary RRL_PALLETS.HU_KIND=STOCK без HU_CONTENT_VERSION/CASE carrier. Обе реальные ячейки разрешаются через RRL_CELLS; каждый склад должен разрешать execute. Сохранённый warehouse не противоречит ячейке. ExecuteA+viewB не разрешает движение.

RRL_WAREHOUSE_TASK_ACCESS.scoped_stock_executor — pure guard. RESOURCE_POLICY использует его только COMPLETE/actor=assignee; FORCE/session/qualification/shift и document guards сохранены. Legacy/HU/CASE ветви не расширены. Единственный writer — прежний canonical RRL_STOCK_POSTING_API → TASK_PLAN/CORE/DOMAIN. ACCESS_REV SHARE — после strict begin_plan, до policy/resource locks. Current permission проверяется также на replay.

Новый native запрос требует явные operation_id и expected_task_signature. Signature делегируется существующему TASK_PLAN.signature через ACCESS wrapper; в ACCESSIBLE BY добавлен только доверенный ACCESS caller, широких GRANT/копии алгоритма нет. Expected signature проверяется при компиляции нового запроса; committed exact replay не сравнивается с изменившимся после DONE UI snapshot.

## API
POST /api/warehouse-tasks/{id}/complete: identity → pure read-only preflight → canonical writer. Native разрешён только ordinary guard; legacy сохранён. Для original APPLIED receipt того же actor/task допускается отсутствие нового signature поля, если оригинальный контракт его не имел; native всё равно сравнивает неизменное тело.

GET detail после scoped view возвращает task_signature, список не получает N+1. Missing optional signature исключается из metadata, сохраняя старый canonical контракт. WarehouseTaskStatusRequest вынесен в существующий inventory/contracts.py, schemas.py сохраняет alias; baseline только уменьшен.

503 и OPERATION_CONFLICT не считаются подтверждённым отказом оригинальной команды. Ответ сохраняет operation_id и read_before_retry. Assign/start/cancel остаются отдельными flat маршрутами.

## Проверка
[Native/live HTTP](../../reports/retailcase/2026-10-15/resource-timeline/task-scoped-complete-native.json): **20checks total PASS**, не сумма с прежними13. Unit tests/retailcase/test_task_scoped_completion.py: **13PASS**.

Positive fixture: существующие DEV WAVE395/pick_wave_task1810/HARD reservation1376, FULL.QA:d9a5c53b54/P20/H20; временная assigned task/own qualified REACHTRUCK session/native-only actor. Physical completion APPLIED — caller-owned rollback. После rollback совпадают P/H/version и wave/pick domain facts; отсутствуют operation/movement/event/sync/residual/новый partial unit/RRL_EVENT_OUTBOX.

Committed replay — original NI032:PART:55edaf9dce, точный исходный CLOB. Исторический inactive QA actor временно получил native-only SELF; exact receipt вернулась, другое тело конфликтует, revoke403. USER_GROUP/DELETED/WARE_ID восстановлены точно.

Отказы: чужой assigned, missing/stale signature, wrong physical target scan, closure change после prepare, executeA+viewB и отзывB, HU/CASE. Live HTTP: native identity/detail/signature; correlation/version422; wrong scan проходит до native StockPosting и отклоняется409/rollback; assign/start/cancel/чужой assignee/HU403. Новый положительный HTTP stock commit не выполнялся: positive business execution проверен тем же native entry с caller-owned rollback.

Временная metadata **фиксировалась отдельно**, чтобы strict begin_plan начинался чисто, и удалена с explicit absence checks; native access audit/command receipts сохранены. Историческая QA identity восстановлена. Stock/резервы не фиксировались, NativeAPI.post не вызывался. Scripts: warehouse_task_scoped_complete_smoke.py, warehouse_task_scoped_extra.py, warehouse_task_scoped_http.py.

Двухсессионная конкуренция/revoke under lock и физическое оборудование отдельно. Инкремент не закрывает assign/start/progress, HU/CASE или весь AK06.

[SQL review](../../reports/retailcase/2026-10-15/resource-timeline/task-scoped-complete-sql.json): preflightavg3.642ms/10, helper3.623ms/18, signature4.503–8.989ms; metadata fixtures до336ms. Решение: PK/точные cell lookups/bounded canonical closure; дополнительных индексов не требуется.

Verifier scripts/store_app_verify_oracle.py: union12актуальных source store/wave/TASK, единственный latestPosting; PASS/INVALID0. Architecture962/0/72 и24toolingtests, encodingPASS. Общий gate пока остановился на параллельном Claude admin UI typecheck (mock session_id; Filters waveId/waveLabel); это не backend ошибка и не общий frontend PASS.

Первая неудачная попытка apply → rollback → restorative compile сохранена в component page/checkpoint. Исправленная APPLIED редакция её не стирает.
