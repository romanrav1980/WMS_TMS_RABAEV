# 52 — NI04.2: архив показаний весов в сборке

14.10.2026, RABAEV/orcl, локальный API. Владелец реализации: Codex.

Терминал использует существующий архив весового поста. Добавлены обновление без сброса сканов, поиск по точному ID вне последних 50, подробности устройства/времени/калибровки/версии состава. Использованные показания и другая версия/строка/база веса недоступны для выбора. Точное чтение возвращает capture_purpose и used_operation_id в той же read-only транзакции с действующей проверкой доступа. Нового проведения и DDL нет.

Файлы: case-scale-archive.js, case-weighted-box.js, case-pick-tsd.html, case-pick-guide.css; inventory/infrastructure/warehouse_scales.py.

Реальный браузерный сценарий scripts/browser1373_scale_archive.mjs: CASE1077/line1081, архив FDBB07B26B039B418D9B17C6E20117B65F6DA464BFAA08F2B0B32808D7139A77. API200, used_operation_id=CASE.WEIGHT182:1077, выбранное показание пустое. Обновление сохранило KEEP.SCAN.1373; ошибок JS0, POST0. Данные показания TEST; это не испытание физических весов и не новый весовой отбор.

Скриншот: screenshots/97-ni042-scale-archive.png. Результат: tmp/result1373.json. После добавления сведений использованного пакета сценарий повторён успешно.

SQL: scripts/read1374_scale_sql.py, V$SQL 5p5hhg5qa13bw — 6.428мс, 161 buffer gets/2 исполнения; 5q7nmkjubujfk — 4.928мс,16/2. Решение: оставить точечные чтения по capture key; новый индекс не нужен. Список ограничен 50, локальные точные находки100.

Quality gate PASS: architecture740/0cycles/74debt,24tests, оба TypeScript. Encoding PASS. Проверка авторская; NI04.2 целиком и промышленная аппаратная приёмка этим не закрываются.