# NI06.1: агрегационные сканы целого многотоварного места

Checkpoint667, 12.10.2026. Подготовлено расширение существующего RRL_IW_GROUP_REC и GroupReceive API. До применения сохранён live package body666, hash manifest и paired rollback в [миграции](../../db/migrations/2026-10-12_ni061_group_aggregation/checkpoint.json). RABAEV/orcl выделен пользователем для dev; копия базы не нужна.

Единый native RRL_INTERWARE_MARK_SCAN уже умеет разворачивать зарегистрированные BOX/PALLET по прежнему RRL_IW_AGG_SCAN для нескольких legs. Group handler запрещал сам факт aggregation_scans до вызова этого validator; удаляется только этот запрет. Целый неизменённый состав/все товары/точные количества/сканы товара/текущие профили/исходные единицы/thermal guards остаются.

Для BOX/PALLET карточек запрещены прямые unit_scans соответствующих физических единиц, даже если другая партия того же профиля представлена агрегатом. Неприменимая маркировка не разрешает игнорировать лишний агрегат. Никакого нового дерева кодов и исполнителя количества нет: original atomic root receive/balance/unit/history/outbox не меняются. Внешний регуляторный ACK не предполагается.

После применения необходимы USER_ERRORS/VALID и адресное подтверждение: совместные UNIT+BOX/PALLET, полный состав, запрет чужого/неполного/неактуального агрегата и прямого fallback. Положительный физический цикл ещё не заявлен. Raw group UI aggregation controls пока не добавлены. Источник [[database/nicora_ni061_group_receipt_20261012]].

667 applied: первая компиляция выявила SQL-вызов метода JSON object; исправлено предварительным присваиванием CLOB. Live USER_ERRORS=[] / INVALID=[]. UI668 поддерживает UNIT/BOX/PALLET по текущим карточкам; одна ограниченная SQL-матрица scan_profiles, SOURCE_JSON неизменён. JS/architecture PASS. Fresh669 source — отдельный источник; protected404/405/406 не повторять.

Checkpoint674 prepared: смешанный case673 выявил глобальную проверку direct_scan по системе/профилю. QR одного товара ошибочно блокировал PALLET другого товара того же профиля. Общий native validator уточнён по текущему физическому UID; локальная копия правила удалена. Оба source/hash/paired rollback сохранены до применения; количество и блокировки не менялись.

## Actual673?675
667/674 applied; USER_ERRORS=[]/INVALID=[] live. Actual fresh669/670?existing assignment671/two originalST/wholeHU LOAD+DEPART/sourceP0?plan672?unload/whole mixed receive673. First SKU CRPT UNIT_OR direct3 + EGAIS BOX3; second SKU same CRPT profile PALLET-only3. Existing authoritative shared validator674 scopes direct-mode prohibition to actual physical UID; no parallel local rule remains.

Native673 intermediate rollback undoes both receipt lines/P/units/links; final receipt restores same original six units/nine codes and one TOP/two links, P3H0 each in blocked receiving cell. Exact native replay PASS; existing customer fulfillment not repeated. PALLET-only direct QR, foreign aggregation code, missing aggregate and wrong item quantity refused before stock writes. Original early667 textual guard removal missed an adjacent no-space token; corrected before positive receiving. Source670 equal-distance placement selected another valid cell; resumed already committed birth via existing replan after private-coordinate correction, no second birth/source factory.

HTTP675 current detail returns BOX/PALLET/UNIT_OR modes and exact original group-receive replay. Native direct UID/profile guard2.316ms/11.5buffers across14 executions; inventory retains current code hash/unit UID indices and bounded profile matrix/200legs/10000units. Before high-leaf industrial use, profile/archive batching and plan profiling remain inventory backlog; no broad index or timeout increase.

Raw UI668 accepts configured aggregation evidence and restores bounded scan arrays. JS/architecture PASS; browser/hardware/real ERP or government ACK/partial-group receiving remain open. Protected tmp/context671.json now contains successful group_receipt673; never rerun669/670 source factories,672 source discovery or673 initial receipt assertions. Read675/exact saved replay only. Qwen676 task prepared; no model run performed.
