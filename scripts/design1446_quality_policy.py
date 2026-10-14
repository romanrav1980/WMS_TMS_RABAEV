from pathlib import Path
p=Path('wiki/database/nicora_ni051_scoped_policy_20261014.md');p.write_text('''# NI05.1 — адресные правила контроля и целое неизменённое место

В реализации, миграция `2026-10-14-1447-ni051-scoped-quality`. Основание: NS41-TC03/04/TT01 и раздел настроек `05_quality_release.md`. Проверен live RRL_STOCK_QC_POLICY: warehouse-only mode/independence/sampling, FINAL_WEIGHT_REQUIRED коробки усиливает режим; настройки магазина и освобождение целой монопаллеты отсутствуют. Это реальная доработка кода, не ожидание оборудования.

Владелец quality/inventory. Авторитет — существующие RRL_STOCK_QC_POLICY/GATE под общим Oracle stock root. Новый metadata reader выбирает явное правило по warehouse/subwarehouse (RRL_WARES.PARENT_WARE_ID), адресу магазина и категории STOCK/CASE/ANY; наиболее близкий склад, затем адресное правило, затем категория. До первой адресной настройки сохраняется прежний режим. Отключение override сохраняет версию в истории, чтобы старый допуск не воскресал. Подпись применимых версий входит в текущую QC signature.

Изменение правил — прежняя CONFIG X транзакция, право warehouse_settings_edit и текущий склад, expected_version и operation_id; immutable история, повтор с иным содержимым отклоняется. Ни одного изменения остатка в конфигурации.

Освобождение касается только WEIGHT: CASE с обязательным финальным весом не освобождается. Для STOCK нужно доказательство одной неизменённой исходной физической паллеты: native receipt APPLIED, исходная quantity/UOM равны всему текущему количеству и отгружаемому leg, исходная composition epoch не изменялась после рождения. Неполный/изменённый/восстановленный остаток, несколько leaves или неизвестная legacy provenance не освобождаются автоматически. QR и случайный полный scan действуют независимо. Основание освобождения сохраняется в той же stock-транзакции по operation+ST, без второго проведения.

Checkpoint live sources1443 сохранён до правки; paired rollback не удалит журнал проведённых освобождений. Применение пока не выполнено. User разрешил исполнение спринтов в тестовом RABAEV; отдельная копия базы не нужна.
''',encoding='utf-8')
p=Path('wiki/index.md');p.write_text('- [Адресные правила контроля NI05.1](database/nicora_ni051_scoped_policy_20261014.md): подтверждён обязательный кодовый остаток NS41; Oracle в работе. Ведомый реализует NI08.1 единый маршрут с перерывами. Все спринты ещё не завершены.\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=Path('wiki/log.md');p.open('a',encoding='utf-8').write('\n- 2026-10-14: live1443–1445 подтвердил отсутствие store/subwarehouse category overrides и освобождения whole unchanged STOCK в QC policy. Root NI05.1/1447 в реализации; ведомый NI08.1 route rest/final approval. Эти кодовые остатки не подменяются внешней приёмкой.\n')
