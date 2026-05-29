# ТМС-2 — Production Migration Checklist

**Дата создания:** 2026-05-29  
**Oracle среда:** `RABAEV` (prod)  
**Ответственный:** DBA + Tech Lead  

---

## Порядок применения миграций

Каждая миграция идемпотентна (CREATE ... если не существует). Применять строго по порядку.

```
042 → 043 → 046 → 047 → 044 → 045 → 051 → 052 → 053 → 054 → 055 → 056 → 058 → 060 → 062
```

---

## Предварительные действия

```sql
-- 1. Убедиться что dev/staging прошёл strict release gate без skips
-- scripts/tms2-release-gate.ps1 -SeedDate 2026-05-24 -IncludeSprint60To95 -IncludeUiSmoke -IncludeLoadSmoke
-- Ожидаемо: no failed commands, no pytest skips, load/UI/NFR green

-- 2. Сделать резервную копию схемы RABAEV
expdp RABAEV/password schemas=RABAEV directory=BACKUP_DIR dumpfile=rabaev_before_tms2_$(date +%Y%m%d).dmp

-- 3. Проверить свободное место в tablespace
SELECT TABLESPACE_NAME, ROUND((BYTES-NVL(FREE,0))/1048576,1) AS USED_MB,
       ROUND(NVL(FREE,0)/1048576,1) AS FREE_MB
  FROM (SELECT TABLESPACE_NAME, SUM(BYTES) BYTES FROM DBA_DATA_FILES GROUP BY TABLESPACE_NAME)
  LEFT JOIN (SELECT TABLESPACE_NAME, SUM(BYTES) FREE FROM DBA_FREE_SPACE GROUP BY TABLESPACE_NAME)
 USING (TABLESPACE_NAME);
-- Требуется ≥ 500 MB свободного места
```

---

## Миграции по блокам

### Блок I — Phase 1 (уже применены в dev, могут требовать применения в prod)

| № | Файл | Содержание | Статус prod |
|---|------|-----------|-------------|
| 042 | `db/migrations/2026-05-21_transport_dispatch_phase1/042_apply.sql` | VIEW `RRL_V_AVAILABLE_STS`, индексы | ⬜ Применить |
| 043 | `db/migrations/2026-05-22_transport_dispatch_improvements/043_apply.sql` | `+VERIFY_PERC`, `+NAPR` в view | ⬜ Применить |

### Блок II — Seed (только dev! prod использует реальные данные)

| № | Файл | Содержание | Статус prod |
|---|------|-----------|-------------|
| 046 | `db/migrations/2026-05-23_dobrotseny_seed/046_apply.sql` | Тестовые данные «Добра Цен» | ⛔ НЕ ПРИМЕНЯТЬ на prod |
| 047 | `db/migrations/2026-05-23_dobrotseny_seed/047_apply.sql` | Тестовые данные «Добра Цен» | ⛔ НЕ ПРИМЕНЯТЬ на prod |

### Блок III — ARM / Операции

| № | Файл | Содержание | Статус prod |
|---|------|-----------|-------------|
| 044 | `db/migrations/2026-05-27_transport_sprint11/044_apply.sql` | `RRL_TRANSPORT_NORMS`, `RRL_TT_OPERATIONS`, 12 seed нормативов | ⬜ Применить |

### Блок IV — MAP / Координаты

| № | Файл | Содержание | Статус prod |
|---|------|-----------|-------------|
| 045 | `db/migrations/2026-05-26_transport_sprint7/045_apply.sql` | `LATITUDE`, `LONGITUDE`, `MAX_VEHICLE_TONS`, `UNLOAD_NORM_MIN`, `TW_STRICT` в `RRL_ADDR`; `RRL_ADDR_DISTANCE_MATRIX`; `RRL_PLANNER_PLANS` | ⬜ Применить |
| 051 | `db/migrations/2026-05-26_transport_sprint7/051_apply.sql` | Координаты dev-адресов (seed-like, но безопасно — UPDATE WHERE LATITUDE IS NULL) | ⬜ Проверить, применить если безопасно |
| 052 | `db/migrations/2026-05-26_transport_sprint8/052_apply.sql` | `APPLIED_AT`, индексы на матрицу и планы | ⬜ Применить |

