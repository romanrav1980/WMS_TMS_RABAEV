# C0095 — отдельное приложение магазина: RESULT

15.10.2026, Claude (отдельная сессия C0095, инструменты Read/Edit/Write/Glob/Grep — без Bash/сети).

## Что сделано

Самостоятельный модуль `terminal/wms_terminal_web/src/features/store-receiving/**`, публичный `index.tsx` экспортирует `StoreReceivingApp`. Codex подключает его через отдельный entry `/store/` (manifest/SW/Vite — его область, не трогал).

Поток экрана: вход собственными credentials (HTTP Basic, в памяти, без fallback на admin env) → `GET /api/store-app/session` → выбор магазина (авто при одном, явный список при нескольких) → `GET /api/store-app/deliveries` (серверная пагинация `after`/`limit=50`) → карточка поставки `GET /api/store-app/deliveries/{load_operation_id}` → три режима по `preview.mode` (BARCODE/WEIGHT_PHOTO/PAPER_COUNT, сервер назначает, клиент не переключает) → `POST /api/delivery/store-receipts/confirm` (прежний контракт + `paper_reference` для PAPER_COUNT) → акт приёмки.

### Файлы
- `contracts.ts`, `api.ts`, `messages.ts` — локальные типы и HTTP-клиент (`VITE_WMS_API_BASE_URL`, Basic auth, честная ошибка при 404/не-JSON/нет сети, различение подтверждённого структурированного отказа от неизвестного исхода — принцип C-0036/C-0062).
- `receiptIntentValidation.ts`, `receiptResult.ts` — валидация сохранённой команды и ответа сервера (адаптированы из принципов `admin/features/delivery`, код не импортирован между проектами).
- `useStoreSession.ts`, `useStoreDeliveries.ts`, `useStoreReceivingFlow.ts` — сессия, список поставок, основной цикл приёмки (pending/retry/restart/corrupt-recovery, offline → черновик, auto-retry при возврате сети, operation_id не создаётся повторно для одной команды).
- `photoApi.ts` — переиспользование существующего `/api/delivery/store-photos/*` с собственными credentials магазина (без нового writer).
- `components/*` — LoginScreen, StoreSelector, DeliveriesList, DeliveryDetail (оркестратор режима), UnloadingStep, MarkedGoodsPanel/MarkedGoodsSummary (сверка маркировки — обязательна во всех трёх режимах, если товар маркирован), WeightEvidencePanel (вес + ≥3 фото реальной камерой устройства + показания шлюза весов), DiscrepancyFields (опционально для BARCODE/WEIGHT_PHOTO, принудительно для PAPER_COUNT), ReceiptSummary (акт).
- `help/*` — локальный модуль справки (offline, без сети): `helpArticles.ts`, `HelpContext.tsx`, `HelpHint.tsx`, `HelpPanel.tsx`. Каждый контрол имеет `data-help-id` + title-подсказку + переход в статью.
- `docs/help/authoring/store-receiving-app.md`, `-barcode.md`, `-weight-photo.md`, `-paper-count.md`, `-recovery.md` — опубликованные статьи (тот же текст, что в `helpArticles.ts`), формат соответствует существующим `docs/help/authoring/*.md`.
- `styles.css` — локальные стили, scoped `.store-app-*`, mobile-first (крупные поля, работа с клавиатурным сканером), не трогает `admin`/общий `terminal` styles.css.

## Ограничения и честные допущения

- Backend `/api/store-app/session`, `/api/store-app/deliveries`, `/api/store-app/deliveries/{id}` на момент сдачи в канале помечены Codex как «ещё проверяю» (C-0096). UI делает реальные HTTP-запросы по объявленному контракту; при 404/недоступности сервера показывает честную ошибку источника, не демо-данные.
- `/api/delivery/store-receipts/confirm`, `/api/delivery/store-receipts/unloading/start`, `/api/delivery/store-photos/*`, `/api/delivery/store-scales/captures` — существующие эндпойнты (использовались admin-панелью приёмки). Переиспользованы как заявлено в TASK; не проверено мной живым HTTP (нет сетевых инструментов), поэтому не исключено, что они ожидают другую идентичность пользователя, чем новая `/api/store-app/session`. Вопрос передан Codex в `CLAUDE_C0095_TO_CODEX.md`.
- WEIGHT_PHOTO фотофиксация использует реальный `<input type=file capture="environment">` (камера устройства через браузер) — не сымитирована. Если устройство/браузер не поддерживает камеру, выбор файла остаётся доступен через обычный выбор файла ОС (честно, без фиктивного успеха — но это не доказанная «живая» камера, зависит от устройства).
- Квитанция маркированной продукции (StoreMarkControl) проверяется клиентски по `expected_scan_count`/`marked_partial_control`; окончательное решение о полноте состава — сервер (как и в admin-варианте).
- TypeScript/build/Playwright/Oracle-проверки не выполнялись мной (инструменты недоступны). Список необходимых проверок — ниже.

## Проверки, которые нужно выполнить (Codex/root)

1. `tsc --noEmit` в `terminal/wms_terminal_web` (новый код использует строгие типы, mirror существующих паттернов `admin/features/delivery`, ожидаю PASS, но не запускал).
2. `python scripts/retailcase_quality_gate.py` — архитектурный gate (новая feature-папка с публичным `index.tsx`, не должна зацепить baseline).
3. Подключение `StoreReceivingApp` к реальному Vite multi-entry `/store/` и ручная проверка на мобильном экране 390px.
4. Живая проверка контракта `/api/store-app/*` после READY: вход, список, карточка, все три режима, 401/403 → logout, lost-response → retry, confirmedRejection → restart, offline → черновик → auto-retry при восстановлении сети.
5. Подтверждение, что `/api/delivery/store-photos`, `/api/delivery/store-scales/captures`, `/api/delivery/store-receipts/unloading/start` и `/confirm` принимают новые store-app credentials (не только старые admin-driver credentials).

## RELEASE

Файлы `terminal/wms_terminal_web/src/features/store-receiving/**`, `docs/help/authoring/store-receiving*.md` готовы к подключению entry. Жду READY backend-контракта и живую проверку от Codex; при расхождении контракта — готов внести точечные правки без полной переделки.
