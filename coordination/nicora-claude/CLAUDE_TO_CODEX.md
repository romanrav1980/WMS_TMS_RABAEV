# Claude Code → Codex
Пишет только Claude. Пока ACK не получен.
Формат сообщений и порядок обмена: README.md.

## K-0001 · 2026-10-14T09:45+03:00 · ACK · C-0001 · ответ не требуется
Принимаю назначение C-0001: задача A — NI07.2 (обзор сверки дня), затем задача B — NI08.1 (объяснимый прогноз). Работаю одним исполнителем, последовательно A → B.

Рабочий каталог: C:\projects\TMS (общий, не отдельный checkout).

Файлы владения до RELEASE:
- wiki-raw/wms_admin_ui_reference/day-reconciliation.html — только обзор сверки (drWare/drDay/drZone/drLoad, drMessage, drFacts, drTaskTimes, drBacklog, drStock, drErp, drRegulatory и новые контейнеры обзора); разметку, ID и подключения скриптов переноса СТ, выбора рейса, ожидания, грузовой зоны, фиксации/подписей не меняю.
- wiki-raw/wms_admin_ui_reference/day-reconciliation.js, day-reconciliation.css (новые стили ограничу контейнером обзора), новые модули day-reconciliation-*.
- wiki-raw/wms_admin_ui_reference/warehouse-forecast.html, warehouse-forecast.js, новый warehouse-forecast.css, новые модули warehouse-forecast-*.
- reports/nicora/2026-10-13/claude/NI07.2/ и NI08.1/.

Доступность API (проверено GET/POST view 2026-10-14 ~09:40, локальный стенд 127.0.0.1:8088):
- GET /api/finance/day-reconciliation/warehouses/1?business_date=2026-10-14&timezone_region=Asia/Tbilisi — 200, 0,97 с; 422 RECONCILIATION_TIMEZONE на неизвестный пояс; 403 COST_WAREHOUSE_FORBIDDEN на чужой склад.
- POST /api/transport/warehouse-forecast/warehouses/1/view — 200 для CASE_DISPATCH/FULLPAL_DISPATCH/OUTBOUND_WORKLOAD, на складе 1 status=NO_SERIES. /project не вызывал и автоматически вызывать не буду.

Замечено при чтении (не меняю, сообщаю):
1. Текущий day-reconciliation.js не имеет подписей для ключей interwarehouse_* (daily_facts и current_backlog) — выводится «undefined · N». Исправлю в своём файле.
2. Прозрачность: до получения C-0001 в этой сессии я по прямому поручению владельца вёл twin/wms_twin_3d и дописывал строки о нём вверх wiki/index.md и в конец wiki/log.md (14.10, несколько записей «digital twin»), а также создал wiki/requirements/twin_*.md, wiki/concepts/warehouse_transport_digital_twin_principles.md, wiki/subprojects/wms_twin_3d.md. Дальше в index/log не пишу — wiki-изменения по NI07.2/NI08.1 оформлю предложением в отчёте. Если мои прежние строки мешают интеграции, сообщите — перенесу их в proposals/.

## K-0002 · 2026-10-14T09:59+03:00 · RESULT · C-0001 задача A (NI07.2) · требуется ответ о принятии
Прочитаны C-0002 и C-0003 (срок 18:45 MSK учтён; записи о двойнике оставляю как есть).

Результат: обзор сверки дня в назначенных файлах.
Файлы:
- wiki-raw/wms_admin_ui_reference/day-reconciliation.html — заменён только блок обзора #dayOverview; подключён day-reconciliation-catalog.js; ID/разметка/скрипты фиксации, журнала, осмотра, грузовой зоны, переноса СТ, ожидания и выбора рейса сохранены.
- wiki-raw/wms_admin_ui_reference/day-reconciliation.js — переписан обзор.
- wiki-raw/wms_admin_ui_reference/day-reconciliation-catalog.js — новый каталог показателей (все ключи daily_facts/current_backlog/open_items текущего ответа, включая interwarehouse_* — undefined устранён).
- wiki-raw/wms_admin_ui_reference/day-reconciliation.css — стили .day-page .dr-overview и body.day-page{min-width:0} при max-width:1279px.

Сценарии (живой API, склад 1, 14.10, Asia/Tbilisi): положительный (2 открытых пункта с причиной/действием/реестром), устаревший ответ после смены даты не отрисован, 422 пояс, 403 чужой склад, пустой склад, фильтр загруженного, соседний GET review-context работает (запись не нажимал), консоль без неожиданных ошибок. Скриншоты desktop 1440 / mobile 390.
Отчёт: reports/nicora/2026-10-13/claude/NI07.2/report.md; предложение wiki: reports/nicora/2026-10-13/claude/NI07.2/wiki-update-proposal.md.

Ограничения: внешние ACK этим API не сверяются (показано явно); ссылки только на реестры — в ответе нет ID документов (необязательное предложение контракта include_samples в отчёте). Обратите внимание: общий styles.css задаёт body{min-width:1280px}; на этой странице оно снято только для body.day-page при <1280px — мобильные правила соседних блоков этой страницы теперь срабатывают, desktop не затронут. Долгий SQL: 666 мс холодный / 8–10 мс повторно — оставить. Авторская проверка, не независимое ревью; полный спринт NI07.2 не закрываю.

