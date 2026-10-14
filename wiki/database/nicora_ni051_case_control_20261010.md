# NI05.1 — состояние контроля существующих CASE
10.10.2026. Миграции065/066 APPLIED в RABAEV/orcl. [[nicora_ni051_sampling_20261010]] и [[nicora_ni041_hu_case_20261010]].

Используется существующий RRL_CASE_PICK_TASK, без второго задания и без второй проводки. PLAN назначает CONTROL_IN_PROGRESS; полный действующий допуск — CONTROLLED (waiver PLAN — READY_TO_SHIP); ошибка — WAIT_CONTROL. Каждое изменение фиксируется существующим CASE_PICK_EVENT. Контроль не меняет CONTENT_VERSION, P/H или марки.

В BOTH проверка веса учитывает фактического неизменяемого ACTOR текущей root operation до APPLIED/commit. Контекст ACTOR для обычной проводки не является источником этого значения. Проверка независимости и после commit использует журнал операций и реальные picking facts.

Проверенный CASE внутри верхнего HU сохраняет результат контроля, но автоматическая отдельная отгрузка откладывается (whole_hu_shipment_required). Это не разрешение отгрузить верхний HU: его атомарная команда ещё в разработке. HU_READ допускает физически закрытый CONTROL_IN_PROGRESS.

Упаковка/распаковка отзывает подписи контроля всех CASE в затронутых parent/child snapshots, возвращает их WAIT_CONTROL и добавляет CONTROL_REVOKED. Перемещение целого HU сохраняет semantic approval состава. Неизменяемые прежние QC операции остаются историей. Логические ST/CASE ресурсы объявлены заранее; реальные ST строки блокируются по ID перед CASE строками по ID, как в shipping/QC.

Own native case12+8 passed: legacy wave/one whole replenishment/actual CASE picking/bind, HU staging20/H20, independent PLAN/SCAN/WEIGHT, BOTH first scan pending, CONTROLLED without composition-version change, failed weight WAIT_CONTROL, repeat same operation, nested auto deferred, unpack revokes both admissions. Собственные P/H убраны root-командами; документы/журнал сохранены. Остаток прежней неуспешной fixture6ff4b0adbb тоже убран отдельно, без общего сброса.

Slow SQL: существующий indexed CASE lookup2j6mxfbpar45s ~0.27ms/12; новые выборки ограничены HU200 nodes и keyed CASE/ST IDs. Решение — bounded tree/key lookups, дополнительные индексы не нужны по текущему case; миллион операций и независимая acceptance этим не доказаны.

Открыто: атомарная отгрузка верхнего HU, упаковочная/переменная масса, labels, approved corrections, terminal/native QC adapters, legal circulation/aggregation, независимая приёмка полного NI05.1.
