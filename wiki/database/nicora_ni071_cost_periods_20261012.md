# NI07.1: начисление по датам сборки внутри грузового места

Статус: применено в RABAEV/orcl; bounded author cases513/515/519/520 выполнены, полный спринт не закрыт.

512: finance владеет проведением суммы, inventory остаётся единственным владельцем количества. Источник — существующий архив погрузки, полные измерения BOX и неизменяемый STARTED_AT_INSTANT CASE. Количество коробок группируется по дате в явно выбранном часовом поясе; каждая дата использует свою действующую историческую ставку. Средняя ставка не вводится.

Один RRL_LOG_COST_SOURCE_CLAIM на LOAD/COST/CURRENCY принадлежит ровно одному расчёту. PERIOD_KEY разделяет строки по датам, не снимая защиту повторной оплаты всего источника. Исторические строки сохраняют ключ LEGACY, включая две строки с неизвестной датой: суммы/результаты не переписываются. Внешних FK на прежний ключ нет (live512). Коррекции и дополнительные расходы используют отдельные источники и не меняются.

Миграция: [SQL](../../db/migrations/2026-10-12_ni071_cost_periods/apply.sql), версия 2026-10-12-512-warehouse-cost-period-partition. Сохранён прежний native guard. Rollback допускается только без многопериодных строк, иначе требуется forward repair без удаления истории. Один короткий commit: result, source claims, dated lines, monetary outbox. Ставка блокируется на время расчёта; существующий порядок TT → period policy → rate head.

Граница: обычные BOX пока не имеют достоверного начала цикла сборки. LINKED_AT уже содержит часовой пояс, но дата первой сохранившейся связи не доказывает начало цикла после удаления раннего содержимого. Пустой HU не является началом сборки. Новую дату для исторических коробок не выдумываем.

515: fresh measured CASE7/14 original codes, one dated BOX cost2.75; two concurrent operations one winner/one COST_ALREADY_CHARGED, exact replay. Original5 lines/13.50 unchanged. 519: actual ordinary BOX3EA packing →LOAD/DEPART →native date source →cost2.25. Source519 old scenario stopped after LOAD because status now requires actor; exact retained load resumed, no source recreated. Both source P0, protected20/20 unchanged.
513 projection: one source across two dates ->1×2.50 +2×3.00 =8.50, historical versions separate. This is not a physical two-day warehouse rehearsal.
518: authoritative readonly RRL_BOX_ASSEMBLY_READ used by preview, Python date partition and native guard; rejects changed start operation/version/instant/warehouse and unknown old BOX clock (520). Original CASE proof stays READY.
SQL521: native clock read6.653ms/51 buffers, source claim insert19.009ms/237, cycle latest0.322ms/7.27, exact cycle join1.691ms/18.11. Decision finance/inventory: keep current prefix PKs, 200 nodes/source/200 loads/500 dated rows and 10000 preview boxes; reject overflow before writes. Owner finance: batch clock resolution/partition verification if multi-box warm latency exceeds50ms; no redundant index without plan evidence. No throughput claim from single BOX.
Next: physical multi-date case, larger bounded loads and remaining transport/point/unload norm sources, real finance SAP agreement and independent acceptance.
