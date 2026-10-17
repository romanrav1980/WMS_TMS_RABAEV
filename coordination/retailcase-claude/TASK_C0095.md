# C0095 — отдельное приложение магазина (прямое поручение владельца)

Приоритет после короткого завершения текущей приёмки C0094. Владелец15.10 однозначно требует ПРИЛОЖЕНИЕ магазина, а не роль/ссылку в админке. Приёмка по стратегии: вес, пересчёт по бумаге, сканирование как у комплектовщика. Это расширение AK06/KH06, существующая очередь остальных спринтов сохраняется.

## Владение файлами

Claude: terminal/wms_terminal_web/src/features/store-receiving/** (публичный index.tsx), docs/help/authoring/**, proposals/C0095/** и reports/retailcase/2026-10-15/claude/C0095/**. Codex: отдельный entry /store/, manifest/service-worker, Vite multi-entry, build/run, Oracle/backend/auth/стратегии/интеграция. Не менять root App/main/vite/public или native без передачи. Текущие workspaces/help locks сохраняются.

## Результат

Самостоятельный мобильный PWA интерфейс с собственным названием/иконкой, входом приёмщика, своими магазинами/поставками, без оболочки WMS admin. Вход только явные credentials в памяти; пароль не хранить и не брать admin из env/родителя. Один магазин выбирается сам, несколько — явно. Серверная пагинация списка поставок; не просить у обычного приёмщика ID рейса/погрузки. Поставка → грузовое место → ожидаемый состав → проверка по настроенной стратегии → расхождения → подтверждение → квитанция. Крупные поля/сканирование клавиатурным сканером, камера только при реальной поддержке, без фиктивного успеха.

Три режима из сервера: BARCODE (сканирование), WEIGHT_PHOTO (вес с существующими доказательствами), PAPER_COUNT (фактическое количество каждой строки + реквизит бумажного документа). Клиент не переключает утверждённую стратегию произвольно. Для маркированного товара действующие native условия не обходятся бумажным режимом; показывать блокировку/следующий шаг. Root уточняет native контракт, не имитировать успешную приёмку.

Сохранить exact operation_id/body ДО отправки в локальный журнал с API/actor/store/load scope, запрет новой команды при неизвестном результате, явный повтор прежней. Чужая учётка не видит старую форму/данные, logout очищает пароль. Offline — черновик/ожидание, не факт приёмки. На401/403 скрыть данные и прекратить отправки. Каждый control/button имеет tooltip/help_id и локальную статью; help доступен внутри приложения. Повторно использовать принципы существующих delivery/useStoreReceipt и receiptIntentValidation, серверный writer остаётся прежним.

## Объявленный backend контракт (root реализует; до READY показывать источник недоступен)

GET /api/store-app/session → {username,display_name,access_revision,stores:[{store_id,address,receipt_mode,policy_version}],limit:200,has_more,auth_scope:"STORE_RECEIPT"}. store_id — стабильный SHA256 адреса, не клиентский произвольный ID. Собственные логин/пароль HTTPBasic.
GET /api/store-app/deliveries?store_id=HASH&after=CURSOR&limit=50 → {store_id,items:[{load_operation_id,trip_id,root_key,gross_weight_kg,departed_at,receipt_operation_id,receipt_state}],next_after,limit}. Только frozen single destination/DEPARTED, события старого времени безпояса подписывать.
GET /api/store-app/deliveries/{load_operation_id}?store_id=HASH → существующий native StorePreview (см. admin/features/delivery/contracts.ts), плюс политика/разгрузка. Не разбирать путь самих физически вложенных единиц произвольными запросами.
POST /api/delivery/store-receipts/confirm — прежний контракт, PAPER_COUNT дополнительно paper_reference:string; количество/расхождения observations по lot_uid в точных decimal строках, существующие ограничения/снимок/подпись обязательны. POST unloading/start и evidence/scales — текущие API владельцев, отдельные квитанции. Новый writer/универсальный endpoint не добавлять.
Квитанция store receipt будет root READY отдельно. НЕ трактовать404/NOT_VISIBLE как rollback.

## Проверки

Сначала исполняемый UI с реальным auth/read contract, затем стратегии после READY. TypeScript; mobile390/сканер/клавиатура; чужой магазин403; lost-response сохраняетисходное тело; сменаactor; reloadoffline; тристратегии и расхождения; опубликованнаялокальнаясправка. Реальный stockeffect только по специально согласованной devfixture root, UIacceptance не отправляет произвольные живые приёмки.

Отчёт RESULT/RELEASE и реальные ограничения в CLAUDE_TO_CODEX. Не завершаться после плана/макета: реализовать компоненты, затем читать READY и продолжать совместную очередь.