### Блок V — Биллинг

| № | Файл | Содержание | Статус prod |
|---|------|-----------|-------------|
| 053 | `db/migrations/2026-05-27_transport_sprint11/053_apply.sql` | `RRL_TRANSPORT_NORMS` + `RRL_TT_OPERATIONS` + 12 нормативов (идемпотентно) | ⬜ Применить |
| 054 | `db/migrations/2026-05-27_transport_sprint15/054_apply.sql` | `SEQ_BILL_ORDERS` + `RRL_BILL_ORDERS` | ⬜ Применить |

### Блок VI — Фаза 3 (Sprint 97–119)

| № | Файл | Содержание | Статус prod |
|---|------|-----------|-------------|
| 055 | `db/migrations/2026-05-29_fleet_crud/055_apply.sql` | `SEQ_TR_VEHICLE` + `RRL_TR_VEHICLE_ADD/UPDATE/DEL` | ⬜ Применить |
| 056 | `db/migrations/2026-05-29_fleet_crud/056_apply.sql` | `SEQ_TR_VODITEL` + `RRL_TR_VODITEL_ADD/UPDATE/DEL` + колонки `LICENSE_NUMBER`, `COMPANY` | ⬜ Применить |
| 058 | `db/migrations/2026-05-29_notifications/058_apply.sql` | `RRL_PUSH_SUBSCRIPTIONS` + `RRL_NOTIFICATION_SETTINGS` | ⬜ Применить |
| 060 | `db/migrations/2026-05-29_gps/060_apply.sql` | `RRL_VEHICLE_GPS` + `RRL_VEHICLE_GPS_LAST` + индекс | ⬜ Применить |
| 062 | `db/migrations/2026-05-29_geofencing/062_apply.sql` | `RRL_ADDR.GEO_FENCE_RADIUS_M NUMBER(5) DEFAULT 200` | ⬜ Применить |

---

## Скрипт последовательного применения (Oracle SQL*Plus)

```sql
-- Запускать из корня проекта: sqlplus RABAEV/password@prod @scripts/apply_prod_migrations.sql

-- === Phase 1 ===
@db/migrations/2026-05-21_transport_dispatch_phase1/042_apply.sql
@db/migrations/2026-05-22_transport_dispatch_improvements/043_apply.sql

-- === ARM / Gantt ===
@db/migrations/2026-05-27_transport_sprint11/044_apply.sql

-- === MAP / VRP ===
@db/migrations/2026-05-26_transport_sprint7/045_apply.sql
@db/migrations/2026-05-26_transport_sprint8/052_apply.sql

-- === Billing ===
@db/migrations/2026-05-27_transport_sprint15/054_apply.sql

-- === Fleet CRUD ===
@db/migrations/2026-05-29_fleet_crud/055_apply.sql
@db/migrations/2026-05-29_fleet_crud/056_apply.sql

-- === Notifications ===
@db/migrations/2026-05-29_notifications/058_apply.sql

-- === GPS ===
@db/migrations/2026-05-29_gps/060_apply.sql

-- === Geofencing ===
@db/migrations/2026-05-29_geofencing/062_apply.sql

COMMIT;
EXIT;
```

---

## Smoke-проверки после каждой миграции

