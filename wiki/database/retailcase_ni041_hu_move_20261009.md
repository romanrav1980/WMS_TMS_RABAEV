# NI04.1: движение всего верхнего места

051 APPLIED в RABAEV/orcl, read/commands/transfer/root VALID. [[retailcase_ni041_hu_tree_20261009]].

HU_MOVE переносит полный bounded PALLET/container состав: каждый количественный лист P/H и его прежние владельцы/unit locations движутся существующим transfer core в одной root-транзакции; внутренние контейнеры меняют адрес/версии. Родитель не получает количественного stock. Snapshot/ancestor guards запрещают отдельный nested movement, устаревший состав, cycle и concurrent ownership drift.

На этом slice разрешён пустой ordinary storage target того же warehouse, без weight/height limits/physical STORAGE_SLOT и open arrivals. CELL target имеет exclusive admission fence; система не обходит ограничения неизвестной массой или фиктивным claim. Это явная временная граница, следующий ticket — actual measures/slot and warehouse-task adapter. Существующая общая TASK_COMPLETE пока не означает поддержку container UID без количественного листа.

Упаковка/движение отвергает дерево с открытым physical warehouse task; отдельный CASE lot нельзя упаковать вместо carrier. Существующая CASE membership остаётся полномочной; CASE attachment будет отдельным slice.

## API и рабочее место

/api/warehouse-hus composition/create/attach/detach/move, typed request/role server boundary, optional standard SSCC + internal identifiers. Экран warehouse-hus.html включён в existing nav. Скан identifier/child/from/to, просмотр версии, explicit unpack reason. Durable intent сохраняется user/API-scoped до запроса; unknown outcome повторяется тем же body/ID. Ошибка persistence не посылает операцию.

Quantity summary отдельно по SKU/BASE, верхнее место1, вложенный root0. Empty container API tare1.5/root create/replay подтверждены реальным HTTP с авторизацией; quantity rows0. Для неизвестной массы API возвращает null. Дополнительная проверка актуальности frozen leaf gross weight необходима до weight-capacity adapter; нельзя использовать copied historical gross при частичном остатке.

Common posting error теперь сохраняет bounded uppercase business rule reason без SQL/stack; новые HU/wave endpoints показывают конкретное препятствие.

## Адресный факт

TOP→BOX→leaf5/H2 целиком перемещены, source0/0, target5/2, тот же reservation owner. Nested BOX movement и blocked target denied unchanged, точный повтор не даёт второй journal effect. После явного unpack собственный P/H очищен root, история сохранена. Authenticated HTTP create/decimal tare/preview/replay прошёл; bind uid заменён на p_uid после ORA01745, исправление подтверждено HTTP.

SQL HU snapshot ~2.6ms/40 и API7.43ms, parent-link lookup ~0.08ms/209. Решение inventory — node200/depth16 и parent/active/UID indexes; no speculative tuning. Новые physical slots/CASE/marked multi-leaf/independent browser scope остаются открыты; полный NI04.1 не завершён.
