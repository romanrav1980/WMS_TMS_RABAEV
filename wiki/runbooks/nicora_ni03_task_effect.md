# NI03 — согласованное выполнение складских заданий

7 октября 2026 года. Первый функциональный срез реализован: прежний POST /api/warehouse-tasks/{id}/complete выполняет подтверждение существующего задания, остаточное задание, resource event, domain effect, stock move и резерв в одной транзакции. Другой warehouse task engine не создаётся.

## Поведение

- Пополнение WAVE: движение через RRL_EVENTS и существующий stock-move ledger. Частичный факт уменьшает свой source HARD reserve; неперемещённая часть остаётся в residual task и резерве.
- FULL_PALLET PICKING_MOVE: раньше обработчик обновлял только wave/pick статусы; теперь добавлен физический перенос всего stock pallet и прежнее потребление резервов.
- Повтор того же подтверждения/actor возвращает успех без повторного движения. Отличающееся подтверждение — 409. Старые DONE без сохранённой identity требуют отдельной сверки.
- Ошибка физического эффекта откатывает новое DONE, residual, reserve и movement. Отдельный retry существующего sync также использует общую транзакцию и блокировки; SYNCED не запускается повторно.
- Партия/срок/марки сохраняют pallet identity при целом перемещении. Частичный marked move и движение вложенного SSCC отвергаются до точной NI04 команды состава: нельзя переносить условное количество вместо физических кодов.
- Незавершённое размещение SAP, чужой склад, заблокированное назначение, дубли остатков, нехватка товара/резерва и отменённый source document препятствуют выполнению.

SAP PUTAWAY переиспользует свой готовый атомарный handler. MES handlers объединены одним cursor с сохранением существующей семантики production lifecycle; это не заявление о переработке MES. Сканирование/права текущего endpoint сохранены, actor берётся из authenticated user.

## Источники и запуск

[warehouse_task_service.py](../../api/wms_api_server/app/services/warehouse_task_service.py) → inventory public → task_completion.py/TransactionGateway → существующие domain handlers → task_stock_move.py/task_reservation.py. [Database mirror и 010](../database/nicora_ni03_task_effect.md). Runtime hashes/logs — runtime/ni03.

Использовать существующий serv.bat. Новая схема/инстанс/MCP не нужны. Установка 010 выполнена: 3 statements, 0 errors; поля/constraint/ledger прочитаны live. API import 374 routes, это проверка загрузки кода, не бизнес-приёмка. Новые бизнес/tests/load не запускались по поручению владельца; meaningful case и slow SQL измерения отсутствуют.

## Оставшийся объём NI03

Общая eligibility во всех планировщиках, единое владение двумя существующими резервными регистрами, отдельный case-pick/short API с точным составом, PLANNED → PICKED fulfillment и единая команда запуска волны остаются. NI03 целиком не закрыт. Source analysis сохранён, испытательные поручения Qwen NI01 не исполнялись.
