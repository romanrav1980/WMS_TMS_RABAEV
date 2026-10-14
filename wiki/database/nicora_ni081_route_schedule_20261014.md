# NI08.1-R1 — единый маршрут, отдых и утверждение времени V6

14.10.2026. Authoritative calculator: `RABAEV.RRL_TT_ROUTE_SCHEDULE`. Миграция `2026-10-14-ni081-route-rest-approval`, [SQL/checkpoint/rollback](../../db/migrations/2026-10-14_ni081_route_rest_approval/), [отчёт](../../reports/nicora/2026-10-13/codex/NI081/REPORT.md).

## Поведение

Предварительный просмотр окон и окончательный `RRL_TT_TIME_API.approve` используют один native calculator. Прежний Python `domain/delivery_windows.py` удалён. Назначение СТ вручную или solver остаётся проектом до общего утверждения времени; автоматического допуска к выезду это не даёт.

Расписание: направленная дорога → отдых15 после120 минут вождения → ожидание окна → разгрузка → существующий LOAD_RETURNS → обратная дорога. WAIT/UNLOAD не обнуляют вождение. Сохраняются предрейсовые/послерейсовые операции, резерв планового интервала отражается WAIT. Неизвестный вид промежуточной операции требует явного mapping вместо молчаливой потери работы. Проектный лимит540 минут — не утверждение о законодательстве. Предшествующая работа вне WMS остаётся непроверенной.

Только настроенная база склада, current ROAD_PROFILE_ESTIMATE не старше24ч, однозначный адрес и норматив, пересечение окон СТ. Жёсткое окно блокирует; мягкое предупреждает. ST_NUMBER строковый, включая SAP_2135. Паллеты одного адреса объединяются по минимальному ORD. Расчёт должен укладываться в существующий ARM интервал возврата, иначе требуется исправить план через существующие команды.

## Транзакция и подпись

Существующий CONFIG X → TT → текущие ADDR sorted → направленные matrix pairs sorted, row wait5. Затем свежий source snapshot: member windows, destination norms/TW_STRICT, операции, складская база, дорога/provider/UPDATED_AT/freshness и policy identity `REV55_ROUTE_V6_120_15_540_ROAD24H`. Результат клиента не принимается как proof. Изменение существующей дорожной строки ждёт row lock; после изменения source hash устаревает.

Под той же fence проверяются опубликованные интервалы ресурсов и цепь того же водителя, лимит непрерывного вождения и сутки в выбранном часовом поясе. Только явный REST сбрасывает непрерывность; неизвестный промежуток не приравнивается к отдыху. Граница200 рейсов/2000 операций сохранена; превышение отказывает. Покрытие — текущие source-approved планы WMS, а не вся фактическая занятость водителя.

Единственная запись — прежний immutable `RRL_TT_TIME_APPROVAL.RESULT_JSON`, теперь source_contract_version6 и route_schedule. Ранний exact replay прежней команды сохранён. Старые approvals с другим source hash требуют повторного согласования. Товарные таблицы, права и механизм выезда не изменены. Диагностика использует подтверждённые segments только при current source и отсутствии факта; фактические операции не заменяются прогнозом.

## Применение и проверка

OracleApply UTF8, оба пакета VALID, USER_ERRORS/INVALID=[]; ledger APPLIED. Положительный final approve на собственном planning-only TT33641 завершён, затем rollback: approval version0/NO_APPROVAL. Синтетические дороги отмечены provider NI081TEST, новые адреса NI081.BASE/SHOP, existing WARE9102; setup metadata committed отдельно из-за обязательного clean transaction. Остатков/движений/товарных строк не создано; B01/B02/33564 не менялись. Изменение own road после чтения source отклонено `TT_TIME_SOURCE_CHANGED`.

9 ограниченных native readonly случаев; actual React components с real GET/API/native, видимый REST, без POST из browser; screenshot в отчёте. Общий gate/encoding выполняет ведущий после интеграции.

## SQL

Дорожный batch ≤201 пары. После измерения39.197мс/2282 buffers на вызов добавлен leading/use_nl/index по существующему PK_DIST_MATRIX(FROM_ADDR,TO_ADDR):6.882мс/15buffers, HTTP105мс. Новый индекс не нужен. Peer query24.082мс/73buffers, stop JSON1.108мс; bounded selection сохраняется. Это адресные замеры, не нагрузочная гарантия; actual V$SQL_PLAN не заявляется.
