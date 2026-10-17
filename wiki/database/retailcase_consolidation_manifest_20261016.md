# Ожидаемый состав консолидации

Статус dev APPLIED; ограниченный сценарий проверен автором, независимая приёмка открыта. Блок2/AK06-F: планирование состава и его проверка перед отгрузкой. Основание — [[../concepts/retailcase_nested_hu_consolidation_20261015]], принятый владельцем смешанный процесс.

Физическое дерево `RRL_PALLETS/RRL_WMS_HU_LINK`, PICKED fulfilment → CASE/STOCK, current ST binding и native HU_SHIP сохранены. Добавлен отдельно сохраняемый ожидаемый состав. Доработка не создаёт запас, SSCC, физические связи или межскладскую приёмку.

Владелец — fulfillment; Oracle — единственное место правил и транзакции. Версионируемый план: целевой склад/ячейка, планируемый внутренний идентификатор корня, до200 существующих fulfilment IDs. Участник может оставаться PLANNED до сборки; форма физической вложенности определяется прежним HU tree. Сохраняются ST identity и подпись подготовленных строк. План отделён от физической иерархии; DAG вложенных планов в этот ограниченный инкремент не входит.

SAVE/CANCEL требуют `warehouse_task_execute` на целевом складе, VIEW — `warehouse_task_view`; доступ к источникам участников проверяется до выдачи подробностей. SELF без подтверждённого владельца не даёт права планировать общую паллету. Роль проверяется до replay и под REV→CONFIG; старое и новое назначение плана требуют своих областей. Точное повторение operation_id возвращает исходный ACK, новое тело конфликтует. История команд неизменяема.

Готовность сверяет actual WARE/cell/top-level root, неизменность ST refs/строк, ожидаемые/фактические ST без лишних/неизвестных листьев. Другая ячейка/склад означает «не прибыл», а не физическое вложение. Native HU_SHIP получает admission token и повторяет проверку под прежними CONFIG/stock/CASE locks до эффекта. Эта готовность не является QC или измерением массы; прежние quantity/quality/loading owners сохраняются. У корня без зарегистрированного ACTIVE плана сохраняется legacy-путь.

Сценарий проверки: существующая mixed26EA фикстура, два реальных fulfilment; план с недостающим PLANNED fulfilment блокирует отгрузку, исправленный план допускает только проверку состава. Дополнительно: exact replay/body conflict/stale version/current revoke и caller rollback без изменения физического дерева. Изоляция — прежний TEST WARE20220394; новые журналы не удаляются. Нагрузка и аппаратная приёмка сейчас не запускаются.

Зависимости: [fresh sources](../../reports/retailcase/2026-10-16/consolidation-manifest/before/manifest.json). [SQL kit](../../db/migrations/2026-10-16_consolidation_manifest/README.md), MIGRATION_ID `2026-10-16-consolidation-manifest`; текущий frozen SHA `87572a063a121dc865ecb06656d69ce028c7a61356fce9c77cb1deb539e6efd6`. Python API SAVE/READ/CANCEL и native SHIP hook подготовлены; quality gate1102/0циклов/debt72/tooling24/обаTS PASS. Авторские проверки не заменяют независимую приёмку.

Первый apply комплекта52bab71b остановился на compile gate: слитый `node_uid_valueand` в READ body,2 ошибки строки58, только этот body INVALID. Таблицы/остальные пакеты/триггеры созданы, ledger отсутствовал, товарных команд не было. [Исходный комплект](../../reports/retailcase/2026-10-16/consolidation-manifest/original-kit-v2/frozen-manifest.json) и [inspection](../../reports/retailcase/2026-10-16/consolidation-manifest/partial-inspection.json) сохранены. Исправлен один пробел; `complete_partial.sql` проверил точные частичные source SHA, именно эти2 ошибки, пустую metadata и отсутствие ledger, затем заменил только READ body и выполнил полную verify. Полный apply повторно не запускался. [Completion](../../reports/retailcase/2026-10-16/consolidation-manifest/root-complete.json) и независимый от installer read-only [readback](../../reports/retailcase/2026-10-16/consolidation-manifest/root-readback.json):15 source SHA совпали, USER_ERRORS0/INVALID0, ledger APPLIED. Это не независимое ревью автора.

