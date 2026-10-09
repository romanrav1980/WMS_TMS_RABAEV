# Физическая CASE-паллета и существующая отгрузка СТ

09.10.2026. Продолжение [[nicora_stock_posting_native_quality_20261008]] и [[nicora_stock_posting_case_20261008]]. Миграция 2026-10-09-001-case-existing-st-shipment, компоненты 197–203, установлена в RABAEV/orcl. Полного cutover пока нет.

## Поведение

Оператор закрывает паллету отбора, сканирует её фактический идентификатор и идентификатор уже подготовленной паллеты СТ. Существующий CASE ТСД получил действие «Связать с отгрузкой СТ». API POST /api/case-pick/tasks/{id}/bind-shipment использует авторизованного RUSERS actor и прежнее право case_pick_execute.

Связь хранится в RRL_CASE_PICK_TASK.LEGACY_SBORKA_PALLET_ID. Ограничение RRL_CASE_SHIPMENT_UK допускает одну физическую CASE-паллету на паллету СТ. Повтор той же привязки возвращает существующий результат. Привязка к другому СТ отклоняется. Новая СТ, заказ или рейс не создаются.

До привязки проверяются фактический скан, закрытое состояние carrier, CONTENT_VERSION, warehouse, тип/состояние СТ, единственная fulfillment-связь с этим заказом и полный состав. Количества СТ точно преобразуются по последней явной политике UOM; сравнение выполняется по SKU/base unit с Fraction, без float и округления. Партии суммируются только для сопоставления плана, сами партии в stock остаются отдельными. Пустой состав, лишний/отсутствующий SKU, другая базовая единица, непредставимое количество и более 200 строк отклоняются.

Существующий SHIP_PALLET в новом ядре выбирает собственный PICKING HARD только из положительных physical lots привязанного carrier. Полный физический состав обязан совпасть с проведёнными allocations. Чужие carrier lots и свободный CASE-товар исключены из общего распределения отгрузки. Пересчёт плана не может заменить реально собранную партию другой партией того же клиента.

План заранее захватывает CT row/HU и stock closure всех положительных партий. Исполнение проверяет связь, customer/warehouse, CONTENT_VERSION и снимок состава под существующим порядком блокировок. Списание P/H и марок, старый документ, fulfillment, CASE SHIPPED/SHIPPED_OPERATION и обязательный outbox выполняются одной root-транзакцией. Повтор остаётся по исходному operation_id через неизменный журнал. Отменённый заказ или закрытый fulfillment блокируют проводку.

Для CT добавлены SHIPPED_OPERATION (FK на журнал) и статус SHIPPED. Его физический состав сохраняется как история membership; положительные остатки после полного списания отсутствуют. Состояние READY_TO_SHIP теперь поддерживается существующим whole-carrier move вместо отсутствовавшего в CHECK значения READY.

## Legacy drift и восстановление

В RRL_SBORKA_PALLETS нет PRIMARY/UNIQUE constraint для ID. Первая попытка добавить FK была отклонена Oracle ORA-02270; столбцы не были добавлены этой неуспешной командой. Нельзя объявлять такой FK установленным. LEGACY_SBORKA_PALLET_ID остаётся проверяемой логической ссылкой на существующий СТ; target lookup отклоняет неоднозначный PALLET_UID, ядро повторно проверяет документ/fulfillment. Legacy документы не очищались и уникальность ID принудительно не менялась. Физическое удаление legacy документа может оставить ссылку без цели; отгрузка тогда отклоняется, автоматического подбора замены нет.

Source checkpoints: runtime/stock_posting_20261008/198_case_shipment-checkpoint и 199_case_shipment_finish-checkpoint. CP198 manifest предшествует локальной замене строкового CLOB-снимка на JSON array и последующей warehouse-проверке; исходный checkpoint не переписан. Последний canonical 068 содержит итоговое исполнение. Additive schema 197 имеет paired rollback; полный rollback 201 сперва возвращает пакеты, затем схему. После физических операций или сохранённых binding schema rollback отклоняется. Восстановление после реальных проводок не проверялось.

