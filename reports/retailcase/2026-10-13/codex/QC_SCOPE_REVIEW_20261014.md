# NI05.1 — независимое чтение нового QC scope

14.10.2026, ведомый Codex. Только чтение актуальных001–006 SQL и quality_scope.py/quality_scope_routes.py. Ни DDL, ни тесты, ни stock writes не выполнялись в рамках review. Runtime proof ведущего не заменяется этим чтением.

## Finding

**F1 — EXEMPT_STORAGE не имеет отдельного условия.** `002_reader.sql / exemption_json`: после `if exempt_whole!=1 and exempt_storage!=1 then return` оба переключателя идут по одному whole-native-receipt predicate. При whole=false/storage=true можно освободить любое подходящее целое место без отдельной проверки «со штрихкодом хранения». Требование: `wiki/requirements/retailcase_business_processes/05_quality_release.md:11`. Нужен существующий authoritative physical-bound/storage-identifier признак для storage-ветки либо явное устранение обещания двух независимых правил. Не предлагается выдумывать новый barcode registry. Передано ведущему немедленно.

## Прочитанные свойства — замечаний в обозначенной области не найдено

- Количество: один leg, не CASE; исходный POSTED_BASE_QTY, current sum(REMAIN), отгружаемое количество и UOM сопоставляются; composition epoch1, APPLIED receipt, birth operation/origin, material/expiry/produced проверяются. Epoch имеет NOT NULL constraint. Supplier batch не подменяется числовым MES batch. UID builtin fix уже учтён в текущем reader.
- QR: eligible заменяет только weight_ok. Затем независимо вызываются обязательные mark proof и full item scan; отсутствие нужного scan не превращается в готовность.
- Выборка: сохраняются sample bucket/selected/rescan; неизвестный bucket при percent>0 запрещает допуск. Отказ QC выставляет rescan_required.
- Малые коробки: case_task не получает exemption, FINAL_WEIGHT_REQUIRED усиливает effective mode и final scale admission остаётся в gate.
- Подпись: version stamp применимых scope overrides включён в composition signature; фактическое правило читается под общим CONFIG, изменение API увеличивает version. Disabled rule остаётся в stamp и истории.
- Атомарность: record_exemption размещён внутри execute перед фактической отгрузкой и после gate; тот же stock root OP/TX, lockST и FK; последующая ошибка root должна откатить и audit. Readonly status не вызывает record. Immutable insert/journal guards присутствуют.
- Конфигурация: current actor/warehouse/permission, CONFIG X, expected version, canonical request hash, exact replay возвращает receipt; changed body не перезаписывает правило. Decimal percentage, диапазон и scale ограничены в API. RRL_WARES singleton проверяется trigger, поскольку unique constraint отсутствует.

## Предел

Это scoped static review, не утверждение о положительной новой physical shipment, нагрузке или внешней независимой приёмке. После исправления F1 требуется короткое чтение конкретного predicate, без повторного общего аудита.

## F1 resolved

Applied existing native fullpal-binding proof and completed real SAP receipt → fullpal → QC PLAN/audit/replay. See [final evidence](QC_F1/REPORT.md). Status additionally exposes current-signature recorded exemption for the label release guard.
