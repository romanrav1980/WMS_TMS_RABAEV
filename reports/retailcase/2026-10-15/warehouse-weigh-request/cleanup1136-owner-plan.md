# CASE1136: последующая компенсация и границы metadata cleanup

Состояние после разрешённого ONE ASM PICK1EA: исходный UID23/H0, CASE child1/H1 в CPT; новые quantity-команды требуют root release. Exact replay AFTER дополнительных эффектов не создаёт.

Штатная последовательность физической компенсации: CASE_CARRIER_RETURN на исходную ячейку QIPcdbf4c0962 → WAVE_CANCEL567 → PICK_PLAN_CANCEL2199. Возврат сохраняет отдельный child UID: требуемый итог — aggregate P24/H0 в исходной ячейке, parent23+child1, root origin300000034518661218 и неизменная история created_by Stockop. Объединять UID или править количества напрямую запрещено. Stock HARD1863 и legacy pick reservation2005 — разные сущности, итоговые активные удержания проверяются отдельно.

После пустого CANCELLED CASE1136 разрешённый владелец TARE_BOOK_CANCEL может закрыть HELD booking `WHREQ15.AK06.TARE.BOOK`, тип32/WARE13583852. API: POST `/api/inventory/tare/book-cancel` с новым operation_id и original booking_operation_id; право tare_plan. Native требует CASE NEW/ASSIGNED/CANCELLED и отсутствие положительных carrier lots. Затем canonical TARE_COUNT observed0 с актуальной balance version может компенсировать TEST count1 `WHREQ15.AK06.TARE.COUNT`. Нельзя отменять бронь до физического возврата CASE content.

Ресурс: session54/resource58/shift63, operator WHREQ15.OP. `ResourceManagementService.logout_session` → public `close_existing_resource_session` — штатный владелец CLOSED session54; guard отказывает при любом незавершённом warehouse/inventory/CASE задании. Вызывать после RETURN/CANCEL. Штатный close_shift в просмотренных service/ReachShifts не найден; shift63 сохраняется как TEST metadata, пока не подтверждён отдельный владелец. Не подменять его прямым UPDATE.

ST641520/row16727999/fulfillment190 (order2146, qty1EA) сохраняются как TEST история: RETURN снимает CASE binding/факт и возвращает fulfillment PLANNED0. Штатного cancellation owner этого внутреннего order/ST не найдено. Root явно принял retained TEST metadata/backlog; delete, произвольный CONDITION или ложное SAP происхождение не допускаются. Акторы/устройство/face выводятся из эксплуатации только существующими владельцами после приёмки; immutable captures/claims/events сохраняются.

Основание: native source/preflight и caller-rollback report, `opc1136-after.json`/`opc1136-after-replay.json`. Этот документ — read-only plan, не запись об исполнении компенсации. Физические весы/складской подбор не заявляются.