Общий apply — 202_case_shipment_apply.sql; ledger 200 APPLIED; verify — 203. Current runtime manifest требует оба новых CT столбца, bundle обновлён. API/UI исходники сохранены локально; GitHub не обновлялся.

## Проверка и оставшиеся границы

197/198/199/200 установлены Errors=0. Три пакета/тела VALID, RRL_CASE_SHIPMENT_UK ENABLED/VALIDATED. 21 локальная проверка composition/replay/warehouse bridge прошла; точное сопоставление разных партий/упаковок, большая десятичная величина, расхождения SKU/количества/единиц и запрещённое округление проверены. AST пяти Python файлов и node --check нового UI прошли.

Физического Oracle shipping case и браузерной приёмки ещё не было. PREPARED остаётся активным статусом release; B0 и ACTIVE не выполнялись. Для стыка используется равенство полного carrier и одной существующей паллеты СТ: несколько подготовленных паллет требуют соответствующей фактической раскладки. Автоматическое изменение плановых количеств/рейсов и перепривязка уже закреплённого carrier не добавлены.

Возврат/отмена физического состава, составное warehouse-task completion, произвольная вложенность HU и помарочный birth MES/inventory по-прежнему открыты. Исходный writer registry остаётся отдельным незавершённым gate, не доказательством готовности всей системы.

Slow SQL shipping ещё не доступен: проводок не было. Решение владельца следующего физического случая (разработчик ядра): проверить планы join по CASE task/LOT_UID, UID/cell и own reservation, а также RRL_SQL_SLOW_LOG. Чтение composition ограничено 201 строкой для обнаружения превышения. Массовый load не запускался.

## Закрытие receipt writer gate
204_receiving_writer_registry.sql установлен Errors=0 после обзора receiving.receive/complete/replan/cancel/private event и root receipt stages. Активные qty пути идут через SAP_RECEIPT/TASK_COMPLETE, metadata защищены CONFIG X; private event запрещён после cutover. Записан digest текущего source, paired rollback возвращает исходный UNCONVERTED hash из writer checkpoint. Registry: 22 ADAPTED / 6 RETIRED / 3 UNCONVERTED; Form1, mes_service.py и picking_service.py остаются на финальном обзоре. Это не объявляет полный транзитивный каталог закрытым.

## Продолжение MES и eligibility
205: mes_service.py reviewed/ADAPTED. Физические эффекты проходят через mes_commands/mes_task_commands, release/supply команды и native Oracle adapter; issue/complete metadata создают факты до их физического применения. Private legacy SOFT/HARD builders запрещены вне PREPARED. MES quantity/fact_qty/pallet quantity/pack count контракты теперь Decimal с bounds/scale; pallet JSON сохраняет строки. PREPARED confirm также больше не преобразует факт в float. Marked FG/inventory birth по-прежнему требует отдельного capture, ADAPTED writer не означает реализации этого процесса.

206/207: create_hard отклоняет CASE membership после уже запланированного HU lock; новый резерв на упакованный товар не создаётся даже после снятия старого H. TRANSFER проверяет membership и источника, и назначения: обычное перемещение не может вмешать товар в carrier. Используются прежние locks, новый порядок не вводится. Первый apply имел ошибку разделителя объявления переменной, исправлен повторным apply Errors=0; исходный source checkpoint не переписан. Ledger 2026-10-09-002-case-allocation-eligibility APPLIED. Это защита до реализации физического unpack/return, не утверждение, что return уже готов.

Итог локальных проверок: 28 passed (1.38 s). Registry 23 ADAPTED / 6 RETIRED / 2 UNCONVERTED: Form1.cs и picking_service.py остаются на финальном whole-file обзоре. Непроведённые физические случаи, маркированный birth и B0/cutover остаются открытыми. Current runtime bundle обновлён после 206.
