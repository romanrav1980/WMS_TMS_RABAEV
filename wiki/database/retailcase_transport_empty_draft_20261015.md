# Машина с нормативами тары на пустом черновике · 15.10.2026

AK05-DRAFT01. Миграция `2026-10-15-transport-empty-draft-floor`, APPLIED. [Apply](../../db/migrations/2026-10-15_transport_empty_draft_floor/apply.sql), [rollback](../../db/migrations/2026-10-15_transport_empty_draft_floor/rollback.sql), [verify](../../db/migrations/2026-10-15_transport_empty_draft_floor/verify.sql), точный before-body и checkpoint рядом. Владелец данных transport; authoritative implementation PL/SQL `RRL_TRANSPORT_PLAN_RULES.check_vehicle`, транзакция остаётся у вызывающего `RRL_TRANSPORT_EDIT_API`/gateway.

## Причина и изменение

Назначение машины с `floor_capacity` на собственный пустой черновик передавало `[]` в `prepared_floor_counts`, который правильно ограничивает непустой груз диапазоном 1–200 СТ. Следующий `RRL_STOCK_LOAD_FLOOR.planning_counts` также требует непустой источник. Это проверка состава груза, которого в пустом черновике ещё нет, а не отсутствие нормативов машины.

Исправление пропускает эти два расчёта только при точном пустом массиве СТ и `p_complete=0`. Нулевые типовые количества и `unknown_places=0` по-прежнему проходят штатную проверку нормативного профиля машины. Не меняются состояние профиля/активность/вместимость машины, actual loaded proof, frozen trip, области/владелец пустого черновика, типы и лимиты непустого состава, неизвестная тара, подъезд и завершённая проверка. `p_complete=1` с пустым составом по-прежнему не становится готовым рейсом. Физический допуск к погрузке не выдаётся.

## Проверки

Перед подготовкой source из live `USER_SOURCE` побайтно после нормализации SQL-префикса совпал с предыдущей scoped-миграцией; цель `RABAEV/orcl`, INVALID0. Скрипт [transport_empty_draft_smoke.py](../../scripts/transport_empty_draft_smoke.py) воспроизвёл прежний `PLAN_TARE_ST_BOUND_200` на настоящем READY профиле машины, создавая собственный черновик в caller-owned транзакции и откатывая его в `finally`. Sequence ID может быть потреблён; бизнес-commit отсутствует.

После согласованного apply скрипт проверяет успешное назначение, сохранение запрета пустого complete, лимита 200, ошибку числовой/пустой СТ, отсутствие доказательства для неизвестной тары и исчезновение тестового заголовка после rollback. До фактического apply результат не объявляется PASS. Исходный helper и downstream loaded-floor пакет не модифицированы. Нагрузочная и независимая приёмка этим не заменяются.

[[retailcase_transport_scoped_edit_20261015]], [[roadmap/retailcase_access_knowledge_plan]].

## Применение и native результат

Root применил версионный apply штатным stop-on-error runner: 3 statements, 0 errors. После применения live source полностью совпал с подготовленным body, `USER_ERRORS=0`, глобально `INVALID=0`, migration ledger `APPLIED`. Checkpoint содержит SHA256 и результаты. Rollback подготовлен; не исполнялся.

Семь native проверок прошли: собственный пустой черновик принимает машину с READY floor profile; пустой complete отвергается; 201 СТ, числовая и пустая СТ отвергаются прежними ошибками; неизвестный тип остаётся `TARE_TYPE_UNCONFIRMED`; тестовый заголовок после rollback отсутствует. Девять прежних native scoped-edit проверок также PASS: READ ONLY preflight, чужая область/смешанный состав/отзыв, автор пустого черновика. [Новый сценарий](../../reports/retailcase/2026-10-15/dispatch-scope/empty-draft.json), [регрессия](../../reports/retailcase/2026-10-15/dispatch-scope/native-edit.json), [source/ledger/slow SQL](../../reports/retailcase/2026-10-15/dispatch-scope/empty-draft-verification.json).

Бизнес-commit тестов отсутствует; транзакционные заголовки и назначения откатились, физическое движение не выполнялось. Sequence ID потреблены, что нормально при rollback. Offline architecture PASS: 926 файлов, 0 циклов, 72 прежних долга; UTF-8 проверка PASS.

После функционального прогона `RRL_SQL_SLOW_LOG` за час пуст. Bounded поиск в `V$SQL` по двум именованным грузовым запросам не вернул записей: это отсутствие доступного плана/метрик для этих запросов, не нулевая стоимость SQL. Native вызовы не создавали HTTP API audit. Решение transport/Codex: сохранить прежние ограничения 200 источников/5000 мест, новые индексы не добавлять; повторно атрибутировать и смотреть план при устойчивом интерактивном запросе свыше 1000мс. AK05-DRAFT01 закрыт по native коду; независимый пилот всего AK05 отдельно.
