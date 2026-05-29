# Slow SQL Review Runbook

Дата обновления: 2026-05-29.

Назначение: обязательный порядок анализа долгих SQL/SKV-запросов после каждого существенного functional case, load test, release gate или pilot rehearsal.

## Правило

Каждый meaningful gate завершается slow SQL review. Найденный долгий запрос нельзя оставлять как "просто лог": по нему фиксируется одно из решений:

- переписать запрос или убрать N+1;
- сузить окно данных, добавить обязательный `date_from`/`date_to` или pagination;
- добавить batch/`executemany`;
- добавить cache для read-only reference/report endpoint;
- добавить индекс/миграцию и verify query;
- обновить статистику/проверить execution plan;
- явно записать backlog item с причиной, владельцем и порогом возврата.

## Быстрый порядок

1. Перед длинным gate зафиксировать последний `LOG_ID`:

```powershell
curl.exe -s -u admin:admin123 "http://127.0.0.1:8088/api/admin/slow-sql?limit=1"
```

2. После gate посмотреть только свежий интервал:

```powershell
curl.exe -s -u admin:admin123 "http://127.0.0.1:8088/api/admin/slow-sql?from_log_id=<last_log_id_plus_1>&limit=30&min_elapsed_ms=500"
```

3. Посмотреть агрегаты:

```powershell
curl.exe -s -u admin:admin123 "http://127.0.0.1:8088/api/admin/slow-sql/top?limit=20"
curl.exe -s -u admin:admin123 "http://127.0.0.1:8088/api/admin/slow-sql/oracle-top?limit=20"
```

4. Для каждого свежего запроса выше 1000 мс или часто повторяющегося запроса выше 500 мс записать решение в соответствующий runbook/status page.

## ТМС-2 текущий результат

2026-05-29 full release gate marker: `from_log_id=1115`.

Свежий slow SQL review после `scripts\tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeSprint60To95 -IncludeUiSmoke -IncludeLoadSmoke`:

- no critical slow transport query above 1000 ms;
- one fresh `/api/admin/transport/planner/history` entry at `685 ms`, `244` rows, accepted as non-critical;
- previous 6-13s `/api/admin/transport/tasks?date_to=...` entries were caused by unbounded historical fixture lookup in billing tests and were corrected to explicit narrow fixture date ranges;
- current Sprint 60-95 load gate shows `/tasks` p95 about `39-57 ms` and `/available-sts` p95 about `53-232 ms`, below the accepted thresholds.
