# NI05.2 — факт погрузки и отдельное разрешение выезда
Задание077,10.10.2026. Не установлено; design/ticket, последующие результаты отдельно.

Требования NS46/47/48: existing ST.TRANSTASK_ID — единственное назначение; RRL_TRANSPORT_TASK/VEHICLE/TT_DOCK/TT_LOAD_TASK/TT_OPERATIONS — существующий рейс, машина, ворота, окно и план. План и can_print не подтверждают физическую погрузку. В текущем close_task исключение can_print проглатывается; сам legacy can_print возвращает ok при исключениях. Ни один из них не пригоден как фактический допуск.

Изменение: HU_SHIP с явным loading context фиксирует скан верхнего HU, машину/рейс/ворота/оператора/время/состав/измерения и exact member STs в одной root транзакции со stock consumption, FF/CASE, journal/outbox. Таблица физических фактов RRL_TT_HU_LOAD_FACT и связей ST дополняет existing load plan, не заменяет назначение. Ручная техническая HU_SHIP без loading context не считается фактом загрузки и не разрешает выезд.

Скан машины и ворот соответствует фактическому назначению TT; все member STs обязаны принадлежать этому рейсу, current warehouse/dock. Независимые места не удваиваются: верхнее HU =1, вложения не добавляют мест. Свежие SI измерения current composition обязательны; vehicle PALLETS/MAX_WEIGHT_KG ограничивают сумму loaded places/mass. Unknown capacity blocks confirmation. Окно TT_LOAD_TASK остаётся планом, не фиктивным фактом.

Actual-row order для погрузки: vehicle → TT → dock → sorted ST → sorted CASE; logical closure глобально acquired root заранее. Соответствует existing TT assignment lock TT→ST; direct vehicle/dock updates сериализуются actual-row locks. Frozen inputs проверяются до любой leg. Root owns commit; внешних вызовов/ожиданий в транзакции нет. Actor/right stock_posting_shipping current authority; выезд transport_dispatch_close.

TRIP_DEPART — root metadata command с stable operation_id, all assigned STs physically loaded/current vehicle+gate, no pending goods, min/max physical-place load and weight. Отдельное событие departure; stock не списывается второй раз. Existing close_task delegates it; exception cannot allow departure. Active loaded member ST/vehicle/dock cannot silently change; confirmed unloading/stock compensation must be completed in a subsequent explicit ticket.

API/ARM показывают actual loaded places and pending member STs, сохраняют retry intent. Module transport owns load/departure data; inventory public posting contract injected in composition root. Current QC/marked composition/production-ready gate reused. Государственный operation-specific ACK остаётся NI04.3 и не имитируется; industrial/full sprint acceptance not claimed.

Target fixture: existing actual FULLPAL3/ST bound to private TT/vehicle/dock, topHU loading→P/H0+one fact/replay; wrong vehicle/dock/trip/capacity denied; missing assigned ST blocks departure; complete assignment permits one departure without additional quantity journal. Own cleanup only. Slow SQL decision after case, no broad loads/snapshots.

Recovery: checkpoint affected package/API sources, additive schema and explicit guarded rollback/forward recovery; no deletion of physical history.
