# C0171 — остановлено по указанию владельца 26.10 09:52 МСК (не завершено)

T08 не принят. Ни одна проверка C0171 не выполнена до конца. Это передача состояния Codex.

## Набор (принадлежит теперь Codex)
- Склад 223214750 «TRADECASE QA c9a41e1d»: новый, отсутствие проверено предикатом до insert. Товар TC03C9A41E1D (SKU A: 10 шт/короб, 0,40×0,50×0,50 м, 10 кг, NORMA_UKLADKI=20, 4×5).
- Состояние: `runtime/test-evidence/tradecase/2026-10-26/T08/topup-physical-660.json`, phase `MAIN_PLANNED`. Сценарий: `tests/tradecase/live_topup_physical_660.py` (этапы receive → main_orders → topup → pick → load).
- Выполнено штатными API, команды от admin:
  - 33 паллеты по 200 EA приняты через SAP supply order;
  - SUPPLY bind SNS/МРЦ 200, размещение в 33 ячейки хранения, вердикт СКМ VALID (синтетический);
  - Oracle: 6600/HARD 0/33 паллеты.
- Документы: site, OWNER SNS/BLC, SKU A, RECIPIENT C1 (customer 776), ORDER O1 6000 EA, машина 10131 с профилем 33 места (13,2×2,5×2,0 м, синтетика), TRIP T1 v1 (66 м³ / 6600 кг), NEED N1 (дополнительно 80 коробов).
- Нативный заказ 2214/строка 3701 привязан к O1; plan 2271; волна 625 рассчитана; ячейка приёмки переведена в EXPEDITION.
- Свой актор настройки TC03c9a41e1d выведен (DELETED=1, назначение отозвано). Других акторов нет.
- 32 дополнительные ячейки хранения T3Sc9a41e1d02..33 и правило STORAGE — DML по образцу `live_stock_acceptance.setup`, только на этом складе.

## Незавершённая операция
- `POST /api/picking/waves/625/launch`, operation_id `TP26.c9a41e1d.main.launch`, ответ HTTP 500 Internal Server Error за 3585 мс.
- Oracle READ ONLY после ответа: волна PREVIEW, строки RRL_STOCK_OPERATION нет, заданий волны 0, HARD 0. Применения нет.
- Причину 500 нужно смотреть в журнале API (у Claude журнала нет). Повторять только тот же operation_id.

## Найдено попутно
- `tests/tradecase/live_trade_pick_shortage.py` (сценарий root C0170): putaway стоит до SUPPLY bind, а штатный путь отвечает 409 `TRADE_CELL_ATTRIBUTES_REQUIRED`. Сначала нужен SUPPLY и bind, затем putaway — как в `live_stock_acceptance.py`.
- Одна ячейка хранения не вмещает вторую паллету («No storage slot satisfies occupancy...»): нужна отдельная ячейка на каждую паллету.

## Не сделано (остаётся Codex)
- Запуск основной волны (30 целых паллет).
- Добивка 80 → 60 + 20 необеспеченных, гонка двух согласований ADJUST, confirm/replay, синтетический SAP, TRIP v2, перенос удержаний волной.
- 33 задания, привязка отгрузок, контроль, LOAD, итог 660/66/6600, 640.
- Паллетоместа и штабелирование: расчёт `floor_places_checked=False`, источника раскладки нет — открыто.
- Очистка набора не выполнялась.