RELEASE: day-reconciliation.html, day-reconciliation.js, day-reconciliation-catalog.js, day-reconciliation.css, reports/nicora/2026-10-13/claude/NI07.2/.
Перехожу к задаче B (NI08.1).

## K-0003 · 2026-10-14T10:07+03:00 · CONTRACT_REQUEST · C-0001 задача B (NI08.1) · требуется ответ
Зачем: TASK B запрещает выводить потребность в людях/технике/слотах без нормативов производительности. Нормативы в системе есть (RRL_WORKLOAD_NORM: WARE_ID, SITE_CODE, ARTICLE, BASE_UOM, BASE_PER_HOUR, VERSION_NO; чтение GET /api/resources/workload/warehouses/{ware_id}), но контракт прогноза их не использует и нигде не определено соответствие вида работы прогноза (CASE_DISPATCH/FULLPAL_DISPATCH/OUTBOUND_WORKLOAD) участку норматива SITE_CODE. Пересчёт на клиенте был бы выдуманной формулой — не делаю.

Предлагаемый контракт (владелец — transport/resources, решение за Codex):
- Новый read-only эндпоинт, например POST /api/transport/warehouse-forecast/warehouses/{ware_id}/workload-view, вход = текущий ForecastRequest + необязательный site_code.
- Сервер сопоставляет каждый READY-ряд прогноза с действующей версией RRL_WORKLOAD_NORM по (WARE_ID, ARTICLE, BASE_UOM) и правилу scope→SITE_CODE, которое хранит владелец (не UI).
- Выход по ряду: article, base_uom, estimated_quantity (как сейчас), norm_base_per_hour (строка), norm_version, norm_site_code, estimated_hours (точная строка, правило округления на сервере), norm_status ∈ {APPLIED, NO_NORM, NO_SCOPE_MAPPING, FORECAST_BLOCKED}.
- Агрегат: total_estimated_hours только по рядам APPLIED + счётчики неприменённых рядов; без перевода в людей/слоты, пока нет контракта явки/смен (RRL_WORKLOAD_ATTENDANCE) и слотов.
- Обратная совместимость: /view не меняется.
Пока ответа нет, экран показывает блок «не вычисляется в этом контракте» со ссылкой на resource-workload.html; остаток NI08.1 обозначен в отчёте.

## K-0004 · 2026-10-14T10:08+03:00 · RESULT · C-0001 задача B (NI08.1) · требуется ответ о принятии
Результат: экран объяснимого прогноза в назначенных файлах.
Файлы:
- wiki-raw/wms_admin_ui_reference/warehouse-forecast.html — переработан.
- wiki-raw/wms_admin_ui_reference/warehouse-forecast.js — переписан.
- wiki-raw/wms_admin_ui_reference/warehouse-forecast.css — новый (body.wf-page{min-width:0} при <1280px; общий styles.css не менял).
- wiki-raw/wms_admin_ui_reference/warehouse-forecast-explain.js — новый.

Сценарии (живой API, Playwright): ADVISORY склад 9104 (ряд DS-BASE-D10, формула из чисел ответа), INSUFFICIENT_HISTORY (минимум 3), NO_SERIES склад 1, NEEDS_PROJECTION склад 381877 (панель обновления подсвечена), ввод 91 отсечён у поля без запроса, устаревший ответ после смены горизонта не отрисован, смена параметров убирает результат. Вызовов /project — 0 (кнопку не нажимал, проекцию не менял); ошибок консоли — 0. Скриншоты desktop 1440 / mobile 390.
Отчёт: reports/nicora/2026-10-13/claude/NI08.1/report.md; предложение wiki: reports/nicora/2026-10-13/claude/NI08.1/wiki-update-proposal.md.
Долгий запрос: /view 0,08–0,14 с — оставить.
Ограничения: ресурсная потребность — остаток NI08.1, см. K-0003; на dev реальный ряд только у склада 9104, десятки складов в NEEDS_PROJECTION (решение об обновлении истории за владельцем данных). Авторская проверка, не независимое ревью; полный спринт NI08.1 не закрываю.

RELEASE: warehouse-forecast.html, warehouse-forecast.js, warehouse-forecast.css, warehouse-forecast-explain.js, reports/nicora/2026-10-13/claude/NI08.1/.
Назначенные задачи A и B сданы. Жду ответа о принятии K-0002/K-0004 и решения по K-0003; новых файлов не занимаю.

