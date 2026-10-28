# T06 mixed-tree preflight review — 28.10.2026

## Проверено

- Локальный API `8088` перезапущен штатным `serv.bat`; `/health` вернул `ok`, OpenAPI содержит маршруты marking-policy и /weigh-line-manual. PID: `62992`.
- C0190 read-only preflight через Oracle выбрал склад `231693372`; он отсутствует, остатков, CASE-заданий и волн нет. Коллизий тестового тега нет, шаблон товара найден. Результат: `findings=[]`.
- Preflight не получал NET или тару и не создавал складских записей. Журнал команд пуст. Снимки: [API readiness](t06-api-ready.json), [состояние preflight](t06-c0190-preflight-state.json).
- Offline runner: 60 тестов прошли. RETAILCASE quality gate, architecture и encoding прошли. Команда `run` остановилась на read-only preflight до первого write: `FIXTURE_CONFIG_RECOVERY_UNVERIFIED`, `PARENT_TARE_KG_REQUIRED`, `MANUAL_NET_KG_REQUIRED`; журнал пуст. Снимок: [блокировка запуска](t06-c0190-run-blocked-state.json).

## Решение

Live `run` блокируется кодом `FIXTURE_CONFIG_RECOVERY_UNVERIFIED`. `Live.meta()` выполняет отдельные Oracle DML и commit для каждой строки НСИ, но не сохраняет восстанавливаемый журнал и не сверяет неопределённый результат. При сбое посередине останутся частичные справочники; повтор может создать конфликт или новый комплект записей. Пока восстановление fixture не реализовано, runner не должен писать в Oracle.

Для прогона также нужны фактические значения NET и тары, введённые оператором. Их не заменяли тестовыми числами. Контроль/LOAD/DEPART и приёмка магазина в C0190 не реализованы. Поэтому T06 остаётся частичным; C0190 принят только как offline runner и read-only preflight. Oracle бизнес-движений не было.