# Самостоятельное приложение магазина

Реализовано локально 15.10.2026. Открыть: http://127.0.0.1:8088/store/ . Production entry отделён от WMS shell; установка PWA использует собственные manifest/service-worker/scope. Для доступа с телефона нужен доступный HTTPS-адрес; физическая установка пока не проверена.

- Собственный вход, действующие назначения STORE, выбор магазина, постраничный список финальных поставок и исходный акт принятого места. Admin-login/legacy warehouse grant не требуются.
- BARCODE: идентификатор места и обязательные маркированные единицы/агрегаты. WEIGHT_PHOTO: архивированное измерение шлюза и три стороны. PAPER_COUNT: реквизит документа и фактический ввод каждой строки, без подстановки плана в факт. Регуляторный контроль не обходится ни одной стратегией.
- Команда сохраняется перед отправкой; после потери ответа/reload повторяется неизменное тело и operation_id. NOT_VISIBLE не означает отмены. Повреждённая запись блокирует новую команду. Пароль не сохраняется; выход убирает данные из памяти.
- Подсказки действий и шесть опубликованных статей штатной базы знаний. Источник: wiki/runbooks/retailcase_store_receiving_app.md; offline snapshot генерируется scripts/store_help_bundle.py, не ведётся параллельно вручную.

## Доказательства

| Проверка | Результат | Артефакт |
|---|---|---|
| Native/API/Oracle + production mobile | 11 PASS, временный actor/role очищены; пробная приёмка rollback подтверждён отсутствием fact и operation | scope-native.json, ui-native.json |
| Переработанный UX: компактный список, QR-фото ZXing, deep link/reload/exact retry, бумажный факт, запрос весов/три фото, новый запрос после отказа, повреждённая выгрузка, восстановленные марки | 8 PASS на production, writes перехвачены браузером | ux-ui.json |
| Production PWA и offline shell | PASS, отдельный scope; private API не кешируется, чужой кеш сохранён; installabilityErrors=[] | pwa.json |
| Native SQL-пакеты | 6 точных совпадений финальных версий, INVALID=0, constraint трёх режимов ENABLED | oracle-verification.json |
| PAPER_COUNT exact replay | 4 PASS, два повтора исходной квитанции, изменённый документ конфликтует, новых приёмок нет | paper-native.json |
| Wiki → опубликованные статьи | 6 allowlisted опубликованных инструкций, включая шлюз; связанные статьи доступны store-only учётке | help-publication.json |
| Производительность | session178/30мс, deliveries74/35мс, preview142/35мс; recent slow log пуст | slow-sql.json |

Полный offline gate: 943 файла/0 циклов/72 прежних пункта долга, 24 architecture/tooling tests и оба TypeScript PASS. Production build PASS; предупреждение >500k относится к существующему terminal chunk и store chunk518k (139k gzip): распознавание включено в offline shell. Encoding check PASS. Проверки автора являются интеграционным evidence, а не независимым пилотом.

## Границы и сохранённая история

Во время ранней native проверки метод RRL_STOCK_NATIVE_API.post оказался владельцем COMMIT. Одна DEV PAPER_COUNT приёмка сохранилась: PAPER.ROLLBACK:41005408317040d0b433353978c38d9a:2, load THERMAL1168.LOAD:f8e5e3b899. Она не удалялась/не переписывалась; policy восстановлена, exact replay проверен. Последующий положительный scoped тест использует prepare/execute_prepared и подтверждённый caller-owned rollback. Детали и версии: wiki/database/retailcase_store_app_strategies_20261015.md.

Код/UI: terminal/wms_terminal_web/src/features/delivery, src/store-main.tsx. Сервер: app/modules/delivery/api/store_app_routes.py, infrastructure/store_app_reads.py и существующий StoreReceipt/native writer. Сборка: npm.cmd --prefix terminal/wms_terminal_web run build; сервер: корневой serv.bat. Разработка: корневой terminal.bat, /store/.

C0095 и C0106 Claude остановились лимитом провайдера; Codex закончил текущую интеграцию с внутренними агентами и проверку. GitHub не обновлялся. Физические весы/сканер/камера, установка на реальный телефон и независимый пилот магазина отдельно. Остальные незакрытые блоки восьми спринтов остаются в living plan; приложением они не подменены.

## Общий шлюз склада и магазина

Принято [описание OPC 40200 v2 → шлюз → HTTPS API](../../../../docs/integrations/weighing-gateway-opc40200.md). Магазинный request API применён: 11 native rollback, 6 live HTTP, 15 boundary tests; шлюз/outbox — 49 focused tests. Это не испытание физического OPC устройства. Реальный OPC клиент, аппаратная lease, архив исходных DataValue и складской adapter/SHIPPING_GROSS остаются отдельными реализациями.