## K-0005 · 2026-10-14T10:12+03:00 · STATUS · ответ не обязателен
По прямому поручению владельца («делай коммиты») выполнил локальные коммиты в feature/transport-dispatch-phase1, без push/fetch/PR:
- 48fe1406 feat(twin): twin/wms_twin_3d.
- 988a3bf9 docs(wiki): страницы двойника; в wiki/index.md и wiki/log.md застейджены только мои строки о двойнике (6 и 4), остальные незакоммиченные правки этих файлов остались в рабочей копии нетронутыми.
- a4cc5043 feat(nicora): NI07.2 — day-reconciliation.html/.js/.css, day-reconciliation-catalog.js, reports/.../NI07.2.
- e9bbf938 feat(nicora): NI08.1 — warehouse-forecast.html/.js/.css, warehouse-forecast-explain.js, reports/.../NI08.1.
Внимание: файлы day-reconciliation.* и warehouse-forecast.* до этого не отслеживались — коммиты включают их исходную версию. Соседние скрипты страницы сверки (day-review*.js, day-inspection.js, shipping-register.js, st-*.js) и resource-workload.html — твоя незакоммиченная работа, в коммиты не включены; до их коммита страница сверки в HEAD ссылается на неотслеживаемые скрипты. Папку coordination/ и чужие файлы не коммитил.

## K-0006 · 2026-10-14T10:43+03:00 · ACK · C-0004 · ответ не требуется
Прочитал C-0004: принятие K-0002/K-0004 учтено; K-0003 (scope→SITE_CODE, total_estimated_hours как частичный итог) — за тобой, на клиенте людей/слоты не считаю.
Принимаю NI07.1/CC-04 (дополнение TASK.md). Рабочий каталог C:\projects\TMS.
Файлы владения до RELEASE: admin/wms_admin_frontend/src/features/finance/BillingWarehouseCosts.tsx, BillingTransportCosts.tsx, BillingExtraExpenses.tsx, новые BillingCosts*.tsx и BillingCosts.css; reports/nicora/2026-10-13/claude/NI07.1/.
Не трогаю: finance index/contracts/api, App/router/styles.css, VehicleTareVariants, TransportDispatchPage.tsx (место встраивания BillingWarehouseCosts, строка ~3995), backend/Oracle. Действующие команды и защиту от повторов сохраняю; автоматический retry не добавляю. Чужие счета и начисления ради показа не меняю.

## K-0007 · 2026-10-14T11:18+03:00 · CONTRACT_REQUEST · C-0004 (NI07.1) · требуется ответ
Зачем: владелец потребовал, чтобы для любой суммы счёта всегда можно было получить документ-основание или начисление-основание. Для складских и транспортных начислений это закрыто существующими GET (rates/history, transport-cost-facts). Для допрасходов строка GET /api/finance/expense-allocation/billing-orders/{invoice_id} (infrastructure/expense_allocation.py, invoice) не содержит WARE_ID, EXPENSE_DATE, автора и решений; сейчас склад определяю по начислениям того же рейса, а решения беру из GET /api/finance/logistics-expenses/warehouses/{ware} (последние 100). Если у рейса нет начислений или расход старше 100 записей — решения недоступны.

Предлагаемый аддитивный контракт (тот же эндпоинт, новые поля, старые без изменений):
- ware_id (e.WARE_ID), expense_date (e.EXPENSE_DATE), reporter (e.ACTOR), article_code;
- logist_operation_id, logist_outcome, logist_actor, logist_decision_reference; finance_operation_id, finance_decision_reference, finance_actor (из RRL_LOGISTICS_EXP_DECISION по фазам);
- confirmed_total (как в logistics_expenses.pending — итог с утверждёнными коррекциями).
Обратная совместимость: поля добавляются; фронтенд работает и без них (текущий запасной путь), при наличии — использует напрямую.

## K-0008 · 2026-10-14T11:19+03:00 · RESULT · C-0004 (NI07.1/CC-04) · требуется ответ о принятии
Результат: расшифровка существующего счёта и основания сумм.
Файлы: admin/wms_admin_frontend/src/features/finance/BillingWarehouseCosts.tsx, BillingTransportCosts.tsx, BillingExtraExpenses.tsx (изменены); BillingCostsCommon.tsx, BillingCostsInvoice.ts, BillingCostsSummary.tsx, BillingCostsBasis.tsx, BillingCosts.css (новые). Публичный экспорт index.ts не менял (BillingWarehouseCosts({invoiceId})), TransportDispatchPage/общие файлы не трогал.

- Сводка по валютам: категории раздельно, валюты не складываются, точная десятичная сумма внутри валюты (BigInt), отклонённые расходы вне итогов.
- Складские группы/источники с периодом и версией ставки; транспорт исходно→с корректировками, норма, выезд, округление; допрасходы с состоянием и «Дальше», фильтр.
- Основание любой суммы (кнопка «Основание»): версия ставки (документ решения, причина, автор); факты рейса (приёмки, способы выгрузки, документы-доказательства); документ расхода, решения, переход по цепочке коррекций к исходному начислению. CSV всех оснований счёта.
- Узкая карточка счёта (~243 px): строки таблиц — карточки (container query).

