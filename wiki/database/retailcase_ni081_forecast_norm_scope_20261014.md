# NI08.1: связь прогноза с нормативом участка

Миграция2026-10-14-1328-forecast-norm-scope PREPARED. Владелец resources. Append-only RRL_WORKLOAD_SCOPE_SITE(warehouse, work_scope, version) связывает CASE_DISPATCH/FULLPAL_DISPATCH/OUTBOUND_WORKLOAD с явным SITE_CODE существующих норм RRL_WORKLOAD_NORM. Не угадываем соответствие названий, универсальную производительность или численность людей.

Запись FORECAST_SCOPE в прежнем RRL_WORKLOAD_CONFIG_API: текущий склад/право resource_shift_edit, существующая короткая metadata transaction, expected_version и исходный operation_id/hash, история и нативный guard. Replay сохраняет решение; другой payload того же ID отвергается. Обновление нормы и mapping не изменяет запас, присутствие или задания.

Read model получает mapping + актуальные нормы SKU/base_uom в том же readonly snapshot прогноза. Трудозатраты = прогноз количества / base_per_hour, Decimal; отсутствующая/неактивная норма оставляет строку без часов. Частичный итог явно отделён от полного; заблокированный прогноз не даёт рекомендацию по часам. Не вычисляем работников без плановых доступных часов и квалификации.

LIVE исходник и INVALID=[] сохранены; rollback возвращает код без удаления истории. Применение/API/UI/evidence ожидаются.

## Installed1341
4/0, USER_ERRORS=[], INVALID=[]. API/UI и source/runtime mirror подключены. [Actual результат](../components/retailcase_ni081_forecast_labour_20261014.md), report47; K-0003 реализован, независимая/промышленная приёмка отдельно.
