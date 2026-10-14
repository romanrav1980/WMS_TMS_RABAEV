# NI06.2 — фактическая складская приёмка возврата
Ticket096,10.10.2026. [Решение](retailcase_ni062_return_receiving_design_20261010.md), [SQL](../../db/migrations/2026-10-10_ni062_return_receiving/apply.sql). 2026-10-10-096-store-return-warehouse-receipt APPLIED. Return CMD/root/balance/location/QC item spec/body и guards VALID.

STORE_RETURN_RECEIVE принимает ordinary SUPPLIER/DISPOSAL по уже APPLIED pickup→handover→existing trip plan→SAP return→Supply Chain approval→original receipt. Current warehouse_return_receive и существующий RUSERS.WARE_ID или GLOBAL_ADMIN. Завершённая историческая передача остаётся действительной после увольнения водителя. Current required marking/profile не обходится: этот slice отказывается до точного unit/regulatory flow.

Фактические scan vehicle/pallet/blocked receiving cell, SKU barcode/unit or BOX, whole original BASE qty, original expiry, observed batch и gross/net KG. Для нового запаса fresh palletID≤50char/150byte, original STOCK_ORIGIN_UID и произведённая дата/цена сохранены. Отдельная return warehouse policy: supplier/disposal cells различны, same SAP warehouse, BLOCKED_FOR_ACCEPT0/REMAINS1/POPOLNENIE1. Это карантин через ячейки; доступность к резервированию false.

Используются существующие RRL_STOCK_BALANCE_CORE.apply_delta/write_leg; private ACL добавляет только return CMD. One Root transaction: fresh PP+P/H0+one journal leg+immutable return receipt+outbox. Нет фиктивной ревизии или новой закупки. Обнаружен legacy обязательный PRIHOD_NAKLAD_ID: сохраняем его non-null контракт, создаём реальный складской incoming header DOCUMENT_KIND=STORE_RETURN, positive existing sequence ID, immutable source approval/SAP return reference. В RRL_SAP_SUPPLY_ORDER запись не создаётся. Existing header writers используют explicit column lists и не были переписаны.

Barcode resolver выделен из существующего RRL_STOCK_QC_ITEM в resolve_barcode; QC и receiving используют один authoritative lookup unit/box/ambiguity. Qty entered as BASE independently, hidden BOX multiplication нет. Calendar conversion даёт business denial для invalid date. Новое optional scan_article исключается из canonical defaults для replay старого принятого запроса; новые операции требуют barcode.

API /api/inventory/store-returns: warehouse policy/current scoped queue100/receive. ARM [store-return-receiving.html](../../wiki-raw/wms_admin_ui_reference/store-return-receiving.html), shell wms_admin_login + action rights. Original intent/ID stored before send, unknown result retained; new warehouse/source clears stale observations. Простая проверка формата до сохранения не подтверждает stock effect.

Actual author evidence:
- own bea258a7dd return1: separate non-admin warehouse-bound receiver, source/qty/expiry/cell denial; actual P1H0 blocked, original P0, event1/outbox1, typed positive return document/Russian text intact, exact API replay and immutable history.
- First author verifier stopped on reserved SQL bind :uid after successful commit; corrected to :lot_id and completed on original committed receipt, без новой проводки. Earlier failed staging attempts rolled back before any stock; NOT NULL legacy contract handled typed document.
- Fresh source04633c677f approved2→SAP→existing TT plan→admin store handover→dedicated bound driver→actual SKU barcode receiving2. Foreign barcode denied, same shared QC resolver actual2 scans passed; P2H0 blocked, replay/event1/outbox1.
- Own returned P totals3 in segregated zone. Driver bindings inactive, own users retired. Manual weight declarations and technical source fixtures, не hardware/SAP/Gov physical acceptance.

Slow SQL insert average9.891ms. Queue bounded by warehouse100, source/pickup/approval PK+unique; dedicated receipt warehouse/time index. Решение сохранить bounds and PK; mutable admission не кешировать. Warehouse queue fulltext was not found in sampled V$sql after DDL invalidation; no invented measurement/capacity claim. Owner inventory revisits source queue plan when real warehouse volume is available.

Следующий slice: существующее складское задание размещения по назначению и ERP подтверждение после actual placement; REUSE full box/source batch/expiry/picking flow, multi-place manifests and exact marked return remain open. Full NI06.2 in_progress.
