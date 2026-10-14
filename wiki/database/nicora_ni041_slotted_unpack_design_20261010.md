# NI04.1 — вскрытие в слотовой ячейке, решение
10.10.2026. В разработке, не APPLIED. [[nicora_ni041_multi_hu_slots_20261010]].

Команда HU_UNPACK освобождает непосредственный вложенный CONTAINER верхнего CONTAINER в отдельный свободный STORAGE_SLOT той же ячейки. Родитель остаётся в своём прежнем слоте и содержит хотя бы один товарный лист. Прямой CASE/обычный stock leaf и nested-parent требуют отдельного расширения модели; explicit refusal.

Состав parent/child и две версии фиксируются заранее; fresh SI measurements после вскрытия нужны отдельно для оставшегося родителя и выделяемого контейнера. Старое измерение полного места не делится предположением. Общая масса/объём occupied+incoming ячейки пересчитываются с заменой старого parent на две новые части, каждая часть проверяется по своему слоту/температуре/габаритам.

Root объявляет полный logical closure, CELL_X, old/new SLOT, существующие CASE/ST/stock/unit/owners и две новые реальные warehouse task/claim IDs. Под блокировками повторно проверяет состав и физические сканы. Существующий HU_DETACH executor деактивирует связь и отзывает approval; actor/server warehouse_task_execute.

Факт сканируемого вскрытия оформляется двумя завершёнными существующими MANUAL/PUTAWAY задачами (HU, FACT_QTY1) и двумя fresh claims. Это выполненное действие оператора, а не новая очередь задач. Ранее завершённая задача/старый immutable operation сохраняются историей; новый operation содержит прежний и новый placement.

P/H и физические unit keys/ownership не меняются. Для HARD выделенного subtree используется существующий RESERVE_CORE.move_coverage всей записи в тот же UID/cell, только новый CELL_SLOT_ID; никаких release/reallocate или движения количества. Журнал товарного движения остаётся пустым, обязательный root outbox/результат фиксирует физическое действие.

Commit один у root caller; ошибка второго placement/task/claim откатывает связь, обе версии, control revocation, обе задачи/claims и reserve slot. Exact replay использует один сохранённый результат. При недостатке дополнительного слота требуется existing whole-HU move в рабочую ячейку; самовольное освобождение slot capacity запрещено.

Адресный будущий case: parent retains own5, childBOX contains5/H2; complete originalHUtask to slotA, split with fresh parent/child measurements to slotsA/B; P10/H2 unchanged, reserve slotB, two claims/versions, old approval revoked, replay; own root cleanup only. Independent concurrent/physical measurement/browser acceptance pending.
