# Scoped-чтение волн и времени · 15.10.2026

Миграция2026-10-15-wave-scoped-views, PREPARED. Native RRL_WAVE_EXEC_ACCESS.assert_scope и RRL_WAVE_TIME_API.actor_allowed для **только pick_wave_view** используют RRL_ACCESS_API.allowed по фактическому складу волны. Проверка чистая и допустима в READ ONLY. Остальные команды/права запуска/отмены не получают обхода старого допуска.

[Apply](../../db/migrations/2026-10-15_wave_scoped_views/apply.sql), before bodies/rollback/verify/checkpoint рядом. TargetRABAEV/orcl, INVALID до0; текущийHEAD+SHA256 сохранены до apply. Поручение владельца — исполнить все принятые AK/KH спринты. API queue/details/readiness/pick-readiness/execution/time-context подключаются к native после apply. Пользователи/роли массово не меняются, stockNONE. [[architecture/retailcase_resource_gantt_shift_supervisor]].

## Результат

APPLIED, USER_ERRORS0/INVALID0 проверяются по target пакетам. API wave list/header/detail/readiness/pick-readiness/execution/time-context используют identity и native view. При одном назначенном складе queue выбирает его, при нескольких требует явный ware_id; GLOBAL_ADMIN сохраняет общий обзор. Replenishment-progress также проверяет actual wave scope вместо прежнего плоского разрешения на все волны.

8live HTTP/native checks PASS: всеviewисточники нового пользователя NONE; foreigndirect403; одна/несколькообластей; revoke; пакет/лимиты; пополнение. Fixturesusers/roles удалены, волны только читались, stockNONE. [Evidence](../../reports/retailcase/2026-10-15/wave-scope/http-native.json).

POST /api/picking/shift-overview {warehouse_id,wave_ids<=50distinct} объединяет existingreadiness/pick/time/replenishment в одной READ ONLY Oraclelease. Весь набор проверяется по складу до выдачи; чужойid404, безwarehouseмандата403, duplicate/51ids422. Ошибки источников отдельно, отсутствующие данные не объявляются готовностью. Несколько пачек не обещают snapshot всейсмены. Запуск/отмена/резервы этим не реализованы заново, старые write-guards сохранены.
