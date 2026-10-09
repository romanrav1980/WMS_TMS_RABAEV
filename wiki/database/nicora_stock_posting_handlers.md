> Актуальное продолжение 121–130: [[nicora_stock_posting_continuation_20261008]]. 47 package pairs; 10 ADAPTED / 21 UNCONVERTED; PREPARED, полного cutover нет.

# Единая проводка: установленный код и незакрытый переход

08.10.2026, существующая RABAEV/orcl. Эта страница заменяет прежний статус компонентов 030–063. См. [[nicora_stock_posting_implementation]], [[nicora_dev_stock_reset_20261008]], [[nicora_stock_posting_target]].

## Фактическое состояние

PREPARED, BASELINE_ID NULL, operations 0, RRL_REMAINS 0, RRL_EVENTS 0. STOCK_LEGACY_TRIGGER_ENABLED=0. INVALID объектов RRL_STOCK_* нет. Реестр исходных 31 writer: 9 ADAPTED, 22 UNCONVERTED. Это установленный код до единого переключения; полный переход не завершён. Компиляция не подтверждает физическую корректность, конкурентность или мощность.

Продолжение 100–119: [[nicora_stock_posting_extension_20261008]]. Native MES/picking/wave, inventory count, own-reserve shipment и Oracle JSON binds установлены. PREPARED сохраняется; physical posting/replay не подтверждены.

## Установленные обработчики

| Команда/механизм | Существующие объекты и эффект |
|---|---|
| TASK_COMPLETE | RRL_WAREHOUSE_TASK, stock fact, residual, domain sync; P/H, HARD и текущие единицы одной транзакцией |
| RESERVATION_* / DOCUMENT_RELEASE_RESERVATIONS | RRL_STOCK_RESERVATION; SOFT без P/H, HARD меняет H; document-before-reservation, снятие unit bindings и H вместе |
| SAP_RECEIPT / PUTAWAY | SAP-заказ и существующий приход; POSTED_BASE_QTY, слот, закрытие приёмки/размещения, RRL_SAP_RECEIPT_OUTBOX в той же транзакции |
| INTERNAL_MOVE / MOVE_QUARANTINE | Native RRL_INTERNAL_MOVE2/3; точная MOD_ID/норма коробки, split с происхождением; карантин через недоступные ячейки, специальное право |
| SHIP_DOCUMENT / SHIP_PALLET | Native RRL_CLOSE_OTHOD_NAKLAD и RRL_CLOSE_OTHOD_PALLET; legacy unreserved FEFO, append-only расход со ссылкой на документ/строку, без фиктивных MINUS/EXCESS |
| WAVE_RESERVE_SOURCES | Источники существующих пополнений; F=P-H, HARD и unit binding вместо LOCK TABLE |
| MES_RELEASE_TO_PRODUCTION / MES_CALCULATE_SUPPLY | Существующие BOM/demand/candidate/shortage/raw task/warehouse task; точные UOM, один расчёт доступности по нескольким строкам BOM, HARD и оба задания в одной транзакции |
| MES_RAW_TASK_CANCEL | Снятие HARD и отмена незавершённых raw/warehouse tasks одной транзакцией; выполненный факт не удаляется |
| MES_MOVEMENTS | Пакетное применение существующих RAW/FG movements; полный перевод native production API ещё не завершён |
| CONFIG_API / UOM_CONFIG | Fences публикации ARTMAS и настроек; 50 758 коэффициентов для 6 086 однозначно определённых EA/KG артикулов |
| COMPAT_MANUAL_MOVE | Подготовленный manifest целого немаркированного, незарезервированного перемещения; trigger вызывает тот же balance core, только при глобальном ON |
| SETTING_API | RELEASE X + CONFIG X, отдельное право, причина и immutable old/new/version audit; OFF по умолчанию |

CAPTURED -> AVAILABLE подтверждает физическую складскую приёмку, не положительный ответ государственного сервиса.

