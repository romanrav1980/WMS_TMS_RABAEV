# NI05.1 — адресные правила контроля и целое неизменённое место

Применена в dev; storage-proof и положительный native QC завершены. Миграция `2026-10-14-1447-ni051-scoped-quality`. Основание: NS41-TC03/04/TT01 и раздел настроек `05_quality_release.md`. Проверен live RRL_STOCK_QC_POLICY: warehouse-only mode/independence/sampling, FINAL_WEIGHT_REQUIRED коробки усиливает режим; настройки магазина и освобождение целой монопаллеты отсутствуют. Это реальная доработка кода, не ожидание оборудования.

Владелец quality/inventory. Авторитет — существующие RRL_STOCK_QC_POLICY/GATE под общим Oracle stock root. Новый metadata reader выбирает явное правило по warehouse/subwarehouse (RRL_WARES.PARENT_WARE_ID), адресу магазина и категории STOCK/CASE/ANY; наиболее близкий склад, затем адресное правило, затем категория. До первой адресной настройки сохраняется прежний режим. Отключение override сохраняет версию в истории, чтобы старый допуск не воскресал. Подпись применимых версий входит в текущую QC signature.

Изменение правил — прежняя CONFIG X транзакция, право warehouse_settings_edit и текущий склад, expected_version и operation_id; immutable история, повтор с иным содержимым отклоняется. Ни одного изменения остатка в конфигурации.

Освобождение касается только WEIGHT: CASE с обязательным финальным весом не освобождается. Для STOCK нужно доказательство одной неизменённой исходной физической паллеты: native receipt APPLIED, исходная quantity/UOM равны всему текущему количеству и отгружаемому leg, исходная composition epoch не изменялась после рождения. Неполный/изменённый/восстановленный остаток, несколько leaves или неизвестная legacy provenance не освобождаются автоматически. QR и случайный полный scan действуют независимо. Основание освобождения сохраняется в той же stock-транзакции по operation+ST, без второго проведения.

Checkpoint live sources1443 сохранён до правки; paired rollback не удалит журнал проведённых освобождений. Миграция применена, ошибки компиляции устранены и проверены. User разрешил исполнение спринтов в тестовом RABAEV; отдельная копия базы не нужна.


## Результат W1461–1469

[Отчёт65](../../reports/retailcase/2026-10-13/65-ni051-scoped-quality.md): рабочий интерфейс настроек, реальное сохранение → потеря ответа → повтор той же операции, одна запись истории, частное правило отключеноv3. P3 не изменён; partial2 и маркированный товар без сканов не проходят исключение/допуск. SQL1–13мс; gate759/0/73,24теста,обаTypeScript и encodingPASS. Чтение proof не создаёт аудит.

[Независимый review](../../reports/retailcase/2026-10-13/codex/QC_SCOPE_REVIEW_20261014.md) нашёл F1: переключатель хранения должен требовать отдельный existing full-pallet binding. Ведомый внедряет этот predicate и один native positive QC с audit; нельзя считать синтетический domain доказательством физической отгрузки. Номер исходной партии SAP — supplier_batch, не числовой MES PROD_BATCH_ID.


## Завершение

F1 исправлен и проверен ведущим: existing fullpal binding, DONE task, immutable same-identifier movement, exact qty/UOM/current version. Реальный SAP3EA → putaway1169 → fullpal1168 → bind → QC PLAN ready/audit1/replay; cleanup собственных P/H0, история сохранена. [Итог ведомого](../../reports/retailcase/2026-10-13/codex/QC_F1/REPORT.md).

Добавлен RRL_QC_EXEMPT_DOCUMENT_IX(DOCUMENT_ID), VALID. status_json возвращает weight_exemption_recorded только для текущих ST/signature. Этикетка освобождённой паллеты требует этот факт; GET не создаёт записи. apply включает007, rollback сохраняет additive index/history. installed_manifest.json фиксирует финальные SQL; первоначальный checkpoint не переписан. Оговорка о реконструированном промежуточном gate checkpoint явно сохранена в отчёте ведомого. Gate759/0/73,24теста/обаTS PASS после финального API.
