from pathlib import Path
p=Path('wiki/database/nicora_ni051_scoped_policy_20261014.md');s=p.read_text(encoding='utf-8').replace('В реализации, миграция','Применена в dev; завершение storage-proof и положительного native release в работе. Миграция').replace('Применение пока не выполнено.','Миграция применена, ошибки компиляции устранены и проверены.');s+='''

## Результат W1461–1469

[Отчёт65](../../reports/nicora/2026-10-13/65-ni051-scoped-quality.md): рабочий интерфейс настроек, реальное сохранение → потеря ответа → повтор той же операции, одна запись истории, частное правило отключеноv3. P3 не изменён; partial2 и маркированный товар без сканов не проходят исключение/допуск. SQL1–13мс; gate759/0/73,24теста,обаTypeScript и encodingPASS. Чтение proof не создаёт аудит.

[Независимый review](../../reports/nicora/2026-10-13/codex/QC_SCOPE_REVIEW_20261014.md) нашёл F1: переключатель хранения должен требовать отдельный existing full-pallet binding. Ведомый внедряет этот predicate и один native positive QC с audit; нельзя считать синтетический domain доказательством физической отгрузки. Номер исходной партии SAP — supplier_batch, не числовой MES PROD_BATCH_ID.
''';p.write_text(s,encoding='utf-8')
p=Path('wiki/index.md');p.write_text('- [Адресный контроль, report65](../reports/nicora/2026-10-13/65-ni051-scoped-quality.md): Oracle/API/UI, exact replay и текущий экран114; F1 native positive в работе. [Решение по SQL СТ](../reports/nicora/2026-10-13/66-ni022-wide-page-decision.md): ухудшающий hint отвергнут. Gate759/0/73 PASS.\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
with Path('wiki/log.md').open('a',encoding='utf-8') as f:f.write('\n- 2026-10-14: report65 фиксирует applied scoped QC и незавершённый F1/native positive; интерфейс114 приведён к рабочему оформлению, основание освобождения видно QC-пользователю без transport-права. Общий gate759/0/73,24теста/обаTS/encodingPASS. report66 сохраняет отрицательное решение по NL hint без изменения runtime.\n')
