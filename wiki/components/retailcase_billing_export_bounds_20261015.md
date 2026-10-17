# Excel биллинга: полный файл и явные границы · 15.10.2026

AK05-EXPORT02. Проверены оба оставшихся transport billing XLSX: `/billing/orders/export.xlsx` и `/billing/orders/{id}/export.xlsx`. `tasks/export.xlsx` уже исправлен предыдущим инкрементом; VRP `text/event-stream` — отдельный длительный поток, не Excel.

## Факты и изменение

До изменения реальные HTTP файлы реестра25338байт и счёта5285346байт прошли ZIP CRC. В текущей редакции audit middleware уже читает полный iterator: прежняя порча tasks/export не воспроизвелась для этих файлов. Поэтому это не объявляется вновь обнаруженной текущей порчей ZIP. Отсутствовали Content-Length и границы источников: legacy export вызывал неограниченные списки.

Новый read model владельца finance (`modules/finance/infrastructure/billing_export_reads.py`) читает каждый workbook одним READ ONLY снимком. Реестр сохраняет прежние company LIKE/date-from/date-to/closed/payed фильтры и порядок ID desc, применяет фильтры до2001sentinel. Более2000счетов дают явный409 `BILLING_EXPORT_ORDER_BOUND_2000`, без частичного файла и без скрытого окна дат. Денежные агрегаты включают все рейсы выбранных счетов; лимит не обрезает суммы. Один счёт читает не более5001рейсов, >5000 даёт409 `BILLING_EXPORT_TASK_BOUND_5000`. Несуществующий счёт404, пустой реестр — валидная книга с нулевым итогом.

Legacy renderer и формат колонок сохранены; большая функция не расширена. Router использует finance API helper: обычный полный `Response`, правильный XLSX Content-Type, attachment и автоматически точный Content-Length; готовый файл дополнительно ограничен32МБ с409. `StreamingResponse` остался у VRP SSE. Права endpoints остались прежними `transport_dispatch_view` через legacy permission dependency; эта задача не переводит биллинг на scoped warehouse native view и не доказывает такой доступ. Oracle структура/бизнес-строки не изменялись.

## Доказательства

[Live скрипт](../../scripts/billing_export_live_smoke.py), [результат](../../reports/retailcase/2026-10-15/dispatch-scope/billing-exports.json): реестр527счетов, счёт526с одним реальным рейсом и пустой отфильтрованный реестр прошли ZIP CRC, Content Types/Workbook XML и точный Content-Length; строки и суммы сверены с реальными JSON read endpoints. Проверены404 отсутствующего счёта и401 без credentials. Секреты в отчёт не пишутся.

[Focused tests](../../tests/retailcase/test_billing_export_bounds.py) проверяют пустой/нормальный/максимальный источник, отказ на2001/5001, сохранение полной денежной агрегации и исходный403 без права; HTTP mapping возвращает409 вместо файла. Это тестовые read-model ответы; тысячи фиктивных бизнес-строк в live Oracle не создавались.

HTTP реестр446мс, счёт64мс, пустой47мс. После прогона RRL_SQL_SLOW_LOG за час пуст. Решение finance/Codex: оставить bounded selected headers и ограниченный task detail, никаких предположительных индексов. При повторении >1000мс атрибутировать SQL и посмотреть план. API audit прошли реальные read HTTP вызовы. Независимый биллинговый пилот и native scoped перевод остаются отдельными задачами.

Архитектурный анализ не выявил новых/выросших нарушений и циклов; уменьшение legacy файлов требует штатного `--tighten-baseline`, который выполняет root после совместной интеграции. Общий gate этой карточкой не объявляется выполненным. UTF-8 проверка PASS.
