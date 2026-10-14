# NI05.2 — фактическая погрузка и отдельный выезд
10.10.2026.077 APPLIED RABAEV/orcl. transport owns load/departure facts; inventory owns existing shipment/P/H. Transaction owner RRL_STOCK_POSTING_API, one commit/journal/outbox. [Ticket](retailcase_ni052_loading_design_20261010.md).

## Сохранённый результат
HU_SHIP с loading_context проверяет existing TT/ST assignment, машину/ворота/сканы и новые SI measurements/current version. Верхнее HU =1 physical place; вложенные CASE/FULLPAL не добавляют мест. PALLETS/MAX_WEIGHT_KG actual vehicle limit apply to current loaded aggregate; неизвестная вместимость блокирует команду. Факт RRL_TT_HU_LOAD_FACT и exact ST members сохраняются атомарно с existing ST shipment. TT_LOAD_TASK остаётся существующим планом.

TRIP_DEPART проверяет все assigned STs, completed actual loading operations/current vehicle/dock/driver, physical min/max load и массу. Missing ST оставляет рейс ждать. Выезд переводит actual TT в «Отгружен», load facts в DEPARTED, создаёт root event/outbox, не списывает P второй раз. Legacy close_task delegates this gate; can_print exception no longer allows departure. Original can_print found fail-open and is not authoritative proof.

Actual-row order vehicle→TT→dock→sorted ST→CASE, matching existing assignment TT→ST. All logical ROW/HU/UNIQUE closure declared before root execution. Measured/current assignment rechecked before effect and ST membership after effect before commit. Facts/member history immutable; loaded ST/trip vehicle/dock cannot silently reassign without confirmed unloading. Existing assignment remains sole ST.TRANSTASK_ID.

## API / operator
/api/transport/loading/{task_id}/status, /confirm, /{task_id}/depart; existing /api/admin/transport/tasks/{id}/close wired through injected TransportLoadingPort. Auth RUSERS/right stock_posting_shipping or transport_dispatch_close, actor server. Typed API→port→infrastructure and app composition root inject existing stock poster. No second Oracle quantity engine.

Raw [ARM](../../wiki-raw/wms_admin_ui_reference/transport-loading.html) shows actual physical places/pending STs, separate loading/departure, current composition/manual SI and persisted exact retry. Existing trip ST view retains actually loaded STs after CONDITION2.

## Evidence / boundaries
Author scripts/ni052_loading_case.py passed: native FULLPAL3/ST/BOX/TOP whole move→one actual load/current private TT/vehicle/dock/P0H0/replay. Wrong machine and101kg over100kg denied unchanged3/H3. Pending second ST blocks departure; loaded vehicle/ST reassignment denied; removing only unstarted pending assignment permits separate departure/replay, qty journal0. Other owned pallet3/H3 preserved and own cleanup P/H0. OpenAPI and JS syntax checked.

077 is bounded slice, not full NI05.2 acceptance. Standalone CASE/ST loading without outer container, already logically shipped legacy reconciliation, confirmed unloading/stock compensation, staging-task link, external operation-specific regulatory/recipient ACK gates and independent mixed/marked/concurrency/browser evidence remain. A technical old HU_SHIP without loading_context is not a physical load fact and cannot authorise departure. Existing production-ready/unique-mark QC gates remain; local fact is not governmental ACK.

## Schema / recovery
Legacy TT/vehicle/ST had unique indexes or no ID constraint, unsuitable for FK. Added ID UKs; TT duplicate-key discovery found none, vehicle/ST existing unique indexes reused; new TT ID index supports keyed access. Source facts have FKs to actual identities and immutable stock operation. No original data or journals deleted. Schema mirrored in077, current bundle maintained; never full bundle reapply on ACTIVE. Checkpoints373/374. Backward rollback explicitly refuses unsafe old departure; forward repair preserves physical history.

Full operational capacity and completion of all sprint scenarios not claimed.

Slow SQL077: status join c3c27q6rx11j4 28.659ms/1, history2a9qvnkfuptb9 16.842ms/1, departure missing-member0uh139dc964ps 14.948ms/2; vehicle-other-open query3hbmqtq1n66ja10.778ms/1. Decision: keep TT/status and201 windows; add077 indexed vehicle/status/trip and ST/active predicates to avoid full growing history scans under locks. DDL111ms/catalog27ms excluded; no load capacity claim. UI known4xx rejection can start corrected operation; uncertain503 retains exact intent.

615–616 уточнение по живому RRL_STOCK_HU_LOAD_CORE:14/57 берётся WARE_ID ворот рейса;35 ST обязан иметь тот же WARE_ID;68 это повторно проверяется под блокировкой;74–75 LOAD_FACT.WARE_ID записывается из ware_no. DEPART требует одинаковые ворота для всех мест. Один действующий выезд относится к одному физическому складу. Пункт о необходимости нового multiWARE-внутри-TT ядра был избыточным: агрегирование разных складов нужно между рейсами счёта и уже поддерживается scoped invoice/source/grouped sums. Ограничение native Q26 защищает существующий инвариант, а не отключает допустимый сценарий. Не расширять погрузку/проводку ради выдуманного требования.
