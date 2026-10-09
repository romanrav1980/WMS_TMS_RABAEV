# NICORA: целевой контракт остатка и координации

Current status 08.10.2026 supersedes the historical checkpoints below: [[nicora_stock_posting_handlers]]. Components through 099 installed; bridge/MES adapters prepared, 6 ADAPTED / 25 UNCONVERTED. PREPARED, no B0 or full cutover.

7 октября 2026 года. **Проектируемая модель, не применённая миграция.** Авторитетная спецификация — [ТЗ редакции 2.0](../requirements/stock_posting_core_tz.md). Эта страница — краткое зеркало направления изменения существующей RABAEV.

**Последующий checkpoint 08.10.2026:** [реализация начата](nicora_stock_posting_implementation.md), 013–015 установили очистку dev/часть структуры/математику. Полная целевая модель ниже ещё не реализована; новая проводка не активирована. Указанное далее отсутствие unique/NOT NULL — исходный факт 07.10, устранённый 013.

## Действующий механизм и найденные ограничения

Срез NI03/010 использует существующий `RRL_EVENTS` и действующий legacy trigger для `RRL_REMAINS`: [[nicora_ni03_task_effect]]. Он ещё не переключён на новое ядро. Подготовка ТЗ не отключила триггер, не установила флаг и не применила DDL.

Read-only live metadata 07.10.2026 подтверждает: stock key `RRL_REMAINS(CELL,UID_POLETA)` покрыт неуникальным индексом; столбцы ключа/REMAIN nullable, P/U-ограничение в проверенном наборе отсутствует. Для `RRL_EVENTS.ID_EVENT` и `RRL_PALLETS.UID_PALLET` существуют уникальные индексы; `RRL_PALLETS.SSCC` имеет неуникальный индекс. У `RRL_STOCK_RESERVATION`/`RRL_WAREHOUSE_TASK` есть PK и ссылки на слоты; receipt units имеют PK UID/UNIT и ссылку на паллету. Наличие этих ограничений не подтверждает весь бизнес-протокол.

Локальные свидетельства: [metadata](../../runtime/stock_spec_review_v2/oracle-metadata.json), [предыдущая спецификация 1.1](../../runtime/stock_spec_review_v2/spec-v1.1.md). Raw source exports не переписывались. Полная перепись writer SQL и dependency map остаются частью реализации.

## Количественный контракт

- Единственный текущий количественный остаток: `RRL_REMAINS`, однозначный NOT NULL ключ `(UID_POLETA,CELL)`.
- P — REMAIN в базовой единице однородной физической доли SKU/партии/владельца. H — неисполненный канонический HARD; `0<=H<=P`.
- Canonical HARD — существующий `RRL_STOCK_RESERVATION`; pick/wave registries сохраняются как связанные проекции, их количество не вычитается второй раз.
- Синхронный `HARD_RESERVED_BASE` в строке остатка — агрегат канонического резерва, не третий регистр. P/H обновляются одним UPDATE под общим STOCK anchor.
- Собственный резерв исполняется с уменьшением P/H одновременно; при пополнении/перемещении продолжающееся покрытие переносится вместе с физической долей. Чужой HARD сохраняется.
- Карантин определяется недоступными ячейками хранения/отбора, по уточнению владельца. Физический P в них сохраняется; обычный подбор/новый HARD/отбор их исключают. Разрешённые карантинные перемещения идут специальной командой, без дублирующего SKU-флага карантина.
- Exact NUMBER/Decimal, версионированные рациональные коэффициенты; clamp в ноль и скрытое округление запрещены.

## Ядро, ресурсы и атомарность

Один public posting contract, один закрытый stock algorithm, один UoW. Journal, P/H, reserve, current unit/HU binding, task/residual/fulfillment и обязательный existing outbox фиксируются вместе. CORE/trigger/domain handlers не управляют транзакцией самостоятельно.

Порядок задан в ТЗ, а не выбирается каждым writer: shared/exclusive admission/policy/domain fences, затем полный отсортированный набор OP → ROW → HU → SLOT → STOCK → UNIT → ALIAS/UNIQUE anchors. `RRL_STOCK_GUARD` содержит только metadata координации, без количественного остатка. S policy fences позволяют независимым паллетам одной ячейки работать параллельно; X защищает изменение правил. Все изменения P и любые HARD используют один UID anchor, включая создание новой reservation/destination.

Полный plan до предметного DML включает side effects, изменяемые parents, UNIQUE/FK dependencies и точные keys существующих task/pick/case/SAP/MES/fulfillment/outbox семейств. Новые ресурсы после revalidation — rollback/replan; дозахват после применения запрещён. Все writers состояния допуска, включая cancel/quality/regulatory callback, соблюдают общий protocol.

ORA-00060/timeout откатывает **всю попытку** владельцем UoW. Успех фиксируется одним commit; неизвестный исход commit устанавливается по прежнему operation_id. Idempotency identity сохраняется при архивировании. Реальная независимость/нагрузка ещё не измерены; документ не утверждает невозможность любых внутренних Oracle deadlocks.

## Журнал, состав и выпуск

Сохраняются `RRL_EVENTS` и старые ID/COUNT_EVENT; новые факты получают operation/line/leg, BASE_QTY/UOM и immutable result. Старую историю не пересчитывать по новым коэффициентам. Исходное B0 на согласованном SCN + новые физические legs = текущий P. Сверки используют единый snapshot, не разные committed версии.

Помарочная физическая единица имеет один текущий binding; mixed HU содержит отдельные количественные листья. Имеющаяся CRPT агрегация переиспользуется. Если её/складских связей недостаточно, минимальные metadata unit binding/current HU parent связывают существующие identities; второй каталог паллет/SSCC и второй запас не создаются.

Выпуск всей системы одним cutover. Общая `RRL_SYSTEM_SETTINGS.STOCK_LEGACY_TRIGGER_ENABLED='0'` по умолчанию. OFF отклоняет внешний legacy stock INSERT; ON допускает только prepared wrapper с тем же полным планом/ядром. Guards всегда enabled. Двойной stock effect и тихая запись события без остатка запрещены.

Порядок apply/rollback/verify, B0/open tasks/anomalies и 42 сценария будущей приёмки определены в ТЗ. Никакие бизнес/нагрузочные прогоны не запускались в рамках этой редакции. SQL/мощность/перевод всех callers не объявляются подтверждёнными до реализации.
