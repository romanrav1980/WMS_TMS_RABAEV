# NI06.2 — вывоз возврата существующим рейсом
Ticket094, 10.10.2026. [Решение](nicora_ni062_return_transport_design_20261010.md), [SQL](../../db/migrations/2026-10-10_ni062_return_transport/apply.sql). 2026-10-10-094-store-return-transport-plan APPLIED; command/root/body/guard VALID.

STORE_RETURN_TRANSPORT_PLAN связывает original approval+SAP-return с существующим RRL_TRANSPORT_TASK/driver/vehicle/store и SAP receiving warehouse. Второй writer назначения СТ не создан. Только активный текущий рейс, фактический водитель, существующий магазин на маршруте. Conservative capacity включает все фактические outbound places/mass и все planned returns, без предполагаемого освобождения кузова после receipt. Same TT/vehicle row declarations и locked recheck, immutable plan+outbox.

API /api/delivery/store-return-transport: eligible bounded100, plan, trips/{id} bounded200. ARM [store-return-transport.html](../../wiki-raw/wms_admin_ui_reference/store-return-transport.html), store_return_transport. Pending exactbody/ID saved before send; definitive rejection separate from unknown result. Status PLANNED_PICKUP, physical_pickup_confirmed=false; P/H не меняется.

Авторский case actual own SUPPLIER approval/source bea258a7dd/SAP warehouse9104: oversized capacity refused; configured original own fixture vehicle had no spare mass/slot and correctly refused2kg1place. Through configuration API explicitly set own vehicle allowance outbound+2kg / outbound+1place; plan then APPLIED, replay/duplicate/direct-delete refusal passed, outbox1/events0. This metadata change belongs only to author fixture. No claim actual pickup/returned warehouse goods.

Slow SQL eligible10.190ms average, insert18.672ms, trip15.176ms. Решение: trip/index, bounded100/200 и исходные existing vehicle/TT rows; no global store lock. Capacity here admission snapshot; later actual pickup must recheck current load/vehicle, current source/route and capacity. Planned route edit is not preserved physical admission.

Открыто: actual store/driver handover, authenticated driver binding (legacy anonymous driver_id not proof), warehouse receiving/placement, explicit cancellation/replan, marked lifecycle. Полный NI06.2 не закрыт.
