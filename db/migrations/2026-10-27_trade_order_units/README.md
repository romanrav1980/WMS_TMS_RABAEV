# 2026-10-27 trade order units (C-0175) — NOT_APPLIED

С C-0175 строка ORDER нормализуется при приёме документа (Python, `tradecase_documents._normalize_order`): входная единица → единственная единица обработки SKU, всегда вниз, коэффициенты из RRL_STOCK_UOM_CONVERSION. Строка без исполнимого количества (ноль после округления, нет коэффициента или настройки) хранится с `quantity`=0 и `normalization.executable=false`.

Без этого комплекта native-приём отклоняет такое сообщение целиком (`WHOLE_UNIT_REQUIRED`). Комплект:
- `RRL_TRADE_DOCUMENT_API`: неисполнимая строка принимается только с количеством 0 (`NON_EXECUTABLE_LINE_QUANTITY_MUST_BE_ZERO`); назначение такой строки в TRIP отклоняется (`ORDER_LINE_NOT_EXECUTABLE`).
- `RRL_TRADE_ORDER_API.bind_order`: число складских строк сверяется только с исполнимыми строками документа, неисполнимые пропускаются. Документ без исполнимых строк не привязывается — ни волны, ни резерва.

Откат: только над точными after SHA (`AFTER_SOURCE_DRIFT_REFUSED`) и только пока нет принятых ORDER с неисполнимыми строками (`TRADE_ORDER_UNIT_HISTORY_PRESENT`). Применяет root.
