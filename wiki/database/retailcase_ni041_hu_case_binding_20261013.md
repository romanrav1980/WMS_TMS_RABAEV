# NI04.1 — актуальная привязка CASE внутри HU

993 PREPARED before apply, migration2026-10-13-008-ni041-hu-case-binding. Actual CURRENT HU_CMD990 contains existing matryoshka. HU_ATTACH/DETACH directCASE and HU_MOVE tree increment CASEcontentversion but did not update activePICKED fulfillment; reuse binding core974.

Root declares ST/FF keys per CASE in parent/child snapshots, stores frozen material bindings map and validates it after existing ST/CASE row locks before tree changes. Touched CASE increments and matching FFversion occur inside the existing HU stock transaction. Unbound CASE unchanged. Closed SHIPPED/CANCELLED fulfillment is immutable historical history and is not advanced; activePICKED binding has strict original relation/warehouse/version/load proof. Existing transfercore still moves quantities/reserves/units only on leaf lots.

Packing/detaching existing policy deliberately revokes ordinary CASE controls, measured small-box exception preserved. Moving intacttree preserves current admission by old policy; no blanket recontrol is invented. Current HU slot/target/scan/warehouse constraints retained. Captures990/992/SHA/pairedrollback/no DBcopy. Livecompile and ownretained987 twoCASE HU attach/move/detach scenario still pending; not fullNI04.1 closure.

## Checkpoint999 — применено

# NI04.1 — согласованное исполнение CASE внутри HU

В существующую матрёшку подключена привязка CASE к исполнению заказа. Упаковка, распаковка и перемещение целого HU теперь согласованно обновляют версии CASE и активного исполнения заказа внутри одной транзакции существующего ядра. Новый механизм изменения остатка не создавался.

Миграция 2026-10-13-008-ni041-hu-case-binding (993) применена в RABAEV/orcl. USER_ERRORS пуст, изменённые пакеты VALID. Перед изменением сохранены текущие определения 990/992, SHA и парный rollback. Rollback не запускался. Исторические SHIPPED/CANCELLED исполнения не повышаются; положительный сценарий исторического CASE отдельно не выполнен.

## Фактически выполнено

Источник987 с двумя CASE: 1131 — 12 EA, 1132 — 8 EA, одна СТ/склад, действующие собственные резервы. Исходник не пересоздавался. После штатной упаковки в HU994:4bb85f1f15 CASE/исполнение имеют версии4/4. Первый запрос без подтверждения сохранённого бронирования тары корректно отклонён; новый исправленный запрос содержит исходные идентификаторы бронирования.

Существующее задание1138 переместило целый HU из QW4bb85f1f15 в QH4bb85f1f15: DONE, факт1HU, журнал партий12+8EA, CASE/исполнение5/5 обоих. Положительная проводка с rollback восстановила исходное состояние; штатная команда и её точный повтор сохранили один результат.

Распаковка996 выделила CASE1131: версия CASE6 и исполнения6, связь удалена, исходное бронирование тары осталось HELD. Текущий HU версии4 содержит CASE1132 с8EA/HARD8; отдельный CASE1131 содержит12EA/HARD12. Суммарно остаток20 и резерв20. Историческое задание1138 перемещало20EA; текущий состав после распаковки отличается.

## Интерфейс

997–998: режим HU · одно место, ссылка «Текущий состав HU» из задания, автоматическая загрузка выбранного места по URL после входа. Планирование HU открывает конкретное созданное задание. Обновлена адаптивная форма состава/упаковки/перемещения; создание пустого места и операции со слотами свёрнуты, существующие поля/команды/права сохранены.

Скриншоты19: DONE1138;20: текущий состав;21: обновлённый рабочий экран. Адресная навигация и автоматическая загрузка реально показаны. Автоматизированное нажатие ссылки19 не вызвало наблюдаемой навигации; затем открыт точный URL ссылки, поэтому ручное нажатие не объявляется подтверждённым.

## Ограничения и SQL

Полный NI04.1 остаётся открыт: смешанные/маркированные составы, ресурсные и физические ограничения, оборудование и независимая приёмка требуют оставшихся работ. Подтверждённая масса этих двух CASE отсутствует, пригодность ограниченного слота не заявлена. Широкие прогоны и копия БД не выполнялись.

CASE996 сохранил результаты V$SQL, совпадающего запроса не получено. Решение владельца inventory: сохранить существующие ключи CASE/FF/ST и ограниченное дерево; измерить конкретный HU binding source_snapshot при следующем значимом HU-сценарии, индекс без плана и измерения не добавлять. Это не нагрузочная приёмка.

Источники: tmp/context994.json, tmp/context996.json и SQL миграции; копии результатов в19-hu-binding-evidence.json.
