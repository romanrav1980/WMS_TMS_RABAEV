# C0116 — READY_FOR_UI_CONTRACT_IMPLEMENTATION

16.10.2026, новое поручение владельца: вес пока вводит пользователь; существующий
электронный API сохранить. Единственный UI пакет можно выполнять сейчас, без
ожидания hardware SHIPPING_GROSS. Это готовность перечисленных контрактов,
не закрытие всех спринтов или production acceptance.

## Пакет и владельцы

Claude: существующий UI магазина, погрузки/консолидации и связанный обзор старшего
смены; tooltip/help каждой изменённой кнопки; мобильная навигация. Codex:
backend/Oracle и оставшаяся бизнес-приёмка. Backend/DB Claude не редактирует.
Один ACK C0116 с файлами, затем реализация без ожидания новых запросов.

## 1. Вес магазина — новый контракт установлен

POST `/api/delivery/store-receipts/confirm`: прежнее тело ReceiptBody плюс
`manual_weight_kg: "10.000"` (строка, положительный GROSS KG). Это источник
MANUAL_CONFIRMED; не отправлять одновременно scale_capture_key. По умолчанию
показывать «Ввести вес», отдельно «Электронные весы» с прежним ScaleConnection.
Без ручного поля старое canonical body не меняется. Не посылать null/пустую строку.
Стратегия магазина остаётся WEIGHT_PHOTO; фото/акт/сканы/разгрузка сохраняются.
Источник, значение и остальные поля входят в неизменяемый pending draft.
После отправки запрещать редактирование до установления исхода. Переключение
источника очищает прежний выбор только у ещё не отправленного черновика.

Ответ weight для manual: capture_key/device_id/device_policy_version=null,
measurement_origin=MANUAL_CONFIRMED, recorded_by=оператор; shipping_gross_kg,
observed_gross_kg,tolerance_kg,delta_kg — строки; in_tolerance/act_confirmed —0/1;
photos — прежний массив. Старый SCALE_CAPTURE ответ остаётся прежним.
Показывать «Введено пользователем», не «Получено от прибора».

Backend: `app/modules/delivery/api/store_receipt_routes.py`. Native migration
2026-10-16_manual_store_weight APPLIED,6SHA/INVALID0. Проверены native calculation
на реальном историческом QA load/photos, API wire и guards. Новая полная приёмка
с сохранением ручного веса ещё не проверена — это задача Codex, не сигнал к DDL
или live quantity POST силами Claude. Не называть этот gate пройденным.

UI старт: terminal/.../features/delivery/{contracts.ts,receiptIntentValidation.ts,
receiptDraft.ts,receiptResult.ts,components/WeightEvidencePanel.tsx,ScaleConnection.tsx}.
Найди реальных callers onEvidence и обнови их последовательно. Не создавай второе приложение.

## 2. Ручной вес погрузки — существующий контракт

POST `/api/transport/loading/confirm` и прежние confirm-single/reconciliation:
measurements={origin:"MANUAL_CONFIRMED",content_version:<current>,gross_weight_kg:
"10",width_m:"1.2",depth_m:"0.8",height_m:"1.5"}. Остальные поля и guards не меняются.
Размеры вводятся отдельно; вес не разрешает QC/перегруз/неверную машину.
Прочитай фактические loading_routes.py и существующий UI, используй прежний flow.
Никакой зависимости от неустановленного SHIPPING_GROSS_READ. ASM hardware API
сохранён; новый ручной протокол incremental ASM не выдумывать.

## 3. Ожидаемый состав — installed native/API

GET `/api/consolidation-plans?warehouse_id=20220394&status=ACTIVE&limit=30`.
status ACTIVE(default)/CANCELLED/ALL; limit1..50; after=next_after следующей страницы.
Ответ {warehouse_id,items,has_more,next_after,stock_changed:false}. items:
plan_id,version,status,root_identifier,warehouse_id,cell,expected_count,updated_at UTC.
При смене склада сбросить cursor и старые данные;401/403/404 очистить закрытое.
Нет total; returned limit не означает полный итог склада.

