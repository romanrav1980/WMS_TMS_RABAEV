# NI04.1 — исполнение CASE при смене физического слота

1001 PREPARED: текущий RRL_STOCK_HU_SLOT_MOVE_CMD (capture1000) повышает CONTENT_VERSION прямого CASE при HU_RELOCATE_SLOT, не повышая PICKED_CONTENT_VERSION активного исполнения заказа. Используем прежний RRL_STOCK_CASE_BIND_MOVE, текущий снимок binding в плане, ST/FF ключи и согласованный ST-before-CASE actual row order. Перед записью проверяется frozen binding, затем CASE/FF версии меняются вместе с прежними placement/claim/HARD coverage в Root. Количество не изменяется.

Контейнер между слотами повышает только собственную версию; версии вложенных CASE не повышаются искусственно. Slotted unpack/repack уже вызывают HU_CMD и получают binder993 через прежнее проксирование. Captures/SHA/rollback сохранены, применение и адресный действующий bound CASE сценарий pending. ПолныйNI04.1 не закрыт.

## Checkpoint1014 — применено

1001APPLIEDVALID. Actual1002 retained987 CASE1131/FF10/slot224/1143DONE_SYNC, rootHU8+CASE12/P20H20/rollback/replay. UI1004shared durableintent/correlation/damagedarchive;1007scoped readonly placement/currentread1008/HTTP1006; internalCASE1012. SQL1013placement3.508ms15.2buf/binding.235/.161, keepkeys+2row bound. [Отчёт20](../../reports/retailcase/2026-10-13/20-case-slot-report.md),screens22–23. FullNI04.1open.
