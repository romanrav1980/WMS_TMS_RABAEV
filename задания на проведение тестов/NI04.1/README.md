# Qwen: складское дерево грузовых мест

Основания wiki/database/retailcase_ni041_hu_design_20261009.md, retailcase_ni041_hu_tree_20261009.md, retailcase_ni041_hu_move_20261009.md.050–051 APPLIED, полная приёмка открыта.

Проверить существующие pallet identities, parent no stock, leaf counted once, optional standard SSCC/internal UID. API/UI warehouse-hus packing/unpack version/reason/scans и user/API durable replay. Root guards запрещают циклы, второго активного родителя, отдельный nested P и прямой metadata DML. Проверить concurrent opposite/competing attach с ordered ancestors и rollback whole operation; авторский single-session случай не доказывает конкуренцию.

Перенос TOP→BOX→leaf5/H2: P/H/owner/units/journal/outbox/location/versions вместе, same-body replay once. Несколько SKU/BASE/партий/профилей маркировки не дают суммирования родителя и листа. Quantity summary по SKU/BASE; unknown weight=null, historical partial gross не использовать как фактическую массу.

На051 target ограничен пустым unrestricted ordinary storage, physical STORAGE_SLOT/weight/height/CASE adapters ещё не объявлены установленными. Такие запросы должны отклоняться; не обходить ограничение UNKNOWN измерением или zero claim. Active physical task и separate CASE lot packing запрещены.

Author scripts scripts/ni041_hu_tree_case.py, scripts/ni041_hu_move_case.py. Собственные fixture только, quantity cleanup через root после explicit unpack, link/op history оставить. Приложить SQL decision, реальный браузер/роль/reload evidence отдельно; не объявлять весь спринт завершённым.

## Existing task and physical slot052–053

Review scripts/ni041_hu_task_case.py and ni041_hu_slot_case.py. Use a private business warehouse; do not supersede the published topology of warehouse1. Verify plan/assign/start/complete1HU, exact replay, frozen slot/measures, version conflict/oversize/unknown legacy height unit/wrong slot scan, one parent OCCUPIED claim and unchanged leaf HARD owner. Return whole HU to empty work area before unpack and clean only own P/H through root. Check cancellation releases planned availability and two concurrent plans cannot occupy the same cell/slot. Do not claim multiple HU/cell, CASE packing, scale-device measurement, regulatory aggregation or independent driver acceptance from these author cases.

## Existing CASE inclusion054

Use ni041_hu_case_carriers_case.py as evidence, not independent acceptance. Check closed CASE12+8 packed under one existing parent, single-parent/versions/scan and physical same-location, whole20/H20, no new quantity rows, CASE location/version/events and exact replay. Standalone CASE movement/return/shipping while nested must rollback with the specific nested rule. Unpack before existing CASE return cleanup. Distinguish warehouse membership from CRPT aggregation; no fabricated external acknowledgements.

## 055–056 additions

Check current topology cell weight/volume (not just slot limits), height setting old caller preserve and explicit null clear; script ni041_hu_height_setting_case.py. Verify CASE preview never substitutes copied source gross or unknown CASE tare. Add independent competing CASE metadata/packing and10001 physical-unit boundary using isolated own fixtures; these two boundary cases were not executed by the author.
