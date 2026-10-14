# NI04.3: локальная отмена исходной агрегации
Дата: 12.10.2026. Native migration: [450](../../db/migrations/2026-10-12_ni043_aggregation_lifecycle/apply.sql), актуальные правки454/456/457/463. Owner: inventory, единственный writer остатков прежний RRL_STOCK_POSTING_API. Локальная отмена — metadata-транзакция с CONFIG X; журнал пишет существующий RRL_REGULATORY_API. Государственная квитанция не создаётся.

Команда RRL_TRACE_AGG_LIFECYCLE.invalidate принимает идентификатор операции, склад, исходную паллету, систему/профиль, SHA256 кода, причину OPENED/REPACKED/DAMAGED/COMPOSITION_CHANGED и документ. Право trace_manifest_import, актуальная привязка пользователя к складу. Требуется точный применённый оригинал: SAP receipt/order-line или использованный sender manifest. Отменять можно код исходного состава, даже если при рождении сканировали только его родителя. Все физические единицы именно этой агрегации должны находиться на указанном складе, быть AVAILABLE без hard reservation. Наличие другой единицы того же origin на складе не даёт права отменять чужую коробку.

Неизменяемые RRL_TRACE_AGG_INVALIDATION и RRL_TRACE_AGG_BLOCK сохраняют причину, автора, журнал и affected codes. Непосредственный код и все точные родительские узлы исходного sender graph блокируются совместно. Для плоского SAP состава BOX блокирует PALLET того же профиля, если PALLET содержит все единицы BOX. Соседние коробки не блокируются. Родительская отмена сама по себе не отменяет закрытые дочерние коробки. Лимиты: до1000 affected aggregates, до10000 физических единиц. Повтор с тем же actor/request возвращает исходный результат; другое содержимое отклоняется. Уникальность и CONFIG X сериализуют конкуренцию. Восстановления старого кода нет: новая упаковка требует нового подтверждённого состава и отдельного regulatory lifecycle.

RRL_IW_AGG_SCAN вызывает единый assert_scan и сохраняет прежние проверки qty/profile/version/issued fingerprints. Дополнительно текущий UID каждой исходной единицы должен совпадать с origin: оригинальный код не разрешается автоматически для товара, переложенного в новый товарный паллет/CASE/возвратный UID. Перемещение целой исходной паллеты допускается. Это не доказывает неприкосновенность пломбы; операционная фиксация вскрытия обязательна.

HTTP:
- POST /api/inventory/trace-manifests/aggregations/invalidate — typed strict request, durable original operation ID.
- GET /api/inventory/trace-manifests/warehouses/{ware}/pallets/{origin}/aggregations — warehouse-scoped READ ONLY, до1000 оригинальных/scanned codes. REGISTERED_EVIDENCE не означает разрешённый скан или государственное подтверждение.
- В существующей странице pallet-composition добавлена панель жизненного цикла. Отправка требует права, причины и документа; неопределённый результат сохраняет точный payload в localStorage на actor/API и даёт повторить его. Отдельная отмена не меняет остаток и коды единиц.

Авторские доказательства:
-452: native полная отмена/повтор/content conflict/late rollback; P3H0, event1,6codes неизменны.
-459: unscanned CRPT.BOX1 в sender124 блокирует только BOX1 и её PALLET, BOX2 остаётся доступна относительно этого правила; rollback возвращает0facts/P3.
-462: реальные конкурентные HTTP200/200 одного operation ID, одна отмена/одинjournal/2blocks; повтор/conflict/custody отказ; P3H0/event1/6codes/protected20H20 сохранены. Сохранён tmp/context462.json. BOX1 и PALLET sender124 теперь намеренно отменены; не повторять исходный сценарий459.
-464/465: свежий SAP ARTMAS/supply, birth3/6codes, исходные сканы2, native приёмка3/6/late rollback; первый HTTP после recompilation вернул непроверенный503, точный повтор того же ID успешно проведён один раз. tmp/context464.json — принятая паллета в карантинной ячейке. Не повторять source464/case464 initial.
- Live Oracle: USER_ERRORS/INVALID empty. Architecture647/0cycles/76debt PASS. JS node--check PASS. Браузерное и независимое Qwen ревью не выполнено.

Ограничения: нет реального ACK государственных систем/сертификатов/сканера; автоматическая юридическая переагрегация и новый государственный код не заявлены. Partial/group aggregate-only receiving остаётся отдельным инкрементом. Отмена локально блокирует межскладской aggregate scan; прочие сканирующие потоки должны подключать этот же контракт, а не отдельную копию правила.

SQL466/468/469: old ancestor query22.575ms/225buffers; changed to one exact manifest graph per query, new cold39.16ms/170buffers (not a throughput improvement claim). UID-use/block-op indices added. Decision inventory: preserve 1000/10000 bounds; large-graph edge materialisation/batch only when measured fanout requires it. API470/then504 current.
