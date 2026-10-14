# NI03.3: физическое исполнение и подготовленная СТ
09.10.2026. Первый ограниченный increment031 APPLIED в RABAEV/orcl. NI03.2 ещё имеет остаток; NI03.3 начат связанным ticket, ни один полный спринт этой записью не закрывается.

## Поведение
Existing CASE shipment binding повторно использует прежнюю СТ, без создания новой. Полный физический состав сверяется с её строками точным переводом в BASE. Только после успешной сверки одна metadata transaction устанавливает связь CASE→ST, fulfillment.PICKED, фактический состав/единицу/версию/время/автора и immutable SHIPMENT_BOUND event.
Добавлены в прежний CUSTOMER_ORDER_FULFILLMENT: FACT_COMPOSITION_JSON, FACT_UOM, PICKED_CASE_TASK_ID, PICKED_CONTENT_VERSION, PICKED_AT, PICKED_BY. Общий FACT_QTY заполняется только при одной общей BASE единице; смешанные штуки/килограммы сохраняются по SKU/единице без ложной общей суммы.
Exact replay проверяет shipment и сохранённую content version, возвращает сохранённый состав. Изменённая версия отвергается. Подготовленная СТ сама по себе PLANNED.
Root CASE_CARRIER_RETURN заранее включает fulfillment rows в closure; возврат в той же quantity transaction сбрасывает текущую fulfillment projection в PLANNED/0, сохраняя исторический SHIPMENT_BOUND и root movement journal.

## Чтение заказа
GET /api/customer-orders/{id}/execution с customer_fulfillment_view показывает requested/picked/remaining/HARD по строкам. Физический факт: root-created CASE lots (без умножения профилей маркировки) и BASE journal physical FULL_PALLET move. Отменённые CASE/tasks исключены. Prepared legacy ST не является источником picked quantity. Нет точной UOM policy → REQUIRES_UOM, единица не угадывается; HARD не вычитается второй раз из picked/remaining.
Одна Oracle snapshot ограничена2000 lines. Карточка customer-orders показывает причины ожидания/частичности/отказа и отдельный физический состав fulfillment. Прежние документные статусы не переписываются чтением.

## Авторское dev-подтверждение
scripts/ni033_physical_fulfillment_case.py: CASE941/WAVE247, собственный fixture. До физики PLANNED, progress0; root CASE3 → progressPICKED3; bindingPICKED/EA3/composition/version; exact replay создаёт одно событие; другая версия отклонена. Root возврат → current fulfillmentPLANNED0 и progress0; историческое событие сохранено, свой запас восстановлен.
Первоначальный fixture клонировал всю legacy ST row и получил timeout; это не было доказательством ошибки триггера. Existing insert trigger лишь присваивает ID/date. Fixture заменён минимальной собственной ST, исправлен reserved bind :uid→:p_uid, ранний cleanup больше не должен скрывать исходный отказ. Широкий набор тестов не запускался.
Новый read API:9b614j8n89fhd avg27.49ms/4exec; bind/read4.48ms, fact update5.15ms, return reset5.14ms. Решение owner fulfillment: сохранить bounds200/2000 и существующие keys; correlated fact subqueries переписать на preaggregated bounded joins при steady>500ms. Промышленная мощность не объявлена.

## Остаток
Full pallet provenance в fulfillment, partial/refusal shipping layout без изменения исходного спроса, wave/document завершение и рабочие причины; независимая/Qwen приёмка. Альтернативный pick face связан с существующим dynamic assignment и NI04.2; не создавать второй планировщик.
Источники: migration2026-10-09_ni033_physical_fulfillment, inventory/infrastructure/case_shipment_binding.py, inventory/domain/fulfillment_fact.py, fulfillment/api/execution_routes.py, fulfillment/infrastructure/execution_progress.py, customer-orders + order-execution.js.