Проверка: tsc PASS; python scripts/nicora_quality_gate.py PASS (architecture PASS, 24 passed, оба typecheck); check-encoding PASS. Playwright: реальный счёт БТ-0527 (честные пустые состояния — на стенде у счетов нет начислений), синтетика формы API на БТ-0528 только в тесте (валюты, корректировка, состояния, основания, CSV), 403 по одному источнику, смена счёта во время медленного ответа. Действующие команды (TransportTariffSources) сохранены; автоповторов нет; данные не менялись.
Отчёт: reports/nicora/2026-10-13/claude/NI07.1/report.md; wiki: reports/nicora/2026-10-13/claude/NI07.1/wiki-update-proposal.md.
Ограничения: решения по допрасходу без K-0007 доступны не всегда; реальные начисления счёта на стенде отсутствуют. Авторская проверка, не независимое ревью; полный спринт NI07.1 не закрываю.

RELEASE: features/finance/BillingWarehouseCosts.tsx, BillingTransportCosts.tsx, BillingExtraExpenses.tsx, BillingCostsCommon.tsx, BillingCostsInvoice.ts, BillingCostsSummary.tsx, BillingCostsBasis.tsx, BillingCosts.css, reports/nicora/2026-10-13/claude/NI07.1/.

## K-0009 · 2026-10-14T11:21+03:00 · STATUS · ответ не обязателен
По поручению владельца («делай коммиты») локальный коммит bbeea210 (без push): только мои файлы NI07.1 — features/finance/Billing*.tsx/.ts, BillingCosts.css и reports/.../NI07.1. Исходные версии трёх Billing*.tsx (твои, ранее неотслеживаемые) включены; остальные файлы features/finance (TransportTariffSources и др., на которые ссылается BillingTransportCosts) — твоя незакоммиченная работа, в коммит не входят.

## K-0010 · 2026-10-14T11:31+03:00 · QUESTION · C-0005 · требуется ответ до 13:25 MSK
Прочитал C-0005 (принятие NI07.1 и поручение реализовать K-0007 на сервере: expense_allocation.py + мои Billing-файлы). Сводка всей моей работы за сегодня: [CLAUDE_WORK_REPORT_20261014.md](CLAUDE_WORK_REPORT_20261014.md).

Вопрос: что мне делать дальше? Подтверди, что следующая задача — C-0005/K-0007 в описанных границах, либо назначь другую/приоритетнее. По поручению владельца в 13:25 MSK я заберу из CODEX_TO_CLAUDE.md твоё последнее поручение и начну исполнение; если отдельного ответа не будет — исполняю C-0005. До 13:25 файлов не занимаю.

## K-0011 · 2026-10-14T13:31+03:00 · ACK · C-0008 (C-0005/C-0006 включены как этап 1)
Принял C-0008 по TASK_C0008.md. Работа над C-0005 до этого не начиналась, поэтому этап 1 делаю с нуля в границах C-0005, этап 2 — потом.
Мои файлы до RELEASE:
- api/wms_api_server/app/modules/finance/infrastructure/expense_allocation.py — только read invoice и при необходимости новый read-helper `expense_basis_read.py` рядом; финансовые команды не трогаю;
- связанные finance contracts — только аддитивная типизация, если понадобится (о каждом сообщу в RESULT);
- admin/wms_admin_frontend/src/features/finance/Billing*.tsx, BillingCosts*.ts, BillingCosts.css;
- wiki-raw/wms_admin_ui_reference/logistics-expenses.html, logistics-expenses.js, новые logistics-expenses-*.js, logistics-expenses.css;
- reports/nicora/2026-10-13/claude/NI07.1-C0008/.
Не трогаю: Oracle DDL/PLSQL, financial write-команды, logistics-costs.*, общие App/router/styles.css/admin-nav, forecast/day-reconciliation, файлы NI06.x, общие wiki index/log. K-0003 не переделываю. Общий API не перезапускаю.

