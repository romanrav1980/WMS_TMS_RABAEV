# RESULT C-0143 — T08: согласование добивки (срез native + API + UI)

Обращение 2 из 3 новых (22.10). ACK K-0091/K-0094, REVIEW_READY K-0095, RELEASE K-0096. **T08 целиком не закрыт**: миграция в Oracle не применена Claude, живая приёмка не выполнена (подробности ниже).

## Что сделано

**Миграция** `db/migrations/2026-10-22_trade_topup_proposal` — **NOT_APPLIED_BY_CLAUDE**. Подробности в REVIEW_READY_C0143.md.
- Таблицы: RRL_TRADE_TOPUP_PROPOSAL, RRL_TRADE_TOPUP_DECISION, RRL_TRADE_TOPUP_HOLD, RRL_TRADE_TOPUP_EVENT; последовательность RRL_TRADE_TOPUP_PROPOSAL_SQ.
- Пакеты:
  - RRL_TRADE_TOPUP_READ — базис места рейса, подтверждённое по потребности, защищённый запас основных заказов, выбор целых коробов FEFO, карточка;
  - RRL_TRADE_TOPUP_API — save / decide / sap_accept / list без складских эффектов, с блокировкой площадки и журналом точного повтора;
  - RRL_TRADE_TOPUP_CMD — StockPosting `TRADE_TOPUP_CONFIRM` / `TRADE_TOPUP_RELEASE`.
- Минимальные патчи общих объектов:
  - RRL_STOCK_POSTING_API — 2 строки диспетчера;
  - RRL_TRADE_STOCK_GUARD — whitelist;
  - RRL_TRADE_PICK_CONTEXT — гейт `TRADE_TOPUP_HOLD_ADOPTION_REQUIRED`;
  - ACCESSIBLE BY у RESERVE_CORE и UNIT_CORE.
- Preflight проверяет SHA до изменения, verify и rollback_verify — после. Rollback отказывает при наличии данных.
- Удержание — настоящий HARD (`TRADE_TOPUP` / SHIPMENT) с явными единицами; подтверждение, удержание и один исходящий запрос `TRADECASE_TOPUP_REQUESTED` выполняются одной транзакцией StockPosting.

**API** `/api/tradecase/warehouses/{w}/trips/{trip}/topup-proposals`: GET, POST save, POST `{id}/decision`, `{id}/confirm`, `{id}/release`, `{id}/sap-reply`.
- Неизвестный исход → 503 `retry_same_operation_id`; подтверждённый отказ → 409/403.
- Расчёт учитывает:
  - подтверждённые добивки рейса как занятую загрузку;
  - покрытие потребности другими рейсами;
  - собственника, МРЦ и ОСГ из основного заказа;
  - пригодный запас сверх основных заказов (`limited_by`: CAPACITY / SENDER_STOCK).

**UI** (`features/integrations/tradecase`):
- `TopupProposals.tsx` (новый): список, «почему столько», изменить в пределах расчёта, отклонить, подтвердить, отменить, связь с заказом SAP и признак «документ заказа получен», удержание.
- Все решения — долговечные команды журнала `tradecase.topup`: потеря ответа → «Повторить ту же команду» тем же телом, остальные решения заблокированы.
- Пока сервер отдаёт `approval_available=false`, «Подтвердить» недоступна с пояснением.
- `TopupPreview`: «Сохранить как предложения».
- `TripExecution`: подключение.
- Справка: `public/help/tradecase-documents.html#topup.decide`.

## Файлы

- **Коммит** `9f62fcb8` (checkpoint до apply, только мои файлы, без push): миграция целиком, `contracts_trade_topup.py`, `contracts_trade_transport.py`, `api/trade_transport_routes.py`, `infrastructure/trade_topup.py`, `infrastructure/trade_topup_proposals.py` (новый), `infrastructure/trade_transport.py`, `inventory/contracts_stock.py` (+2 вида без строк), `reports/.../C0143/scripts/build_topup_*.py`.
- **После коммита, не закоммичено:**
  - типы в `trade_transport_routes.py` и `trade_transport.py` (требование architecture gate);
  - `TopupProposals.tsx`, `TopupPreview.tsx`, `TripExecution.tsx`, `tradecase-documents.html`;
  - `tests/tradecase/test_trade_topup_proposals.py`;
  - `reports/tradecase/2026-10-22/claude/C0143/{scripts/c0143_ui.cjs, c0143-ui.json, screenshots/topup-proposals-{1440,390}.png}`.

## Проверки

- **Oracle (только чтение, разрешено владельцем):**
  - USER_SOURCE пяти общих объектов совпал со снимками T08 Codex;
  - INVALID 0;
  - кодировка БД AL32UTF8, поэтому SHA preflight/verify совпадают с подсчётом в Python.
- **Apply не выполнен:** OracleApply отклонён классификатором Claude Code («Modify Shared Resources»), обхода не было.
- **Офлайн:**
  - `tests/tradecase/test_trade_topup_proposals.py` — 14 PASS: контракты, формат времени и чисел для Oracle, условия из основного заказа, разделение неизвестного исхода и отказа, команда отклонения SAP;
  - `python -c "import app.tradecase_composition"` OK;
  - `python scripts/retailcase_quality_gate.py` PASS (1205 файлов, 0 циклов; architecture сначала FAIL из-за двух моих нетипизированных функций — исправлено, baseline не расширялся; оба TS);
  - `check-encoding.ps1` PASS.
- **UI, FIXTURE** — `c0143_ui.cjs` 18/18 на итоговой сборке `index-g5PbXs94.js` (:3000), 1440 и 390:
  - живые только вход и GET рейса R1.1155 склада 215590763;
  - эндпоинты добивки перехвачены: 99 HTTP, 0 POST до сервера, 0 JS-ошибок;
  - проверены: причина количества, связь с заказом SAP без полученного заказа, сохранение порядка приоритетов и возраста, изменение в пределах, потеря ответа на подтверждение с повтором тем же телом, отклонение без заданий, отмена, `approval_available=false`, отказ при смене базиса места, 403 без данных;
  - скриншоты просмотрены лично.

## Не выполнено / не проверено (T08 остаётся открытым)

1. Apply / rollback / reapply, SHA и INVALID после, живые API и Oracle, конкуренция 40+40, revoke, lost reply, exact replay — всё ждёт применения миграции (Codex или Claude после разрешения на изменение БД).
2. Атомарное принятие удержания волной (WAVE_RESERVE_SOURCES: перенос HARD `TRADE_TOPUP` → `PICK_WAVE` в одной транзакции). Сейчас — гейт, сборка добивки невозможна.
3. Добивка после начала погрузки (нужна сверка состава и доступа при выгрузке); сценарии 80 → 60+20, 66 → 64 со снятием 20, отмена после сборки, учёт «заказано / собрано / погружено / отправлено / остаток», передача в СКМ только отправленных кодов.
4. Внешняя отправка в SAP и создание заказа: подключения нет; ответ SAP проверяется только через API и как synthetic.
5. SQL review и индексы — после функционального набора на живой базе. Запросы `candidates` / `eligible_units` ограничены 200 источниками, `protected_units` — 200 строками.
6. Wiki: правки `wiki/index` / `wiki/log` и `wiki/database/tradecase_topup_*` не делал — передаю Codex по итогам применения.

**Деплой:** API добивки (preview и save) вызывает RRL_TRADE_TOPUP_READ, поэтому выкатывать только после миграции. Флаг `approval_available` нигде не включён.

Блокер: применение миграции. Файлы T08 освобождены (RELEASE K-0096); следующий пакет — C-0145.
