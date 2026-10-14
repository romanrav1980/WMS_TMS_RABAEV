# NI06.2 / 648: возврат неизменённой исходной паллеты

Для локальной Qwen, независимый прогон не выполнен. Source wiki/database/nicora_ni062_preserved_pallet_20261012.md, native639.

На собственном новом исходнике3EA/3physicalkeys/6codes выполнить original SAP/ST/load/depart/store acceptance. Профили CRPT PALLET-only + EGAIS BOX-only. Возврат полной неизменённой исходной паллеты с её прежним UID проходит approval/SAP/plan/handover/отдельного driverpickup/receive/PUT; P3H0, прежние3keys6codes, старый birth документ не переписан, новый return document связан отдельным receipt. Exact retries не повторяют движение.

Отказы: новый identifier со старым PALLET кодом, partial quantity/composition, UID другой approval, active stock/reserve/physical task/HU parent, CASE repacking history, original unit moved/repacked/changed profile, unit fallback для PALLET/BOX, regulatory invalidation. All side effects атомарны; late refusal/rollback не оставляют quantity/units/outbox. Current rights перед cached replay обязательны.

UI оба уровня BOX/PALLET соответствуют current profile; UNIT_OR_AGGREGATION допускает нужный уровень. Source/actor/API-scoped draft и pending original intent сохраняются. Не пересоздавать641/642/643/624 и не активировать retiredactors. Retained646 только read-only. Не объявлять новые gov коды, reaggregation или real govACK доказанными.
