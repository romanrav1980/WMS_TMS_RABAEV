# NI04.1 — FULLPAL внутри верхнего грузового места
10.10.2026.075 APPLIED RABAEV/orcl. Inventory/root transaction RRL_STOCK_POSTING_API; existing ST/FULLPAL fact/shipping engine retained.

HU_SHIP теперь объединяет существующие ST от CASE и реально PICKED FULLPAL листьев. Каждый frozen allocation обязан относиться к UID/ячейке дерева. Сумма всех legs каждого физического листа должна точно совпасть с его P: посторонний или непривязанный остаток, частичный лист, двойное назначение отклоняются до движения. Закрытые actual ST sorted перед CASE; все QC rechecked перед любой leg. Один journal/outbox/commit, distinct line offsets.

FULLPAL retains original PICKED_STOCK_VERSION as task-binding history; current positive row version independently frozen and checked under root closure. Technical per-cell STOCK_VERSION is not a global identity epoch: a newly created target-cell row can have the same number as the old source. Therefore whole movement/H-only does not invalidate physical identity; actual UID, owner/pick task, whole quantity/current single location and frozen current version still required. QC v2 protects changed/restored physical composition.

Авторский scripts/ni041_fullpal_hu_shipping_case.py passed: фактический FULLPAL3→ST0.125BOX→BOX/TOP→перенос целого HU→верхняя отгрузка P/H0/replay. Другая паллета того же заказа3/H3 не затронута. Отдельная SHIP_PALLET вложенного FULLPAL и неверный scan ячейки отклонены. История BOX после отгрузки содержит только BOX+его лист, без лишнего TOP. Own cleanup P/H0.

Непривязанный legacy ordinary stock не разрешён к выбору по одному артикулу; необходим существующий physical ST fulfillment. Реальная погрузка/ворота/рейс и нормативный ACK ещё NI05.2/NI04.3, этот slice не означает физический выезд машины. Независимая приёмка/concurrency/marked/mixed CASE+FULLPAL остаются открытыми.

Rollback restores checkpoints366/367 without deleting departure history. [075](../../db/migrations/2026-10-10_ni041_fullpal_shipping/apply.sql), [[nicora_ni041_hu_shipping_20261010]], [[nicora_ni042_composition_epoch_20261010]].

Slow SQL: g0xwzbtxgsfv1 owner reservation allocation23.21ms/6; cdm2zkbyrutwh actual fullpal preview14.07ms/2;6uswhu7qcch23 bound ST/tree query5.321ms/2. V$SQL_PLAN unavailable ORA00942. Decision: current owner/UID/bounds retained; NI08 owner reviews actual plan at volume with read access, no guessed index.
