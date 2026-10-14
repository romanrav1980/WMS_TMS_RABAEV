# Предложение wiki-обновления — NI07.2 (для интеграции Codex)

## Новая страница: wiki/components/nicora_ni072_day_overview_20261014.md (предлагаемый текст)

```markdown
# NI07.2: обзор сверки дня

Экран: wiki-raw/wms_admin_ui_reference/day-reconciliation.html#dayOverview (day-reconciliation.js, day-reconciliation-catalog.js, day-reconciliation.css).
Источник: GET /api/finance/day-reconciliation/warehouses/{ware_id}?business_date&timezone_region (transport_dispatch_view), read-only.

- Группы: «За сутки» (daily_facts), «Сейчас» (current_backlog + open_items, остатки), «Внешнее» (ERP, госсистемы).
- Каталог показателей: подпись, процесс, смысл, следующее действие, ссылка на существующий реестр (ответ агрегатный — ссылка на реестр, не документ).
- ERP: отправлено ≠ подтверждено; маркировка: отправка отдельно, принятие госсистемой «Не сверялось» (NOT_VERIFIED_BY_THIS_REPORT).
- Неполнота: consistent_snapshot, страница/классификация грузовой зоны, full_regulatory_reconciliation_verified, coverage_complete, задания без пояса, day_closed.
- Устаревший ответ отменяется (AbortController + serial); поля drWare/drDay/drZone сохраняют ID и событие input для соседних блоков.
- Мобильная компоновка: body.day-page{min-width:0} при <1280px (общий styles.css задаёт min-width:1280px).
- Долгий SQL: 666 мс холодный, 8–10 мс повторно — оставить.
- Остаток: ссылки на конкретные документы требуют контракта с ID-образцами по кодам.

Отчёт: reports/nicora/2026-10-13/claude/NI07.2/report.md.
```

## index.md — строка
- [NI07.2 обзор сверки дня](components/nicora_ni072_day_overview_20261014.md): группы за сутки/сейчас/внешнее, причины и реестры, неполнота данных, read-only.

## log.md — запись
- 2026-10-14 / NI07.2 / Claude K-0002: обзор сверки дня переработан в назначенных файлах day-reconciliation.*; каталог показателей, ERP/госответ раздельно, фильтр загруженного, отмена устаревшего ответа, мобильная компоновка; соседние блоки сохранены. Авторская проверка, отчёт reports/nicora/2026-10-13/claude/NI07.2.
