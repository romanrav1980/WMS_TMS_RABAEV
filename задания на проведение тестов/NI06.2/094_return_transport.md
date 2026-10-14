# Qwen ticket094
Источники wiki/database/retailcase_ni062_return_transport_20261010.md, scripts/ni062_return_transport_case.py. Уже привязанный approval не использовать повторно.

На собственном ordinary approved+SAP return проверить existing trip/store/driver/vehicle, recipient SAP warehouse, frozen plan data. Не создаётся СТ или новое назначение outbound order. Отказать noSAP/foreignstore/closedtrip/blockedvehicle/missingcapacity/oversize. Верхняя оценка = all outbound + all planned returns + new return, inclusive configured limits; nested boxes не отдельные машиноместа.

Exact retry/conflict/duplicate plan/direct mutation, outbox1/events0/P unchanged. Simultaneous plans against same TT must serialize/recheck; snapshot conflict no partial record. UI retains exact pending intent on unknown response, actor switch clears data. Planned pickup is not physical custody. Slow SQL decision after meaningful case.
