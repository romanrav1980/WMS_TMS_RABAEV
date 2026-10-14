# NI06.3 — передача закреплённой тары погруженного места,102

2026-10-10-102-booked-tare-driver-handover APPLIED в RABAEV/orcl:18 statements/0 errors; helper/CMD/guards VALID. Существующие RRL_TARE_BOOK и RRL_TT_HU_LOAD_FACT связаны immutable RRL_TARE_OFFER_BOOK. Нового назначения СТ рейсу нет.

Склад выбирает HELD записи только собственного склада/типа, подтверждённые фактическим LOADED/DEPARTED верхним местом этого рейса и автомобиля. CASE — exact ROOT_CASE_TASK_ID, HU — exact ROOT_UID. Один верхний PALLET/ROLL_CAGE соответствует одной таре; вложенные BOX/STOCK не умножают её количество.

OFFER сохраняет выбранные claims и original load, не меняет физический баланс. ACCEPT другого текущего участника повторно проверяет принадлежность/факт погрузки, закрывает выбранные claims TRANSFERRED и проводит warehouse→vehicle в той же короткой Root транзакции. Остальные HELD сохраняются. Конкурентное повторное использование claim отказано; исходный operation_id возвращает сохранённый результат. Товарный журнал/P/H второй раз не меняется.

API /warehouses/{ware}/trips/{trip}/loaded-bookings возвращает bounded100. [Складской АРМ](../../wiki-raw/wms_admin_ui_reference/tare-ledger.html) позволяет выбрать фактически погруженные места. Пустой список не включается в canonical metadata, сохраняя прежние OFFER replay.

## Доказанный случай

[Одноразовый сценарий](../../scripts/ni063_booked_cargo_case.py): собственный верхний PALLET с существующим nested BOX+STOCK; COUNT1/BOOK1/free0 до отправки, фактическая штатная Root погрузка, OFFER/replay, dedicated current-bound driver ACCEPT/replay. Claim TRANSFERRED, warehouse0/vehicle1, exact load association1, RRL_EVENTS для tare accept0. Собственный товарный fixture очищен через прежнее Root ядро, immutable история сохранена.

После PASS102 старый несвязанный тест пытался напрямую переназначить ST и получил актуальный отказ EXPLICIT_TRIP_MEMBERSHIP_WRITER_REQUIRED вместо прежнего UNLOADING_REQUIRED. Этот obsolete хвост удалён из нового сценария/генератора; успешный бизнес-факт не повторялся.

Открыто: standalone STOCK/FULLPAL tare booking, repack/cancellation физически использованной тары, moving damaged lineage, независимый UI/START, недостача/прогноз. Полный NI06.3 не объявлен закрытым.
