# NI06.2: точное размещение и восстановление возврата

14 октября 2026. [Отчёт](../../reports/nicora/2026-10-13/codex/NI062/report.md).

После [[nicora_ni062_return_route_20261014]] завершён переход от server-confirmed приёмки к существующей очереди размещения с exact receipt_operation_id. Аддитивный optional filter existing GET применяет bind equality до limit100 и сохраняет склад/права/not-placed. Завершённый или отсутствующий возврат не выбирает другую паллету. Подтверждённое создание задания даёт exact task_id.

Существующие receive/putaway journals сохраняют исходный запрос при неизвестном/чужом ответе; corrupted raw блокирует POST до явного readback архива и текущего GET. Нового журнала команд нет. return-mark-draft также архивирует повреждение до очистки и отвергает чужое изменение. Native бизнес-логика/DDL не менялась.

8 browser checks PASS, реальные GET + modeled POST (реальных0); native historical result прочитан из Oracle. Live optional GET после рестарта: нужный pending1, placed/missing/другой склад0. ExactSQL2rbsv71aszfp3 3.803мс,126buffers/11executions; новый индекс не требуется, V$SQL_PLAN недоступен. Общий gate принимает ведущий. Внешние SAP/Track&Trace ACK, аппаратура и независимая приёмка отдельно от готовности кода.