## Мост и клиенты

AFTER INSERT RRL_EVENTS заменён мостом. EXPLICIT journal не проводит запас повторно. COMPAT принимает только совпадающие с prepared manifest события той же транзакции; не читает mutating RRL_EVENTS и не делает commit/rollback. В PREPARED сохранена прежняя ветка для непреобразованных клиентов. Прямые stock/history/reservation/unit writes после ACTIVE запрещают guards.

Четыре _SP_OLD функции ограничены ACCESSIBLE BY соответствующей public function; RRL_MES_RAW_SUPPLY_OLD ограничен package caller и PREPARED. Установленные native adapters: INTERNAL_MOVE2/3, CLOSE_OTHOD_NAKLAD/PALLET, MES_RAW_SUPPLY_API и event trigger. Точное публичное имя паллетной отгрузки — RRL_CLOSE_OTHOD_PALLET, не RRL_CLOSE_OTHOD_NAKLAD_PALLET.

MES confirm использует TASK_COMPLETE; документальное подтверждение с отдельным правом хранится в payload и не выдаётся за сканирование. Межскладской MES маршрут передаёт source warehouse. Админка сохраняет ID и тело команды в localStorage до подтверждённого исхода; повтор подтверждения после DONE восстанавливает прежнюю warehouse-task identity и проходит проверку canonical request ядром.

Native runner различает неизвестный commit и известный commit с ошибкой очистки; такие соединения не повторяют операцию автоматически. C# internal callers передают operation ID, но полноценное долговременное сохранение desktop intents ещё относится к незакрытому переходу.

## Что ещё требуется до ACTIVE

- Остальные native writers: legacy receipt/отмена/сторно, инвентаризация/корректировки, ARTICULS, MES_PRODUCTION_API, picking/wave projections и их реальные callers.
- CASE picking: заменить прямое REMAIN=greatest(REMAIN-q,0), сохранить наличие до подтверждённой отгрузки; связать существующие carrier/партии и канонический HARD.
- Современная отгрузка собственных HARD из staging вместо одного legacy unreserved pick-face маршрута; действующие regulatory gates.
- Partial marked split и closure вложенных HU/агрегаций; физический и регуляторный состав должны меняться согласованно.
- Полный охват config/birth/pallet metadata writers, действия отмены документов и их проекции в общей транзакции.
- Сверить все 25 оставшихся кандидатов и косвенные callers, зафиксировать hash/ADAPTED либо обоснованный RETIRED; guards сами по себе не заменяют функциональность.
- B0 под закрытым admission, единая активация, короткие реальные случаи posting/replay/rollback/конкуренции. Большие нагрузочные прогоны и копия базы для этого шага не нужны.

## Установка и свидетельства

[Текущий manifest](../../db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json): 45 package pairs, native wrappers и guards. [Bundle](../../db/migrations/2026-10-08_stock_posting_core/115_current_runtime.sql) публикует сначала contracts. scripts/stock_posting_install.py обновлён с исторического runtime-016 subset на текущий refresh; он требует уже установленные additive schema phases, PREPARED без B0/operations, сохраняет source checkpoint при --apply. Reset/bootstrap/activation не выполняет. Read-only preflight текущего manifest прошёл, повтор всего DDL ради проверки не запускался.

Применены 082/083, 085, 087/088, 093, 095/096, 098 и 099; ledger 035/036. Source checkpoints содержат только код затронутых объектов. Rollback после committed stock operations запрещён; новые rollback не прогонялись и не объявляются проверенным recovery.

Python compile затронутых сервисов и node --check raw-supply.js прошли. Новых физических posting cases пока 0, поэтому нет доказанной производительности. UOM bootstrap — один set-based SQL; не заменять циклом запросов на каждый SKU. Slow SQL/планы разобрать после первого реального количественного случая. Старый raw TRANSPORT_TASK_PACKAGE_BODY.sql содержит прежний mojibake; исходное свидетельство сохранено.