GET `/api/consolidation-plans/{plan_id}` возвращает план+members+readiness.
readiness: ready,location_ready,expected_count,missing_count,extra_count,
changed_count,unknown_leaf_count,members[].state. ready=true — «Состав полон»,
не «Можно отгружать». Planned root может ещё физически не существовать.
IN_ROOT=в составе; NOT_PICKED=не собрана; MISSING=отсутствует;
SHIPMENT_CHANGED/REQUEST_CHANGED/BINDING_CHANGED=изменение требует проверки.

PUT `/{plan_id}`: {operation_id,expected_version,reason,root_identifier,warehouse_id,
cell,fulfillment_ids:[191,192]}. До200 уникальных положительных fulfilment IDs.
POST `/{plan_id}/cancel`: {operation_id,expected_version,reason}.
ACK {operation_id,plan_id,version,status,stock_changed:false}; точный replay возвращает
исходный ACK.409 — конфликт тела/версии/состояния;503 uncertain — прежнее тело+ID.
403 — текущий доступ закрыт. Отмена сохраняет историю, не разбирает физическое дерево.

Выбор сборок: существующие GET /api/customer-orders?order_no=...&limit=... и
GET /api/customer-orders/{id}/fulfillment, их реальные DTO и права. Показывать
заказ/СТ/идентификатор, не заставлять оператора угадывать технические IDs. Нет
права читать заказ — явное объяснение, без обхода. Не менять native scope в UI.
Интегрировать с существующим HuTreeDesk/HuTreeWorkspace и выбранным складом
старшего смены. План и физическое дерево показывать раздельно, в общем стиле twin.

Список/cursor live PASS; scope helper прежний. Не заявлять полную отдельную
матрицу scoped pagination доказанной. Native physical/temperature/QC owners сохраняются.

## Справка и визуальная проверка

Обычные URL уже работают на API origin:
`/help/manual-weight.html#enter`, #confirm/#store/#integrated/#retry;
`/help/consolidation-plan.html#save`, #refresh/#cancel/#conflict.
Не делать ARTICLE_SAVE/PUBLISH, новую БД или новый help framework. Из другого
frontend origin строй URL через существующий API base. Ссылка открывается без
потери рабочего черновика. Tooltip объясняет действие/зачем; data-help-id стабильный.
Не открывать произвольный wiki, конфиги, reports и секреты.

390px и desktop: вес/статус/действие видны; длинные UID/даты не раздвигают экран;
timezone одним компактным пояснением, не повторять на каждой карточке.
Сохранять существующий общий Гант CASE_PICKER/REACHTRUCK/DOCK/VEHICLE; недостающие
aware интервалы не рисовать выдуманными. Его готовый контракт — RESOURCE_TIMELINE_API_V1.md.

## Работа и сдача

Разрешены frontend features delivery/inventory/platform workspaces, необходимые
callers/exports/styles и адресные UI tests. docs/help/public можно править как
обычный текст, без API публикации. Backend/SQL/общие правила/права не менять.
Один affected typecheck/build после законченного пакета, адресная проверка draft
replay/source switch/stale warehouse; screenshots390px+desktop. UI mocks явно
назвать UI fixtures, не native/hardware acceptance. Живых credentials для товарных
POST не передаём; безопасные реальные backend проверки выполняет Codex.
Результат: RESULT_C0116.md + RELEASE в CLAUDE_TO_CODEX, файлы/проверки/ограничения.
GitHub/commit/push и платные дополнительные агенты не запускать.

Короткие evidence (читать только нужные):
reports/retailcase/2026-10-16/manual-weight/{functional.json,http-read.json,root-readback.json};
reports/retailcase/2026-10-16/consolidation-manifest/acceptance.json.
Новые backend исходники зафиксированы соответствующими frozen manifests; не
воспроизводить старые fixture/cleanup scripts. Весь исторический журнал не читать.
