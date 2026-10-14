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

Интеграция Codex1261: переданная UI-часть принята; авторские результаты Claude не объявляются независимым ревью или закрытием полного спринта. Общий offline gate после передачи PASS.