Новые таблицы: `RRL_HU_CONSOL_PLAN` (версия/целевая зона/статус), `RRL_HU_CONSOL_MEMBER` (fulfilment/ST identity/подпись строк), `RRL_HU_CONSOL_RECEIPT` (неизменяемое тело/frozen expectations/ACK). Триггеры разрешают запись только внутри native owner context в текущей транзакции с CONFIG6. Пустой rollback восстанавливает прежний HU_SHIP и удаляет новые объекты; после сохранения любой истории требует forward recovery, а не DELETE журнала.

## Проверенный результат и границы

[Функциональный сценарий](../../reports/retailcase/2026-10-16/consolidation-manifest/acceptance.json), [отмена, отзыв доступа и SQL](../../reports/retailcase/2026-10-16/consolidation-manifest/completion-sql.json):16 HTTP с16 Oracle/local audit pairs, max648мс. План из fulfilment191/192/193 при физических191/192 сообщает missing1 и блокирует native HU_SHIP. Исправление до191/192 даёт ready=true; physical tree hash и26EA неизменны. Проверены точный replay, конфликт тела, устаревшая версия, чужой склад, отзыв READ/replay, отмена с неизменяемой историей. Будущий корень и PLANNED193 сохраняются до появления CASE/физической паллеты.

Тестовый доступ закрыт: роль неактивна, назначение отозвано, пользователь DELETED. Полный ACTIVE план остаётся на TEST mixed root; будущий план CANCELLED, подготовленные order/ST/fulfilment193 и receipts сохранены. Физического отгружания и аппаратного взвешивания не выполнялось. ready=true в UI означает «Состав полон»; QC, масса, загрузка и температурная приёмка имеют отдельные решения. CASE-aware interWARE, subtree handover, дерево вложенных логических планов и пустая CASE после all-short этим инкрементом не закрыты.

API: GET/PUT `/api/consolidation-plans/{plan_id}`, POST `/{plan_id}/cancel`. PUT: operation_id, expected_version, reason, root_identifier, warehouse_id, cell, fulfillment_ids. Идентификатор паллеты допускает внутренний UID и прежние идентификаторы; actor берётся только из сессии. CANCEL сохраняет историю; отменённый ID не переиспользуется. При uncertain503 повторяется неизменная команда с прежним operation_id. UI ещё не добавлен.

Справка consolidation-plan опубликована штатными ARTICLE_SAVE/PUBLISH в native
revision2; [публикация](../../reports/retailcase/2026-10-16/consolidation-manifest/help-publication.json),
[чтение/поиск и SQL](../../reports/retailcase/2026-10-16/consolidation-manifest/help-read.json):4HTTP/4pairs/max155мс/0slow.
Первый GET до native publication вернул404: runtime использует Oracle override,
а не файловый каталог. Файл docs/help/published.json сам не меняет runtime.
После замечания владельца дальнейшая обычная справка должна использовать простой
локальный URL: [[../components/retailcase_simple_solution_rule_20261016]].

## Решение по SQL

В6 slow-log записях отмечены целые transaction blocks12–53мс, а не SQL дольше500мс. Native command `an1x5prszdqct`:11 executions, average70мс; это не p95. Самые дорогие V$SQL — migration dictionary verification: `3q4fssmjqmw69`4954мс и `2znm7j098ktcb`4051мс, по одному выполнению, ограничены3 новыми таблицами. Причина холодного кеша не доказана. Решение: сохранять ограничения по именам объектов; владелец migration tooling проверяет dictionary plan/statistics при повторении или превышении deployment budget, без индексов SYS и переноса каталога в runtime. Для бизнес-пути остаются bounds200 участников/200 строк ST/2000 closure references и существующие ключи. Fulfillment owner измерит legacy ST PALLET_UID lookup на пилоте; индекс/кеш без измеренного runtime bottleneck не вводится.
