# NS00: паспорт, воспроизводимый запуск и DS-BASE

**Последнее поручение владельца, 7 октября 2026 года:** дополнительные проверки и Oracle-эксперименты остановлены; минимум 80% ресурсов на функционал. Приведённые ниже команды и pending gates сохранены как история и справочник, не как задание на новые прогоны. Завершается только source review. Cold Oracle install — дополнительный эксперимент, не обязательное условие NS00; временная копия выключена. [Структура исходников](../components/nicora_source_structure.md).

7 октября 2026 года. Техническое ядро NS00 реализовано и проверено автором в существующей RABAEV. Статус спринта остаётся **in_progress**: независимая проверка и приёмка владельцем не проведены; холодная установка Oracle-структуры с нуля отдельно не подтверждена. NS01 по последнему поручению остановлен до реализации NS00; для NS01 были только чтения, ID требований не назначались.

## Что работает

- ORCL/orcl/RABAEV; новых схем и DDL нет. INVALID=0, активных ошибок компиляции=0. Все шесть verification профилей OracleApply повторно прошли. Прежний NS00 checkpoint и 59 перекомпилированных объектов сохраняются в db/restore_points/nicora_ns00_20261007/.
- API 8088, ARM 3000 и ТСД 3010 доступны. API работает из новой `api/wms_api_server/.venv` без system-site-packages. Версии и wheel hashes закреплены в [Windows/Python 3.13 lock](../../api/wms_api_server/requirements-ns00-win-py313.lock): 30 пакетов. Пропущенный runtime import httpx добавлен в requirements.txt. pip check и import API прошли.
- Оба frontend установлены в новые каталоги через npm ci по неизменённым lockfile и собраны с typecheck. Для старых peer ranges используется явный --legacy-peer-deps. Офлайн попытка ТСД не прошла из-за отсутствия toggle-selection в npm cache; новый online install/build прошёл. Это не полный offline install без подготовленного cache.
- [DS-BASE core](../database/nicora_ns00_fixture.md) — 22 owned строки в девяти существующих таблицах. Seed, повтор, reset, cleanup=0 и reseed=22 проверены. API/Oracle одинаково показывают 2400 штук D10; заказы 40/30/30 коробок. Все внешние остатки и связанные паллеты, остальные строки затронутых справочников/ячеек/заказов совпали по SHA256 между стадиями.
- Три live negative probes: отсутствие provenance, изменённая owned строка, ORA-01400 после начала перестроения. Первые два отказали без изменений, третий доказал полный transactional rollback.
- PATCH настоящего API сохранил параметры тестового DS-BASE-D10, затем все три приложения остановлены и запущены с новыми listener PID. Факт и запас совпали после restart. Первоначальная остановка выявила child-first Uvicorn respawn; scripts/kill-port.ps1 теперь останавливает supervisor перед сохранёнными descendants. Отдельный failure report сохранён, после исправления повтор прошёл. Сообщения taskkill о уже завершившихся дочерних PID не означают оставшийся listener; его отсутствие проверяется отдельно.
- Авторский quality gate: architecture PASS, 23 tests passed, оба исходных frontend typecheck PASS. Новые install/build выполнены отдельно на новых dependencies. Это не независимая Claude-приёмка.

## Воспроизведение

Из корня репозитория, на Windows x64 / Python 3.13 / Node 22:

```powershell
# На чистых каталогах; существующие каталоги скрипты не удаляют.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/prepare-nicora-python.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/prepare-nicora-frontends.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-nicora-dev.ps1 -Restart
python -m tools.nicora_environment seed
python -m tools.nicora_environment verify
```

Для уже подготовленного стенда достаточно root serv.bat/front.bat/terminal.bat либо start-nicora-dev.ps1. Root serv.bat автоматически использует .venv; параметр TMS_PYTHON_CMD позволяет проверить другое подготовленное окружение. Front/terminal имеют directory overrides и --strictPort. Node packages исходных интерфейсов уже присутствуют, свежие copies проверены отдельно. Пароли в паспорт/evidence не выводятся; используются имеющиеся dev-настройки.

Проверка reset и persistence:

```powershell
python -m tools.nicora_environment mark
python -m tools.nicora_environment reset
python -m tools.nicora_environment verify
python -m tests.smoke.nicora_ns00_environment_smoke
python -m tools.nicora_environment record-fact
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start-nicora-dev.ps1 -Restart
python -m tools.nicora_environment verify-restart
python -m tools.nicora_environment sql-review
```

