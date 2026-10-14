# Документы сверки и пакетные SQL — 14.10.2026

NI07.2, finance owner. [Отчёт56](../../reports/retailcase/2026-10-13/56-ni072-documents-and-query-batching.md), [скриншот101](../../reports/retailcase/2026-10-13/screenshots/101-ni072-backlog-documents.png).

Существующий day-reconciliation теперь отдаёт current_backlog_documents: до20 ID на каждый из16 видов, точный count, has_more и scope CURRENT_BACKLOG. Исходные условия сохранены; daily и backlog исполняются двумя пакетами вместо32 roundtrips в прежнем read-only snapshot. COUNT OVER требует подсчёта всей подходящей совокупности; ограничение20 не выдаётся за ограничение работы Oracle.

V$SQL средние38–62мс на текущем dev-наборе. Решение: без нового индекса; при >500мс — план конкретной ветви, владелец finance. СТ имеют отдельный применённый индекс и ещё открытый широкий исторический запрос: [[database/retailcase_ni022_st_page_keys_20261014]].

Ссылки task_id, строковый case_id и expense operation_id ведут в существующие документы. Производные ERP/stock/regulatory показатели пока без ID. Interwarehouse/supplier-handover/logistics-costs теперь принимают warehouse_id; четыре return-страницы умели это раньше. External-outbox и tare-селекторы не объявлены готовыми.

Admin session при abort/503 сохранена, но права до успешной серверной проверки недоступны; 401/403 очищают. Реальные браузерные сценарии1390/1394 read-only,1392 равенство счётчиков,1395SQL. Gate PASS746/0cycles/73debt. Не независимая/внешняя приёмка, нагрузка и реальное усечение >20 отдельно не проверены.
## Продолжение1400–1403: внешние сообщения
[Отчёт58](../../reports/retailcase/2026-10-13/58-ni072-external-document-links.md): ERP/регуляторные производные показатели теперь также имеют до20ID с теми же source predicates. EVENT_OUTBOX ведёт напрямую в существующее досье, без чтения всей очереди; ERP ID пока текстом. Actual38542432:8ERP+4регуляторных,4459HTTP200/POST0. SQL8–22мс/noDDL. Положительные неподтверждённые stock-source и>20sample не демонстрировались. Предыдущее ограничение «ERP/regulatory без ID» выше устранено; stock-конфликты безID сохраняются. ACK внешних систем всё ещё не утверждён.
