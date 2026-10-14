# Промпт для Codex: исправление данных и API для live-режима 3D-двойника

Дата: 14 октября 2026 года. Основание: сверка live-адаптера двойника с API ТМС — [[subprojects/wms_twin_3d]] (раздел «Live-сопоставление»), принципы — [[concepts/warehouse_transport_digital_twin_principles]].

Скопируйте блок ниже в Codex целиком.

---

```text
Ты работаешь в репозитории C:\projects\TMS (WMS/TMS: Oracle 11g-совместимая схема RABAEV,
FastAPI в api/wms_api_server, React admin, параллельно работает legacy C# WinForms).

## Обязательный онбординг (до любых изменений)

1. Прочитай AGENTS.md, wiki/index.md, wiki/architecture/retailcase_modular_development_contract.md,
   config/architecture/retailcase-policy.json, wiki/database/oracle_change_protocol.md.
2. Прочитай wiki/subprojects/wms_twin_3d.md (раздел «Live-сопоставление» и «Находки по данным»)
   и код двойника twin/wms_twin_3d/src/adapters/tmsMapping.ts, tmsLive.ts.
3. Правила, которые нельзя нарушать:
   - Не менять Oracle-объекты, от которых зависит C# WinForms, несовместимым образом.
     Новые колонки — только nullable/аддитивно; новые объекты — отдельной миграцией.
   - Мутации транспортного домена — только через существующие Oracle-пакеты; прямой INSERT/UPDATE
     в бизнес-таблицы из Python запрещён. Исправление тестовых данных — миграцией с verify/rollback.
   - Каждая миграция: db/migrations/YYYY-MM-DD_<name>/ с apply.sql, rollback.sql, verify.sql,
     стабильным MIGRATION_ID, зеркалом в wiki/database/; применять tools/oracle_apply (UTF-8).
   - Новые backend-сценарии — в app/modules/<area>/{api,application,domain,infrastructure}
     с public.py/contracts.py; не раздувать transport_service.py (лимиты 600 строк файла, 100 строк функции).
   - Существующие контракты API сохраняются: новые поля/параметры только аддитивно, значения
     по умолчанию дают прежнее поведение.
   - После каждого значимого кейса — анализ долгих SQL (RRL_SQL_SLOW_LOG, /api/admin/slow-sql)
     с явным решением. Перед сдачей: python scripts/retailcase_quality_gate.py и
     scripts/check-encoding.ps1. GitHub не публиковать.
   - Двойник (twin/wms_twin_3d) остаётся read-only: он не вызывает мутирующие API.

## Наблюдения (проверено на живом API 127.0.0.1:8088, 14.10.2026)

A. Брони ворот в live нет. RRL_TRANSPORT_TASK.DOCK заполнен кодами тестовых фикстур
   (QD…, QO… — их создают скрипты вида scripts/case565_depart_profile.py через
   insert into RRL_TT_DOCK(DOCK, WARE_ID, …)). DOCK — ключ RRL_TT_DOCK(DOCK VARCHAR2(15), WARE_ID, ORD),
   а ворота 3D-топологии — RRL_TOPOLOGY_GATE(TOPOLOGY_ID, WARE_ID, GATE_CODE G01…, GATE_KIND
   RECEIVING|SHIPPING|BOTH). Связи «док ↔ ворота топологии» в схеме нет, поэтому двойник
   сравнивает DOCK с GATE_CODE и не находит ни одного совпадения (117 из 120 рейсов с DOCK).
B. Машин на дворе в live нет. RRL_TRANSPORT_TASK.CONDITION принимает только «Спланирован»/«Отгружен»
   (+ один мусорный '"1#F#B#0#D#8$0#E#2#0#D'); подъезд, постановка под док, погрузка, выезд
   в таблице не хранятся. Факты есть в RRL_TT_OPERATIONS (план/факт операций рейса), GPS
   (/api/admin/transport/vehicles/positions, /geofences), складских заданиях (/api/warehouse-tasks).
C. У рейса нет склада. GET /api/admin/transport/tasks не возвращает WARE_ID; WARE_ID есть
   только у СТ (RRL_SBORKA_PALLETS), и 190 из 201 СТ не относятся к складу топологии (ware 1).
   При этом склад дока уже доступен: RRL_TT_DOCK.WARE_ID (так делает
   modules/inventory/infrastructure/interwarehouse_incoming.py).
D. Испорчено название зоны топологии 2 (LOAD-1500-2CH-60): RRL_TOPOLOGY_ZONE.ZONE_NAME хранится как строка из вопросительных знаков (4 + 6 символов)
   (порча кириллицы при записи фикстуры, CREATED_BY='codex-load'). Названия проходов и ворот корректны.
E. Медленный запрос: GET /api/admin/transport/available-sts?unassigned_only=false&page_size=200 — 28,6 с,
   свободные СТ (unassigned_only=true, page_size=300) — 6,8 с. Причина: routers/transport.py
   list_available_sts получает все строки из TransportService.list_available_sts и режет страницу в Python.
F. GET /api/admin/warehouse-topologies/2/map отдаёт 5,7 МБ, из них 15 000 строк distances,
   которые двойнику не нужны (1,4 с).
G. В twin/wms_twin_3d/src/adapters/tmsMapping.ts GATE_KIND 'BOTH' не распознаётся
   (показывается как отгрузка с замечанием «Неизвестный GATE_KIND»).

## Задачи

### 1. Связь «док ↔ ворота топологии» (A)
- Спроектируй аддитивную связь RRL_TT_DOCK.DOCK → RRL_TOPOLOGY_GATE (например, nullable колонка
  LEGACY_DOCK_CODE в RRL_TOPOLOGY_GATE с уникальностью в пределах TOPOLOGY_ID, или отдельная таблица
  соответствий с WARE_ID). Выбор обоснуй в wiki/database/ (проблема, решение, последствия).
- Не меняй тип/смысл RRL_TT_DOCK и RRL_TRANSPORT_TASK.DOCK — C# продолжает работать как раньше.
- Добавь в карту топологии (GET …/warehouse-topologies/{id}/map, gates[]) поле legacy_dock_code
  и в GET /api/admin/transport/tasks — поле DOCK_GATE_CODE (код ворот активной топологии склада дока
  или null). Старые поля не трогать.
- Для dev-фикстуры топологии 2 заведи соответствия для доков склада 1 миграцией с verify;
  тестовые доки QD…/QO… не переименовывай — для них DOCK_GATE_CODE остаётся null.
- Приёмка: для рейса с DOCK, связанным с G03, tasks возвращает DOCK_GATE_CODE='G03'; без связи — null;
  C#-зависимые запросы по RRL_TT_DOCK возвращают прежний результат.

### 2. Склад рейса (C)
- В GET /api/admin/transport/tasks добавь DOCK_WARE_ID (RRL_TT_DOCK.WARE_ID по DOCK) и
  ST_WARE_IDS (уникальные WARE_ID СТ рейса, строкой через запятую или массивом — согласуй
  с существующим стилем ответа), а также необязательный фильтр ware_id (рейс подходит, если
  DOCK_WARE_ID = ware_id или любая СТ рейса с этим WARE_ID). Без параметра — прежний результат.
- Проверь план запроса: фильтр не должен превращать список рейсов в полный перебор СТ.
- Приёмка: функциональный тест в tests/transport/ на рейс с доком склада 1 и СТ склада 3.

### 3. Состояние двора рейса (B) — только чтение
- Новый read-only эндпоинт (модуль transport, слой api/application/infrastructure), например
  GET /api/admin/transport/yard-state?ware_id=&date=, возвращающий по рейсам:
  trip_id, phase ∈ {planned, arriving, queued, docked, loading, departed, unknown}, gate_code,
  phase_since, source ∈ {operations, gps, warehouse_tasks}, evidence (какая операция/геозона/задание).
- Источники и приоритет: факт операций RRL_TT_OPERATIONS → вход/выход геозоны склада по GPS →
  складские задания погрузки. Нет фактов — phase='unknown', а не выдуманное значение.
- Никаких записей; ограниченная выборка по дате и складу; проверь долгие SQL.
- Мусорное значение CONDITION не исправляй молча: верни его как есть и отрази в отчёте
  (кто его записал — найди по API audit/журналам, если возможно).
- Приёмка: тест на рейс с фактической операцией постановки → phase='docked', gate_code заполнен.

### 4. Название зоны топологии 2 (D)
- Найди скрипт/миграцию, создавшую топологию LOAD-1500-2CH-60 (CREATED_BY='codex-load'),
  исправь в нём кодировку записи кириллицы (UTF-8, python-oracledb/NLS_LANG как в serv.bat).
- Исправь существующую строку миграцией с verify-запросом на маркеры порчи (вопросительные знаки вместо кириллицы, латинские буквы с диакритикой из двойного UTF-8, символ замены U+FFFD — используй те же маркеры, что scripts/check-encoding.ps1)
  по RRL_TOPOLOGY_ZONE/AISLE/GATE.ZONE_NAME/AISLE_NAME/GATE_NAME всех топологий; правильное
  название зоны восстанови по смыслу ZONE_KIND='PICKING' (например «Зона отбора») и зафиксируй
  это допущение в wiki.

### 5. Серверная пагинация available-sts (E)
- Перенеси page/page_size в SQL (Oracle 11g-совместимо: ROWNUM/ROW_NUMBER, без FETCH FIRST),
  сохраняя формат ответа (список) и порядок сортировки. Без page/page_size — прежнее поведение.
- Добавь необязательный заголовок/параметр с общим количеством только если это не ломает
  существующих клиентов (admin TransportDispatchPage.tsx).
- Цель: unassigned_only=false&page_size=200 < 2 с, свободные СТ page_size=300 < 1,5 с на dev-стенде.
  Замерь до/после, приложи планы и решение по индексам в wiki/database/.

### 6. Карта топологии без расстояний (F)
- Добавь параметр include_distances (по умолчанию true — прежнее поведение) в
  GET /api/admin/warehouse-topologies/{id}/map; при false не выполнять запрос distances и
  route_cells. Замерь размер и время ответа для topology 2.

### 7. Доработка двойника (A, C, F, G) — после задач 1, 2, 6
- tmsMapping.ts: ворота рейса брать из DOCK_GATE_CODE (fallback — прежнее сравнение DOCK с GATE_CODE);
  склад рейса — DOCK_WARE_ID; GATE_KIND 'BOTH' поддержать (ворота и приёмки, и отгрузки).
- tmsLive.ts: запрашивать карту с include_distances=false; фильтровать рейсы по ware_id топологии,
  если API поддерживает параметр.
- Если реализована задача 3 — использовать yard-state для фазы рейса и постановки у ворот
  (машины на сцене только при phase ∈ {arriving, queued, docked, loading}).
- Обнови таблицу «Live-сопоставление» и «Находки по данным» в wiki/subprojects/wms_twin_3d.md.
- Проверка: npm run typecheck и npm run build в twin/wms_twin_3d; открыть
  http://localhost:5181/?source=live и убедиться, что бронь ворот и склад рейса отображаются.

## Что сдать

- Миграции с apply/rollback/verify и зеркалом в wiki/database/; применены к dev Oracle, verify PASS.
- Функциональные тесты tests/transport/test_twin_live_*.py (реальный API + Oracle), включая
  отрицательные ветки (нет связи дока, нет фактов двора, чужой склад).
- Замеры долгих SQL до/после с решением по каждому запросу.
- Обновлённые wiki/index.md и запись в wiki/log.md.
- Отчёт: что сделано, что осталось, какие допущения приняты (особенно восстановленное название зоны
  и выбранная модель связи дока с воротами).
- python scripts/retailcase_quality_gate.py — PASS; scripts/check-encoding.ps1 — PASS.

## Вне рамок

- Изменение логики C# WinForms и смысла существующих статусов CONDITION.
- Запись чего-либо из двойника.
- Публикация в GitHub.
```