Negative runner ожидает только что reset baseline. Вмешательство другого оператора в owned строки блокирует очистку; нельзя вручную менять manifest ради PASS. SQL-шаблоны исполняются через provenance-checking CLI, не самостоятельно. Namespace DS-BASE — строки в RABAEV, не отдельная схема.

## Статусы сценариев и предел доказательства

| Сценарий | Фактический результат |
|---|---|
| NS00-TC01 | PASS новой установки API/ARM/TSD и запуска на существующей RABAEV; полная cold Oracle install остаётся PENDING_COLD_ORACLE_INSTALL |
| NS00-TC02 | PASS_LIVE: сброс owned ядра DS-BASE, cleanup/reseed, сохранность внешнего запаса, защита и rollback |
| NS00-TC03 | PASS_LIVE: реальный API fact, остановка трёх приложений, новые PID, сохранность Oracle/API факта и 2400 штук |

Декларативные business settings и профили из base/track_trace не стали реализованными функциями; сопоставление всех полей — NS02–NS04. Перезапуск проверял приложения, не аварийное восстановление Oracle VM. From-zero installer здесь не запускали поверх 758382 исторических паллет: его разрушительный DROP/recreate не доказывал бы сохранность текущих данных. Это незакрытый дополнительный installation gate, не скрытый PASS. Никакой rollout/pilot или проверка нагрузки не выполнены.

## UI и известные предупреждения

ARM shell открывается без pageerror; главная — существующая demo/replay-панель, не доказательство баланса RABAEV. ТСД авторизован через реальный GET_RUSER; диагностика показывает API ok, user RABAEV, service orcl. После restart нет JS pageerror, но Ant Design пишет два console.error предупреждения: React 19 compatibility и static message/context. Build также предупреждает о крупных chunks и leaflet-draw default export. Backlog NS06/UI hardening, owner — frontend: подтвердить поддержку React 19, заменить static message контекстным API, проверить карту и разделение bundles перед UI release. Эти предупреждения не объявлены нулём и не блокируют проверенное подключение API к Oracle.

## SQL решение

Marker LOG_ID=1246 и API_CALL_ID=36132 сняты до fixture gate. Свежих Oracle slow-log записей после marker нет. Oracle top, module NICORA_NS00: крупнейшие средние 418 мс (полная проверка ячеек), 353 мс (exact reference ARTICUL в паллетах), 238 мс (только паллеты с остатком). Локальная проверка 66165 ячеек с выгрузкой и SHA256 занимала до 2483 мс; это fetch/hash end-to-end, не чистое время SQL.

Решение: полное сравнение требуется для isolation evidence, поэтому выполнять диагностически пакетами arraysize=1000 с fail-closed cap 150000 строк. Не переносить эти queries в складской runtime. Исторические паллеты ограничены EXISTS по действующему остатку, внешние ссылки — rownum=1, журналы — окна marker+limit. Новых индексов для NS00 не добавлять; NS02 Oracle GAP владеет повторной проверкой плана и индексов при реальном functional/load mix. [Local decisions](../../runtime/test-evidence/nicora_ns00/local-sql-review.json), [Oracle/API review](../../runtime/test-evidence/nicora_ns00/sql-review.json). По markers не заявляется уникальная фильтрация всех параллельных API клиентов: учитывается весь последующий журнал с явным окном.

## Пакет результата

[Отчёт](../../runtime/test-evidence/nicora_ns00/report.md) · [JSON](../../runtime/test-evidence/nicora_ns00/report.json) · [Паспорт](../../runtime/test-evidence/nicora_ns00/passport.json) · [Evidence page](../../runtime/test-evidence/nicora_ns00/evidence-presentation.html).

[Fixture manifest](../../runtime/test-evidence/nicora_ns00/fixture-manifest.json), [cross-stage preservation](../../runtime/test-evidence/nicora_ns00/cross-stage-preservation.json), [negative probes](../../runtime/test-evidence/nicora_ns00/negative-probes.json), [restart](../../runtime/test-evidence/nicora_ns00/restart-after.json), [Oracle profiles](../../runtime/test-evidence/nicora_ns00/profile-verification.json). Первое failure evidence и первоначальный code hash checkpoint сохранены; полный Oracle backup не создавался. Независимый reviewer и владелец получают точные исходники/evidence; NS00 не переводится в accepted автоматически. Публикации не было.

## UTF-8 в Windows

При подготовке документации Windows PowerShell 5 pipe в Python может заменить кириллицу на вопросительные знаки ещё до выполнения кода. Для русских изменений писать script file через .NET UTF8Encoding(false) и запускать файл; источники читать с явным encoding=utf-8. Общий check-encoding дополнен в этой проверке поиском повторяющихся вопросительных знаков в изменённых NS00 документах.
