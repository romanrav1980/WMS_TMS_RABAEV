# NI06.3 — пригодная тара в существующей сборке,101
2026-10-10-101-tare-existing-assembly APPLIED в RABAEV; новые/изменённые пакеты, guards/view VALID. RRL_TARE_BOOK/AVAILABILITY закрепляют фактически имеющуюся GOOD warehouse тару за существующим CASE или верхним PALLET/ROLL_CAGE HU. По одной физической таре на место, активная уникальность; дочерний код не создаёт второй hold. Нет нового планировщика CASE или второго товарного журнала.

BOOK — tare_plan + актуальная привязка к складу, актуальная свободная тара. CASE берёт собственный PALLET_TYPE_ID; HU — явный matching physical type. expected_warehouse_id из экрана проверяется, не позволяет выбранному месту незаметно взять тару другого склада.
BOOK_CANCEL — только пустое неотправленное место; история сохраняется. Held qty уменьшает доступность; общий физqty/P/H не меняются. Balance version меняется вместе с claim, qty сохраняется.
Начало нового CASE требует собственного или допустимого верхнего HU hold через общий RRL_TARE_PLANNING.case_booking/require_case. Переиспользованы CASE resource actions; Snapshot в существующем get_task, indicator/link на прежнем ТСД. Already-started history не объявляется новым стартом.
COUNT не опускаетqty нижеHELD; DAMAGE и warehouse→vehicle OFFER/ACCEPT не расходуют занятую assembly тару. Для передачи cargo-связанного hold водителю нужен следующий manifest handover102. Другой склад/зависимый ребёнок/двойное закрепление требуют отдельного процесса, не молчаливого снятия hold.

## Доказанный dev-случай
Warehouse9104/type3/physical4: четыре собственных EMPTY ROLL_CAGE HU закреплены; fifth отказ. Доступность4→0, physicalqty4, qtygoodsRemain на этих HU0. COUNT0/DAMAGE1 отказывают приheld4. CANCEL/replay пустых мест возвращаетfree4 безqtybirth.
Прежний unused CASE1020/warehouse6667491/type1 получил собственный программный fixture COUNT1, BOOK1/free0; существующий get_task показываетbooking; общий require_case допускает закреплённое и отказывает послеcancel. Сам фактический resource/session START API в этом author-case не исполнялся и независимо не принят.
[Одноразовый сценарий](../../scripts/ni063_tare_assembly_case.py) PASS. Созданные HU/отменённые claims/CASE opening count остаются как история dev; повторный запуск не назначается.

## Интерфейс и структура
/api/inventory/tare/book|book-cancel, warehouses/{id}/availability|bookings, assembly/catalog. [АРМ](../../wiki-raw/wms_admin_ui_reference/tare-assembly.html), старый [CASE ТСД](../../wiki-raw/wms_admin_ui_reference/case-pick-tsd.html) показывает доступность/закрепление. Public inventory facade вместо SQL в legacy get_task.
Запрос availability поbalancePK6s1x9m7naxc33:1.840мс/19 вызовов. Решение retainPK/book(BALANCE_KEY,STATUS), bound types100/history200. Debt view после100:85.722мс, originalstoreclaim22.477, resolutioninsert9.619; retain filtered owner/type/store/indexes, на реальном росте owner NI06.3 оценивает plan/pushdown/incremental read projection. Не увеличение тайм-аута вместо причин.

Открыто:102 физическая передача booked cargo тары по существующей погрузке, shortage/packing/repack и lineage damaged moving, independent START/browser. Полный NI06.3 не закрыт.