## K-0012 · 2026-10-14T14:05+03:00 · RESULT (этап 1 C-0008 = C-0005/K-0007) · файлы держу до этапа 2
Локальный коммит `aa8f049f` (без push).
**Контракт** `GET /api/finance/expense-allocation/billing-orders/{invoice_id}` — аддитивно, прежние поля и их смысл сохранены:
- `ware_id`, `expense_date` (YYYY-MM-DD), `reporter` (ACTOR расхода), `article_code`;
- `logist_operation_id`, `logist_outcome`, `logist_actor`, `logist_decision_reference`;
- `finance_operation_id`, `finance_actor`, `finance_decision_reference` (`finance_outcome` был);
- `confirmed_total` — семантика `expense_correction.confirmed_total`: исходный расход + подтверждённые FINANCE APPROVE коррекции `CORRECTION_OF_OP`; **только для исходника**, для строк-коррекций `null` (у них `expected_confirmed_total`). Реестр склада (`pending`) для коррекций сейчас отдаёт AMOUNT+0 как confirmed_total — в счёте я так не делаю; если нужно, это твоя правка `logistics_expenses.py`.
- `expected_confirmed_total` — добавлен для коррекций.
- `amount` — по-прежнему подписанная сумма строки; теперь `to_char(...,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')`, т.е. точка независимо от NLS сессии. Сумма распределения в ответ не подмешивается (только `allocation_operation_id`, `distribution_basis`, `goods_lines`).
**Реализация:** SQL вынесен в новый `finance/infrastructure/expense_basis_read.py`; `ExpenseAllocation.invoice` делегирует. Фазы присоединяются двумя left join по `PHASE` (unique(EXPENSE_OPERATION_ID,PHASE) — дубликатов 0 на стенде), распределение — unique(EXPENSE_OPERATION_ID). Область — тот же join `RUSERS` (u.WARE_ID=e.WARE_ID или GLOBAL_ADMIN), лимит 200 строк счёта прежний. Поиска по «последним 100» больше нет. Ports/routes/contracts не менялись.
**SQL decision:** один запрос, коррелированные подзапросы только скалярные по PK/FK (CORRECTION_OF_OP, ALLOC_LINE.OPERATION_ID); 7 строк — 4–8 мс прямым SQL (5 замеров), API отвечает в пределах прежнего. Оставить; на росте счетов смотреть план подзапроса confirmed_total.
**Проверки (авторские):** реальный API — все 7 реальных TRIP-расходов стенда (у их рейсов PAY_ORDER_ID=0, поэтому читаются через `/billing-orders/0`; ни один реальный счёт расходов не содержит, `/527` → []); совпадение ware/даты/решений/актеров с реестром склада; точная строка `12345678901234567.89`; GLOBAL_ADMIN 7 строк, пользователь чужого склада 0, неизвестный актор 0. UI: Playwright desktop/mobile + режим старого сервера (поля убраны → явная пометка и прежний поиск), запросов к реестру склада при прямом основании 0. Нормативная коррекция без транспортного начисления в счёте показывает склад и реестр исходника. tsc admin PASS; полный gate запущу после этапа 2.
Скриншоты/скрипт: `reports/nicora/2026-10-13/claude/NI07.1-C0008/screenshots/s1_*`, `scripts/stage1_invoice_basis.cjs`. Перехожу к этапу 2 (logistics-expenses).

## K-0013 · 2026-10-14 · RESULT (этап 2 C-0008) + CONTRACT_REQUEST + RELEASE
Отчёт: [report.md](../../reports/nicora/2026-10-13/claude/NI07.1-C0008/report.md); скриншоты `screenshots/s2_*`; сценарии `scripts/stage2_expenses_screen.cjs` и `stage2_result.json`; предложение для wiki — `wiki-update-proposal.md`.

**Файлы этапа 2:**
- `wiki-raw/wms_admin_ui_reference/logistics-expenses.html`, `logistics-expenses.js`;
- новые `logistics-expenses-model.js`, `logistics-expenses-view.js`, `logistics-expenses-actions.js`, `logistics-expenses.css`.

Все прежние ID и формы сохранены; общие styles/nav не менялись; серверные правила не дублировались — UI только подсказывает.

**Эффект:**
- **Карточки:** документ, стадия, ответственный, цепочка «логист → финконтроль → распределён / только автомобиль».
- **Фильтры** по загруженному окну; окно названо прямо.
- **Итоги** по валютам точной BigInt-арифметикой.
- **Следующее действие** только заполняет существующую форму, POST 0.
- **Права:** `calc_tt_price`, `create_tt_price`, `edit_bill_tt`; финконтроль выполняет другой сотрудник.
- **Предпросмотр коррекции:** знак, дельта, итог A → B.
- **Устаревший ответ** при смене склада отбрасывается.
- **Повтор** тем же `operation_id` и телом; успех — после сверки идентичности ответа; повреждённая сохранённая запись блокирует новые команды.

**Проверка (авторская):**
- Реальное чтение склада 2378876 на desktop и mobile.
- Адресные сценарии с подставленными ответами только в тесте: стадии, права, смена склада во время чтения, обрыв, несовпадающий ответ, повтор, повреждённая запись.
- gate PASS (architecture, 24 passed, tsc admin и terminal), check-encoding PASS.

**Реальная запись не выполнялась.**

**CONTRACT_REQUEST:**
1. **Fixture для реального цикла.** Нужен dev-склад с двумя активными пользователями (не GLOBAL_ADMIN) с паролями для dev-входа:
   - A — `edit_bill_tt` и `calc_tt_price`;
   - B — `create_tt_price`;
   - рейс, связанный со складом через `RRL_TT_HU_LOAD_FACT` или `RRL_SBORKA_PALLETS`, с фактической погрузкой;
   - активная статья (`included_in_rate=0`, scope TRIP).

   Тогда пройду регистрацию → LOGIST → FINANCE → распределение и коррекцию через UI.
2. **`logistics_expenses.pending()`** (твой файл):
   - окно `order by CREATED_AT fetch first 100` отдаёт первые 100, а не последние — предлагаю `desc` или keyset и точный поиск `?operation_id=`;
   - добавить `finance_actor`, `logist_decision_reference`, `finance_decision_reference`;
   - для коррекций `confirmed_total` должен быть `null`, как в счёте.

   UI готов принять эти поля: они показываются, если присутствуют.

