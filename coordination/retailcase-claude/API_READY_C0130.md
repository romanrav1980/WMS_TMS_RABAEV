# API_READY_C0130 — TRADECASE T02

19.10.2026. Реальный API: http://127.0.0.1:8088. Авторизация — действующий Basic через apiFetch/SessionGate, не собственное хранилище паролей. Сервер проверяет RRL_ACCESS_API в области склада на каждом чтении. GET требует tradecase_view; этот код нужен только в техническом приложении. Admin имеет текущий GLOBAL_ADMIN. Промышленная SAP/ITMS/L4 не подключена; очередь обратных ответов не означает успешную доставку.

## Готовые GET

- /api/tradecase/warehouses/{warehouse_id}/site
- /api/tradecase/warehouses/{warehouse_id}/documents/{kind}?after={last_id}&limit=50
- /api/tradecase/warehouses/{warehouse_id}/documents/{kind}/{document_id}
- /api/tradecase/warehouses/{warehouse_id}/messages?after={last_event_id}&limit=50
- /api/tradecase/warehouses/{warehouse_id}/messages/{event_id}

kind: OWNER, SKU, RECIPIENT, ORDER, TRIP. Сегменты и курсор кодировать URL-функциями. limit 1–100, after — последняя строка предыдущей страницы, не числовой offset. Ответ страницы: items, has_more, next_after плюс метаданные площадки. Смена фильтра/склада сбрасывает курсор. Каждый запрос должен иметь AbortSignal и защиту от запоздавшего завершения.

site: warehouse_id, source_id, active_skm, planning_source (SAP/INTERNAL), enabled (boolean), version.
Документ списка: document_id, version, status (ACCEPTED/CANCELLED), payload.
Карточка: метаданные площадки + document_id, entity_type, document_version, payload.
Сообщение списка: event_id, entity_type, document_id, version, result.
Карточка сообщения: метаданные площадки + request (исходный envelope), result.

result: warehouse_id, document_id, entity_type, version, status ACCEPTED/REJECTED, replayed, stock_changed=false, physical_execution=NOT_STARTED, outbox_id, external_delivery=PENDING, external_business=NOT_CONFIRMED, необязательный code ошибки. schema_version/event_id/correlation_id/source_id/target_source_id/occurred_at — технические поля. В UI показывать «Принято основание»/«Отклонено»; «Ответ в очереди» отдельно от «Внешний ответ не получен». Не писать «выкуп выполнен» из ACCEPTED.

## Поля payload

OWNER: entity_type,title,active.
SKU: title,base_uom=EA,units_per_box,permitted_mrc[],active.
RECIPIENT: title,target_owner_id,permitted_source_owners[],buyout_mode (BEFORE_PICK/AFTER_PICK/IN_TRANSIT),osg_basis (SHIP_DATE/DELIVERY_DATE),lead_time_days,min_osg_days,allow_partial_pick/ship,allow_broken_box,active.
ORDER: recipient_id,order_kind OUTBOUND/TOPUP,parent_trip_id?,planned_ship_at (ISO с timezone),cancelled,lines[]. Строка: line_id,sku_id,source_owner_id,target_owner_id,mrc,quantity,uom BOX/EA,min_osg_days.
TRIP: vehicle_id,planning_source,planned_departure_at,capacity_kg,capacity_m3,cancelled,orders[{order_id,line_id,quantity}]. Маршрутные точки/геометрия ещё не готовы: не дорисовывать их как факт.

Числа Decimal в JSON могут быть строками. Сравнения версии — числа. Время выводить компактно с часовым поясом в подсказке; не заполнять половину экрана техническим ISO. Связь с названием товара/собственника разрешается через полученные страницы; не выполнять N+1 на каждую строку. При отсутствии карточки показывать исходный идентификатор как документный номер, не выдумывать название.

Ошибки: 401 — новая авторизация; 403 TRADECASE_ACCESS_DENIED — очистить данные; 404 TRADECASE_NOT_FOUND — площадка/документ не найдены; 409 бизнес-ошибка; 422 формат; 503 TRADECASE_RESULT_UNKNOWN — результат не подтверждён. Ты выполняешь только GET, не повторяешь POST/PUT.

Доказательства root: runtime/test-evidence/tradecase/2026-10-19/T02/document-acceptance.json, свежий склад 193511607. 29HTTP: дубль, конфликт, версия, параллельность, отмена, отзыв роли, сохранённый отказ и общий rollback документа/receipt/outbox PASS. Девять unit contracts PASS. Ошибки/неподключённые внешние системы не объявлены готовыми.
