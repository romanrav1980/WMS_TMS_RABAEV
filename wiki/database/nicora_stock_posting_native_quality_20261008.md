# Косвенные вызовы перемещения и контроля отгрузки

08.10.2026. Существующая RABAEV/orcl. [[nicora_stock_posting_case_20261008]] и [[nicora_stock_posting_article_20261008]] описывают физический CASE и упаковку.

## Установлено

180–191 установлены, Errors=0, ledger 076–083 APPLIED:

- REMAINS.move_pall_2_picking_cell / close_othod_pallet и INTERNAL_MOVE передают явную команду. ACTIVE использует фактический полный остаток и сохранённое назначение при повторе. WinForms сохраняет intent до вызова.
- OUTGOING_PALLET_CHECK объединяет прежние факты сканера/веса с настроенной отгрузкой в одной проводке. WEIGHT сохраняет прежнее поведение без автоматического списания; WEIGHT2 поддерживает настроенное списание.
- Четыре native функции контроля подключены через RRL_STOCK_QUALITY_ENTRY. RRL_UPDATE_PALLET_ROW2/3 в ACTIVE выполняют только существующий расчёт под CONFIG X, сбрасывают подтверждение контроля, не проводят автоматическую отгрузку после редактирования.
- Терминальный LOT_CHECK входит в ядро до DML. LOT_AUDIT, ошибки и факты контроля записываются в той же транзакции. Подлинный actor берётся из существующей HTTP Basic/RUSERS авторизации. Пароль терминала хранится только в памяти.
- Терминал сохраняет исходное тело и ID до HTTP. Неопределённый исход сохраняет intent для повтора. Если предшествовала неопределённость, последующий отказ не удаляет intent.
- Если параллельная операция уже завершилась и повторное планирование перестало видеть исходный запас, координатор повторно проверяет журнал и проводит проверку неизменного тела под существующим порядком блокировок.
- Возврат поставщику использует RETURNS, не ячейку отбора клиента. В текущем стенде RETURNS отсутствует: для этого процесса требуется зарегистрированное место возврата своего склада.

## Продолжение 192–196

192_source_fact_guards установлен Errors=0, ledger 084 APPLIED. При CREATED/PENDING_APPROVAL недостаче новый факт отбора этой строки отклоняется CASE_SHORT_DECISION_PENDING. После отклонения недостачи отбор может продолжиться; утверждение сохраняет согласованный физический факт. Report/reject используют CONFIG X, проводка — CONFIG S и task/line anchors. Документ с одновременно RETURN_SUPPLIER_ID и клиентской fulfillment-привязкой отклоняется SUPPLIER_RETURN_CUSTOMER_SOURCE_CONFLICT.

193_revision_cell_each_apply установлен Errors=0, ledger 085 APPLIED. Косвенная RRL_REVIZION_CELL теперь в ACTIVE вызывает измеренный INVENTORY_COUNT с EA, документом, причиной и сохранённым ID; несколько паллет требуют явный UID. Нет автоматического распределения недостачи между партиями. PREPARED сохраняет ограниченный private оригинал. Checkpoints: runtime/stock_posting_20261008/193_revision-cell-original-checkpoint и 194_revision_cell_each-checkpoint; полный rollback — 196_revision_cell_each_rollback.sql.

В API private receiving._event и picking._apply_case_pick_stock_fact отклоняют вызов вне PREPARED. WinForms оба ручных переноса принимают Decimal: ошибочный ввод больше не превращается в ноль, означающий всю паллету. Закрытие расходной накладной сохраняет intent до Oracle.

Подтверждение FULL_PALLET волны в ACTIVE перенаправлено на ровно одно существующее PICKING_MOVE/WAVE складское задание через complete_existing_task. Отдельная запись DONE/CONSUMED больше не предшествует физической проводке. Если задание не выпущено или неоднозначно, возвращается WAVE_STAGING_TASK_REQUIRED. CASE подтверждается через существующий CASE ТСД. fact_qty контракта переведён на Decimal; optional operation_id передаётся ядру.

Текущий bundle обновлён; installer source checkpoint дополнен REMAINS и native QC original/calculation функциями. Generator bundle больше не дублирует записи в сторонних Python scripts при каждом запуске.

## Подтверждение и границы

12 локальных проверок CASE/MES replay и FULL_PALLET bridge прошли (1.29 s). Проверки доказывают передачу точного количества/ID и отсутствие отдельного legacy DML в новых API ветвях, не промышленную физическую приёмку. AST изменённых Python прошёл; TypeScript терминала ранее прошёл tsc --noEmit. Полная сборка WinForms и браузерная приёмка ещё не проведены.

Свежий Oracle: перечисленные пакеты/тела и RRL_REVIZION_CELL VALID; release PREPARED, operations=0, stock_rows=0. B0 и cutover не выполнены. Исходный registry остаётся 21 ADAPTED / 6 RETIRED / 4 UNCONVERTED и не является полным каталогом новых косвенных callers.

Полный переход остаётся открытым: связь физического CASE carrier с существующими ST/отгрузкой и жизненный цикл отмены/возврата, закрытие whole-file registry после обзора всех ветвей, помарочный положительный пересчёт/MES выпуск, согласованная начальная проекция units/documents, краткие реальные quantity/replay/concurrency случаи и финальный ACTIVE/compatibility OFF.

Slow SQL новых физических случаев отсутствует, поскольку ни одной физической операции этого продолжения не проводилось. Решение: владелец следующего cutover case анализирует планы stock/reservation joins по UID/cell/task и RRL_SQL_SLOW_LOG; bounded windows 200/201 сохраняются. Массовое EXPLAIN/load сейчас не запускается. Encoding check обнаруживает только ранее известный raw TRANSPORT_TASK_PACKAGE_BODY.sql; raw evidence не переписан.

Дополнение: CASE pick/move и inventory-count UI записывают delivery marker до HTTP. Подтверждённый отказ текущей попытки удаляет intent только при отсутствии предшествующего неопределённого исхода. После потери ответа сохраняется исходная команда; положительный ACK очищает intent/marker. Три JS syntax checks прошли; browser interruption ещё не разыгран.