**RELEASE:**
- `finance/infrastructure/expense_allocation.py`, `expense_basis_read.py`;
- `features/finance/Billing*`, `BillingCosts*`;
- `wiki-raw` `logistics-expenses.*` и `logistics-expenses-*.js/.css`;
- `reports/.../NI07.1-C0008`.

Finance contracts не трогал. Локальные коммиты: `aa8f049f` (этап 1) и `2145a383` (этап 2).

## K-0014 · 2026-10-14T15:03+03:00 · ACK · C-0010
Принял TASK_C0010.md. Порядок: 1) pending read-contract + надёжное хранение намерения; 2) fixture C0010 (два пользователя WARE_ID=9807, своя статья) и реальный цикл через UI на рейсе 33571; 3) NI07.2 переходы сверки.
Мои файлы до RELEASE:
- api/.../finance/infrastructure/logistics_expenses.py (только read `pending`), новый read-helper `expense_register_read.py`; связанные finance ports/application/routes — только аддитивный параметр точного поиска `operation_id` в `GET /logistics-expenses/warehouses/{ware}`;
- прежние: expense_allocation.py (invoice read), expense_basis_read.py, features/finance/Billing*, BillingCosts*, wiki-raw logistics-expenses*;
- wiki-raw day-reconciliation.html/.js/.css/-catalog.js и новые day-reconciliation-*.js (этап 3);
- reports/nicora/2026-10-13/claude/C0010/.
Собственные dev-данные: пользователи C0010_LOGIST/C0010_FINANCE (пароли только в памяти), статья DEV.C0010.*, документы DEV.C0010.*, рейс 33571 только как объект расхода. Write-команды и бизнес-правила не меняю; для fix write-пути — сначала CONTRACT_REQUEST. Общий сервер не перезапускаю.

## K-0015 · 2026-10-14 · RESULT (C-0010 п.1–2: финансовый сценарий NI07.1) · RELEASE finance-файлов
Локальный коммит `9d7c5055` (без push). Отчёт будет в `reports/nicora/2026-10-13/claude/C0010/report.md` вместе с NI07.2; данные уже лежат там: `c0010_cycle_result.json`, `c0010_ui_steps.json`, `c0010_verify.json`, `c0010_recovery.json`, `screenshots/c1_*`, `c2_*`.

**Контракт** `GET /api/finance/logistics-expenses/warehouses/{ware}` (аддитивно, совместимо):
- окно — новейшие 100, `order by CREATED_AT desc, OPERATION_ID desc`;
- `?operation_id=` — точный поиск за пределами окна в том же складе; прежняя проверка `require_warehouse` сохранена (чужой склад → `[]`, пустая строка → 422);
- новые поля `finance_actor`, `logist_decision_reference`, `finance_decision_reference`;
- `confirmed_total` = `null` для коррекций, `expected_confirmed_total` отдельно; `amount` с точкой независимо от NLS.

Файлы: `logistics_expenses.py` (только `pending`), новый `expense_register_read.py`, `contracts_expenses.py` (параметр по умолчанию `None`), `logistics_expense_routes.py` (Query-параметр).

**UI** (`logistics-expenses*`, новый `logistics-expenses-intent.js`):
- **запись намерения** с проверкой чтением: при отказе хранилища POST не уходит (адресно: 0 POST, понятное сообщение);
- **неизвестный результат** сохраняет тот же ID и тело;
- **повреждённая запись** блокирует новые команды. Кнопка «Проверить по ID» ищет точно на сервере:
  - найдено → результат установлен, запись можно закрыть;
  - не найдено → по-прежнему заблокировано;
  - удаление без установленного результата — только для записи, где ID нет вовсе;
- **успех, но запись не удалилась** → новые команды заблокированы, пока запись не закрыта (адресно проверено);
- **точный поиск** расхода по ID на экране; найденная вне окна строка помечена;
- **коррекция** при решении подставляет базу исходного расхода.

**Fixture (собственный, RABAEV):**
- группы и пользователи `C0010_LOGIST` (wms_admin_login, transport_dispatch_view, edit_bill_tt, calc_tt_price) и `C0010_FINANCE` (wms_admin_login, transport_dispatch_view, create_tt_price), WARE_ID=9807, не GLOBAL_ADMIN;
- пароли случайные, только в памяти процесса и в Oracle, в отчётах не выводятся (проверено);
- статья `DEV.C0010.PARKING` (TRIP, included_in_rate=0) создана через UI пользователем B.

**Реальный цикл через UI, рейс 33571** (маршрут, погрузка и остатки не менялись; обе погрузки остались DEPARTED):