```sql
-- После 042: проверить view
SELECT COUNT(*) FROM RABAEV.RRL_V_AVAILABLE_STS WHERE ROWNUM <= 1;

-- После 044: проверить таблицу операций
SELECT COUNT(*) FROM RABAEV.RRL_TT_OPERATIONS;  -- 0 (пусто до создания рейсов)
SELECT COUNT(*) FROM RABAEV.RRL_TRANSPORT_NORMS; -- 12 (seed нормативов)

-- После 045: проверить колонки
SELECT LATITUDE, LONGITUDE FROM RABAEV.RRL_ADDR WHERE ROWNUM = 1;

-- После 054: проверить таблицу биллинга
SELECT COUNT(*) FROM RABAEV.RRL_BILL_ORDERS;

-- После 055: проверить функцию создания ТС
SELECT RABAEV.RRL_TR_VEHICLE_ADD('TEST-SMOKE', NULL, 5000, 10, 1, NULL) AS NEW_ID FROM DUAL;
-- Затем удалить созданный тест:
-- DELETE FROM RABAEV.RRL_TR_VEHICLE WHERE NUM_PLAT='TEST-SMOKE'; COMMIT;

-- После 060: проверить GPS таблицы
SELECT COUNT(*) FROM RABAEV.RRL_VEHICLE_GPS_LAST;

-- После 062: проверить колонку геозоны
SELECT COUNT(*) FROM RABAEV.RRL_ADDR WHERE GEO_FENCE_RADIUS_M IS NOT NULL;
```

---

## Post-migration: запуск release gate

```powershell
# Запустить из корня проекта с реальной prod БД
$env:TMS_ORACLE = "RABAEV/password@prod-oracle:1521/PRODDB"
python -m pytest tests\transport\test_sprint96_functional.py `
    tests\transport\test_sprint97_98_functional.py `
    tests\transport\test_sprint99_100_functional.py `
    tests\transport\test_sprint101_102_functional.py `
    tests\transport\test_sprint103_107_functional.py `
    tests\transport\test_sprint108_114_functional.py `
    tests\transport\test_sprint115_119_functional.py `
    -q -ra --tb=short
# Ожидаем: 100+ passed, 0 failed
```

## Post-gate: slow SQL/SKV review

После каждого prod/staging gate обязательно выполнить [`slow_sql_review.md`](slow_sql_review.md):

```powershell
curl.exe -s -u admin:admin123 "http://127.0.0.1:8088/api/admin/slow-sql?limit=1"
curl.exe -s -u admin:admin123 "http://127.0.0.1:8088/api/admin/slow-sql?from_log_id=<last_log_id_plus_1>&limit=30&min_elapsed_ms=500"
curl.exe -s -u admin:admin123 "http://127.0.0.1:8088/api/admin/slow-sql/oracle-top?limit=20"
```

Любой свежий SQL выше `1000 ms` или повторяющийся SQL выше `500 ms` должен получить решение до pilot/prod sign-off: правка кода, сужение окна, batch/cache, индекс/миграция, statistics/plan check или оформленный backlog item.

---

## Rollback план

| Если ошибка в миграции | Действие |
|------------------------|---------|
| 042-043 | `@db/migrations/2026-05-21_transport_dispatch_phase1/042_rollback.sql` |
| 044 | Нет rollback — DROP TABLE RRL_TRANSPORT_NORMS, RRL_TT_OPERATIONS |
| 045 | `ALTER TABLE RRL_ADDR DROP COLUMN LATITUDE, LONGITUDE, ...` |
| 055-056 | `@db/migrations/2026-05-29_fleet_crud/055_rollback.sql` и `056_rollback.sql` |
| 058-062 | DROP TABLE соответствующей таблицы |

---

## Параллельная эксплуатация C# + React

После успешного применения миграций:

1. ✅ Запустить API: `serv.bat` (порт 8088)
2. ✅ Запустить Frontend: `front.bat` (порт 3000)
3. ✅ Проверить C# WinForms: открыть `tabPage6` — убедиться что не сломан
4. ⏳ Дать диспетчерам работать в React 5 рабочих дней параллельно с C#
5. ✅ Если AT-D-01..AT-D-12 прошли на prod-данных — отключить C# tabPage6
