# Сборочный пост: связь с отгрузкой

APPLIED5/0 `2026-10-15-assembly-shipping-context`, owner inventory. Additive read-only projection в RRL_ASSEMBLY_SCALE_API.context после прежнего assert_task; права и writers не меняются. Источник — текущие CASE/customerorder/WARE, существующие fulfillment и СТ, не выдуманный SAP заказ.

Поля: resource_session_id/assigned_resource_id для mass-free EMPTY request; shipment_binding_state REQUIRED/BOUND и bound_pallet_identifier; до20 prepared_shipments только того же заказа и actualWARE, PLANNED/PICKED, не чужаяCASE/возврат/закрытаяСТ; final_composition_signature из прежнего QC status owner после фактической привязки. Это навигационные кандидаты, не доказательство совместимости: bind_existing_case_shipment повторяет physical composition/currentversion/carrier проверки.

Сборка создаёт CASE_CARRIER_LOT, закрытие CASE само не создаёт и не привязывает СТ. Порядок: подготовленнаяСТ/fulfillment → отбор → canonical close → existing bind → fresh FINAL_GROSS → finish. Ни второй stock writer, ни прямой UPDATE legacy binding не добавляются. Для isolated1136 metadata подготовлены ST641520/fulfillment190,1EA/FACT0; товары не списывались.

[Миграция](../../db/migrations/2026-10-15_assembly_shipping_context/apply.sql): свежий intent+WH ASM before-image/hash, checkpoint, paired package rollback, compile/INVALID guards. Root apply5/0/source EXACT/errors0/INVALID0 завершён; actual close/bind ST641520 прошёл. Последующий ASM_FINAL forward добавил отдельную identity собственного OPEN ASM, сохраняя ordinary shipping guards: [[retailcase_assembly_final_snapshot_20261015]]. Аппаратная приёмка и SHIPPING_GROSS всей паллеты отдельно.