| Шаг | Кто | Операция | Результат |
|---|---|---|---|
| 1 | A | регистрация `DEV.C0010.DOC-1`, 12.34 GEL | `EXPENSE:a32f1713…` |
| 2 | A | LOGIST BASE_QUANTITY | `EXPENSE:652c5bde…`; у A кнопка финконтроля недоступна (нет права) |
| 3 | B | FINANCE | `EXPENSE:db40bae4…` |
| 4 | A | распределение | `EXPENSE:300791a6…`: 2 строки 6.17 + 6.17 = 12.34; повтор того же operation_id → тот же результат ALLOCATED, распределений по расходу 1 |
| 5 | A | коррекция `DEV.C0010.CORR-1`, −2.10 | `EXPENSE:a1a748b2…`; предпросмотр «12.34 → 10.24» |
| 6 | A → B → A | LOGIST, FINANCE, распределение коррекции | `EXPENSE:21f5c943…`: строки 1.05 + 1.05, знак применяется при чтении |
| итог | | | текущий итог исходника 10.24 GEL |

- **Outbox:** по одному событию `EXTRA_EXPENSE_RECOGNIZED` ×2 и `EXTRA_EXPENSE_ALLOCATED` ×2 (поиск по `FIN:sha256(type:op)`).
- **Товарный эффект:** операций в `RRL_STOCK_OPERATION` с этими ID — 0; `stock_changed:false`.
- **Чужие расходы** не менялись.

**SQL decision:** окно 100 — 3–6 мс, точный поиск — 1.5–3 мс (5 замеров). Индекса `(WARE_ID, CREATED_AT)` нет: используется `RRL_LOG_EXP_DOC_UQ` с ведущим `WARE_ID`, затем сортировка; при текущих объёмах оставить. При росте склада свыше ~10⁴ расходов — индекс `(WARE_ID, CREATED_AT desc, OPERATION_ID desc)`; это DDL, он твой.

**Gate:** PASS; check-encoding PASS. Проверка авторская.

**RELEASE:** `finance/infrastructure/logistics_expenses.py`, `expense_register_read.py`, `expense_basis_read.py`, `expense_allocation.py`, `contracts_expenses.py`, `api/logistics_expense_routes.py`, `features/finance/Billing*`, `BillingCosts*`, `wiki-raw logistics-expenses*`. Fixture-пользователи C0010 остаются на стенде для повторной проверки (DELETED=0). Перехожу к п.3 (NI07.2), держу файлы day-reconciliation*.

## K-0016 · 2026-10-14 · RESULT (C-0010 п.3: NI07.2) + CONTRACT_REQUEST + RELEASE
Локальный коммит `2dd1a922` (без push). Итоговый отчёт по всему C-0010: [report.md](../../reports/nicora/2026-10-13/claude/C0010/report.md); предложение для wiki — `wiki-update-proposal.md`.

**Пробелы NI07.2, найденные и закрытые в моих границах:**
- **Переходы** из обзора теряли склад и дату. Теперь `day-reconciliation-links.js` передаёт склад, дату или ID только экранам, которые их читают (проверено по коду):
  - `interwarehouse-groups` — `warehouse_id`;
  - `logistics-expenses` — `warehouse_id`, `operation_id`;
  - `warehouse-tasks` — `preset`, `task_id`;
  - `pallet-composition` — `identifier`.

  Для остальных экранов под ссылкой честно написано «укажите склад N и дату D».
- **Прямая ссылка** `day-reconciliation.html?warehouse_id=&day=` с проверкой значений сама формирует сверку. После чтения адрес обновляется, поэтому «назад» из реестра возвращает тот же контекст. Проверено на складе 9807 за 14.10, desktop и mobile.
- **Второй реестр и проведение** не созданы. Отсутствие ACK ERP и госсистем не выдаётся за сверку.
- **day-review / day-inspection / shipping-register** не менялись. Панели на этой странице уже берут общие поля склада и даты, так что переходы внутри страницы контекст сохраняют.

**CONTRACT_REQUEST (следующий реальный пробел, вне моих файлов):**
1. В `GET /api/finance/day-reconciliation/warehouses/{ware}` для каждого `open_items[]` и пункта backlog отдавать до 20 ID документов-образцов и флаг усечения. Тогда переход ведёт к конкретному документу, а не в общий реестр.
2. Научить читать `?warehouse_id=` (и `?day=`, где он есть) экраны: logistics-costs, external-outbox, tare-ledger, tare-loss, store-investigations, store-return-putaway, supplier-handover, return-disposal, interwarehouse. Каталог перехода готов: достаточно добавить имя экрана в `ACCEPTS`.
3. **Найдено попутно:** `admin-auth.js` в `verifyStoredSession` удаляет сессию при любой ошибке, включая прерванный уходом со страницы fetch. Быстрое «назад» выкидывает пользователя на форму входа. Предлагаю удалять сессию только при ответах 401/403.

**Gate:** PASS; check-encoding PASS. Проверка авторская.

**RELEASE:** `wiki-raw day-reconciliation.html/.js/.css/-catalog.js`, `day-reconciliation-links.js`, `logistics-expenses-actions.js` (прямая ссылка), `reports/.../C0010`. Занятых файлов у меня больше нет. Fixture-пользователи C0010 остаются на стенде (DELETED=0) для повторной проверки, пароли нигде не сохранены.

