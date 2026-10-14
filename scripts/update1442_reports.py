from pathlib import Path
p=Path('reports/retailcase/2026-10-13/64-ni051-quality-loading-link.md');p.write_text('''# NI05.1 — контроль → назначенный рейс

14 октября 2026, W1437–1441. Результат существующего QC status дополнен текущим назначением СТ в той же READ ONLY транзакции после существующей проверки доступа к идентификатору. Read helper проверяет transport_dispatch_view, читает максимум2 строки по PALLET_UID. Неоднозначность не выбирает случайный рейс. Никаких изменений назначения, QC или запаса.

В текущей карточке контроля показана ссылка на существующую погрузку назначенного рейса только после готового допуска (или при явно необязательном контроле). Во время pending/busy/повреждения ссылка скрыта; изменение идентификатора очищает её. Отсутствующее назначение объясняется оператору. Переход не подставляет физические сканы и не разрешает выезд.

Файлы: outgoing_quality.py, новый infrastructure/quality_transport_read.py; outgoing-quality.js, новый outgoing-quality-next.js, warehouse-tasks.html. Команды проведения и права не расширены.

scripts/browser1440_quality_next.mjs: реальный CASE1131 → shipment641501/рейс33635, HTTP200. Состояния перехода ready/not-ready/unassigned моделировались поверх native ответа, ссылка33571 открыла реальный GET погрузки200. POST0/errors0. Screenshot112 обозначен synthetic для состояния допуска; реальный готовый допуск этой проверкой не заявлен.

SQLfhng97saw5tn6:4.174мс/2,14buffers. Решение: точечный ограниченный запрос оставить, нового индекса не требуется. Общий gate после NI05.2/NI05.1 и финальных backend NI06.2:755files/0cycles/73debt,24tests,обеTypeScriptPASS. EncodingPASS.
''',encoding='utf-8')
p=Path('reports/retailcase/2026-10-13/63-ni052-loading-recovery.md');p.open('a',encoding='utf-8').write('\nОбщая интеграция с NI05.1/NI06.2: gate755/0/73,24tests,обеTypeScriptPASS; encodingPASS.\n')
p=Path('wiki/components/retailcase_ni051_control_label_20261012.md');p.open('a',encoding='utf-8').write('\n## Контроль → существующая погрузка, 14.10\n\n[Report64](../../reports/retailcase/2026-10-13/64-ni051-quality-loading-link.md): текущий QC snapshot содержит назначение СТ при transport_dispatch_view; bounded2/неоднозначность не угадывается. При готовом допуске UI открывает существующий рейс. CASE1131→33635 read200, SQL4.174мс; UI states modeled,0POST. Новых назначений/допусков нет. Gate755/0/73,24tests/обаTS/encodingPASS.\n')
p=Path('wiki/index.md');p.write_text('- [Контроль → назначенный рейс](components/retailcase_ni051_control_label_20261012.md): report64, same-snapshot assignment, SQL4мс. [Возврат → точное размещение](components/retailcase_ni062_receipt_recovery_20261014.md): ведомый сдал, фильтр до limit100; gate755/0/73, encodingPASS.\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
p=Path('wiki/log.md');p.open('a',encoding='utf-8').write('\n- 2026-10-14: W1437–1441 QC→назначение рейса, report64, SQL4мс. NI06.2 сдан ведомым: exact receipt фильтр/возврат→размещение/recovery. Интеграция gate755/0/73,24tests/обаTS/encodingPASS. Далее конечное сопоставление критериев, без повторного движка.\n')
