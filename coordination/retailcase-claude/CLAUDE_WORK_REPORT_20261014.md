# Claude Code → Codex: сводка выполненной работы

Дата: 14.10.2026, 11:30 MSK. Рабочий каталог: `C:\projects\TMS`, ветка `feature/transport-dispatch-phase1`. Все коммиты локальные, push/fetch/PR не выполнялись. Проверки авторские, не независимое ревью. Полные спринты не закрывались.

## 1. Назначения через канал координации

| Задача | Сообщения | Статус Codex | Коммит |
|---|---|---|---|
| NI07.2 — обзор сверки дня | ACK K-0001, RESULT K-0002 | принято C-0004 (UI-часть) | `a4cc5043` |
| NI08.1 — объяснимый прогноз нагрузки | RESULT K-0004, CONTRACT_REQUEST K-0003 | принято C-0004; K-0003 (scope→SITE_CODE) у Codex | `e9bbf938` |
| NI07.1 — расшифровка счёта и основания сумм | ACK K-0006, CONTRACT_REQUEST K-0007, RESULT K-0008 | принято C-0005 (UI-часть) | `bbeea210` |
| K-0007 — поля основания в строке допрасхода | поручено C-0005 | ожидает старта | — |

### NI07.2 — обзор сверки дня
- **Файлы:** `wiki-raw/wms_admin_ui_reference/day-reconciliation.html` (только блок `#dayOverview`), `.js`, `.css`, новый `day-reconciliation-catalog.js`.
- **Группы:** «за сутки», «сейчас», «внешнее». У каждого показателя есть смысл, следующее действие и ссылка на существующий реестр. Блок «Известная неполнота данных».
- **Внешние подтверждения:** в ERP «отправлено» отделено от «подтверждено»; принятие госсистемой «не сверялось».
- **Поведение:** фильтр по загруженному, отмена устаревшего ответа, понятные 422/403.
- **Исправлено:** вывод «undefined» для `interwarehouse_*`.
- **Мобильная вёрстка:** `body.day-page{min-width:0}` при ширине меньше 1280px; общий `styles.css` не менялся.
- **Соседние блоки страницы:** ID и скрипты сохранены.
- Отчёт: `reports/retailcase/2026-10-13/claude/NI07.2/report.md`.

### NI08.1 — прогноз нагрузки
- **Файлы:** `warehouse-forecast.html`, `.js`, новые `warehouse-forecast.css`, `warehouse-forecast-explain.js`.
- **Форма:** проверка по границам ForecastRequest.
- **Объяснения:** итоговые статусы ADVISORY, NEEDS_PROJECTION, NO_SERIES, INSUFFICIENT_HISTORY и статусы строк; сводка окна; таблица с формулой из чисел ответа; разные единицы не суммируются.
- **Обновление истории** `/project`: только по кнопке, с подтверждением и правом.
- **Ресурсная потребность** не вычисляется (K-0003).
- Отчёт: `reports/retailcase/2026-10-13/claude/NI08.1/report.md`.

### NI07.1 — расшифровка счёта
- **Файлы:** `admin/wms_admin_frontend/src/features/finance/BillingWarehouseCosts.tsx`, `BillingTransportCosts.tsx`, `BillingExtraExpenses.tsx`; новые `BillingCostsCommon.tsx`, `BillingCostsInvoice.ts`, `BillingCostsSummary.tsx`, `BillingCostsBasis.tsx`, `BillingCosts.css`.
- **Сводка по валютам:** категории раздельно, валюты не складываются, точная десятичная сумма внутри валюты.
- **Основание любой суммы** (требование владельца):
  - складское начисление → версия ставки (документ решения, причина, автор);
  - транспорт → факты рейса (приёмки, выгрузки, документы-доказательства);
  - допрасход → документ, решения, цепочка коррекций до исходного начисления.
- **CSV всех оснований счёта.**
- **Узкая карточка счёта:** строки таблиц показываются карточками.
- **Ограничение до K-0007:** решения по расходу доступны, только если склад определяется по начислениям рейса; реестр расходов склада читается до 100 записей.
- Отчёт: `reports/retailcase/2026-10-13/claude/NI07.1/report.md`.

## 2. Работа до назначения (по прямому поручению владельца)
- **3D-двойник склада и транспорта** `twin/wms_twin_3d` (`48fe1406`): React 19 + Three.js/R3F.
  - SIM-режим: симуляция операций.
  - LIVE-режим, только чтение: топология по правилу WMS (последняя PUBLISHED, `LEGACY_CELL_CODE`), рейсы и СТ ТМС, складские задания и CASE-сборка, состояние связи.
- **Wiki** (`988a3bf9`): `concepts/warehouse_transport_digital_twin_principles.md`, `subprojects/wms_twin_3d.md`, `requirements/twin_source_system_requirements.md`, `requirements/twin_live_data_fixes_codex_prompt.md`. В `index.md` и `log.md` закоммичены только строки о двойнике.

## 3. Проверки
- `python scripts/retailcase_quality_gate.py` — PASS (architecture PASS, 24 passed, typecheck admin и terminal).
- `scripts/check-encoding.ps1` — PASS.
- Playwright-сценарии и скриншоты desktop/mobile лежат в отчётах.
- Синтетические ответы в форме API используются только в тестовых скриптах; в коде приложений синтетики нет.

## 4. Что важно для интеграции
- **Неотслеживаемые файлы.** Файлы `day-reconciliation.*`, `warehouse-forecast.*` и три исходных `Billing*.tsx` раньше не отслеживались; мои коммиты включают их исходную версию (твою).
- **Твоя незакоммиченная работа, на которую ссылаются мои страницы:** скрипты страницы сверки (`day-review*.js`, `day-inspection.js`, `shipping-register.js`, `st-*.js`), `resource-workload.html`, `features/finance/TransportTariffSources.tsx` и соседние. В коммиты не входят, пока ты их не закоммитишь.
- **Wiki-изменения по NI07.2, NI08.1, NI07.1** оформлены предложениями в `reports/.../wiki-update-proposal.md`; общие `index`/`log` интегрируешь ты.
- **Тестовый service worker.** Service worker admin-приложения перехватывает запросы; в Playwright для подстановки ответов его нужно блокировать (`serviceWorkers: "block"`).
- **Ошибки WebSocket** `/api/admin/transport/ws/dispatch` (404) в консоли админки существовали до меня.

## 5. Открытые вопросы
- **K-0003** (Forecast scope→SITE_CODE, частичный `total_estimated_hours`) — у тебя.
- **K-0007** — поручено мне в C-0005. По поручению владельца начинаю в 13:25 MSK, после чтения твоего ответа на K-0010.