## K-0017 · 2026-10-14T15:42+03:00 · ACK · C-0015 (C-0011…C-0016 прочитаны)
Принял TASK_C0015.md: вариант повреждённой оборотной тары NI06.3. C-0013/C-0014 учтены: API готов, POST разрешены. Пункт 2 K-0016 по return-workspace-link не дублирую.
Мои файлы до RELEASE:
- admin/wms_admin_frontend/src/features/inventory/Tare*.tsx, tareResult.ts, useTare.ts, TareWorkspace.css;
- аддитивные типы в inventory/api.ts (если понадобятся);
- небольшие новые UI-helpers рядом;
- reports/nicora/2026-10-13/claude/C0015/.
Dev-данные: ровно одна GOOD-единица собственного магазина (контекст 1348); участники OWN1348_STORE/OWN1306_DRIVER; новый пользователь C0015_TARE_APPROVER без GLOBAL_ADMIN (пароль только в памяти/Oracle); документы DEV.C0015.*. Tare write-пакеты, DDL, финансы, router не трогаю; для серверного пробела — CONTRACT_REQUEST.

## K-0018 · 2026-10-14 · RESULT (C-0015, NI06.3 повреждённая тара) + RELEASE
Локальный коммит `1c01ae25` (без push). Отчёт: [report.md](../../reports/nicora/2026-10-13/claude/C0015/report.md); предложение для wiki — `wiki-update-proposal.md`; данные — `c0015_result.json`, `c0015_ui_facts.json`, `c0015_checks.json`, `screenshots/t*`.

**Порядок по нативному контракту** (не обходился):
1. `TARE_DAMAGE` у держателя: магазин, `tare_damage`, ссылка на исходную выдачу.
2. Возврат через `/offer` и `/accept` с `DAMAGED` и `damage_operation_id`; позиция акта переходит к получателю.
3. `TARE_WRITE_OFF`: `tare_writeoff`, исполнитель не автор акта; при таре, отслеженной до склада-владельца, — `writeoff_warehouse_id` и сотрудник склада.

**UI** (`features/inventory`):
- новые `TareDamageCases.tsx` (карточки актов: исходная выдача, текущий держатель, списано и остаток, следующий шаг — кнопка только заполняет существующую форму) и `TareWriteoffForm.tsx`;
- правки `TarePanel.tsx`, `TareDamageSource.tsx` (выбор предложенного акта), `tareResult.ts` (строгая проверка повреждения и списания), `useTare.ts` (запись намерения с проверкой чтением; блок, если подтверждённую запись не удалось удалить), `TareWorkspace.css`.

Серверных изменений нет, CONTRACT_REQUEST не потребовался.

**Реальный цикл** (склад 9807, рейс 33571, тип 1, собственный магазин):

| Шаг | Участник | Операция |
|---|---|---|
| Повреждение 1, акт `DEV.C0015.DAMAGE-1` | OWN1348_STORE | `TARE:5040b7ad-9750-4d90-b031-15d2c97cb228` |
| Возврат магазин → водитель | OWN1348_STORE / OWN1306_DRIVER | `TARE:f138e802…` / `TARE:7889cce5…` |
| Возврат водитель → склад | OWN1306_DRIVER / admin | `TARE:a83ff5b8…` / `TARE:83ba2e59…` |
| Списание `DEV.C0015.WRITEOFF-1` | новый C0015_TARE_APPROVER | `TARE:f8fa5dcf-be39-4b41-b933-0d8455a0083f` |

- **Повтор списания:** первый ответ потерян браузером, повтор того же ID → тот же результат, outbox 5237; строк решения по ID — 1.
- **Баланс:** до — 4/2/0 GOOD; после — склад 4 GOOD, магазин 1 GOOD, машина 0, DAMAGED 0 везде, итого 5.
- **Долг магазина:** выдача 2 → 1, долг по акту — 0.
- **Товарный эффект:** `RRL_EVENTS` по 6 операциям сценария — 0.

**Права:**
- `OWN1348_STORE` — добавлено `tare_damage`;
- `C0015_TARE_APPROVER` (группа `C0015_TAREAPPR`: `USER_GROUP.ID` ≤15 символов) — `tare_view` и `tare_writeoff`, `WARE_ID=9807`, не GLOBAL_ADMIN;
- пароли не сохранялись.

**Адресно, без записи:** автор акта с правом списания блокируется в UI; списать больше остатка нельзя; при отказе хранилища POST 0; mobile без горизонтальной прокрутки.

**SQL:** акты склада — 11 мс; новых запросов нет; индексы не нужны.

**Gate:** PASS; check-encoding PASS. Проверка авторская.

**Для интеграции:** файлы `features/inventory/Tare*` раньше не отслеживались. Мой коммит включает твои исходные версии изменённых и новых файлов. `TareBalanceSummary.tsx`, `TareDamageForm.tsx`, `TareLossForm.tsx` и `api.ts` не менялись и в коммит не вошли — их закоммитишь ты.

**RELEASE:** `features/inventory/Tare*.tsx`, `tareResult.ts`, `useTare.ts`, `TareWorkspace.css`, `reports/.../C0015`. Занятых файлов нет.
