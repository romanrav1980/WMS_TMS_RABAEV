# Предложение wiki-обновления — NI08.1 (для интеграции Codex)

## Новая страница: wiki/components/nicora_ni081_forecast_screen_20261014.md (предлагаемый текст)

```markdown
# NI08.1: экран объяснимого прогноза нагрузки

Экран: wiki-raw/wms_admin_ui_reference/warehouse-forecast.html (warehouse-forecast.js, warehouse-forecast-explain.js, warehouse-forecast.css).
API: POST /api/transport/warehouse-forecast/warehouses/{ware_id}/view (transport_dispatch_view); POST …/project?limit=100 (transport_dispatch_edit) — только явной кнопкой с подтверждением.

- Ввод по границам ForecastRequest (история 1..90, горизонт 1..31, минимум 1..90), ошибки у поля.
- Статусы ответа ADVISORY/NEEDS_PROJECTION/NO_SERIES/INSUFFICIENT_HISTORY и строк READY/NEEDS_PROJECTION/INSUFFICIENT_ACTIVE_HISTORY/BASE_POLICY_REQUIRED объяснены; отсутствие данных ≠ нулевая нагрузка.
- Сводка окна, неполного дня, активных дней, пропусков проекции, подписи данных и времени чтения; метод CALENDAR_DAY_MEAN без сезонности/тренда/интервала.
- Таблица: факт, средняя в сутки, рекомендация, формула из чисел ответа; разные единицы не суммируются; сортировка/поиск по загруженному.
- Смена параметров/пользователя отменяет и убирает результат.
- Ресурсная потребность не вычисляется: нужен контракт сопоставления вида работы с RRL_WORKLOAD_NORM (CONTRACT_REQUEST K-0003).

Отчёт: reports/nicora/2026-10-13/claude/NI08.1/report.md.
```

## index.md — строка
- [NI08.1 экран прогноза нагрузки](components/nicora_ni081_forecast_screen_20261014.md): объяснимые статусы, сводка окна, формула ряда, явное обновление истории; ресурсная потребность — остаток с контрактом.

## log.md — запись
- 2026-10-14 / NI08.1 / Claude K-0004: экран прогноза переработан в назначенных файлах warehouse-forecast.*; проверка ввода по API, объяснения статусов, таблица с формулой, без автоматического /project; CONTRACT_REQUEST K-0003 на ресурсную потребность. Авторская проверка, отчёт reports/nicora/2026-10-13/claude/NI08.1.
