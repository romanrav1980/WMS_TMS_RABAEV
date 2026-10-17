# API_READY_FINISH_KPI — installed16.10,18:01МСК

Backend установлен, API перезапущен. Это готовая задача2 после C0118; не расходовать отдельный запрос на ожидание. Задача3 остаётся на финальные дефекты. Работать по PROMPT_FINISH_KPI_B_20261016.txt с уточнениями ниже, RESULT_C0119.md/RELEASE в прежний канал. Backend/SQL не менять. Не создавать бизнес QA.

## Готовые чтения

- `GET /api/resources/picker-kpis?warehouse_id&start_at&finish_at&operator_id` — aware ISO параметры, период максимум31день, operator_id необязателен. `case_pick_view` текущего WARE даёт обзор, исполнитель `case_pick_execute` — только себя. Чужой человек/склад403. Переполнение5000фактов/500операторов422: сузить период, никакой ложной полноты.
- `GET /api/delivery/timing/kpis?warehouse_id&start_at&finish_at` — `transport_dispatch_view` текущего WARE, максимум31день/500доставок. 403/422/503 отображать отдельно. Только форматирование на клиенте.
- `GET /api/delivery/timing/place?load_operation_id&store_address` — окно/прибытие отдельно по фактическому грузу/магазину. Текущий диспетчер склада, привязанный водитель или свой приёмщик; чужой магазин403.

Точные положительные JSON: `reports/retailcase/2026-10-16/kpi-pick-proof/forward/kpi-result.json` и поле `kpi` в `reports/retailcase/2026-10-16/delivery-time/acceptance-v5.json`. Живой тестовый склад20790457, picker `OC16P5e071e9f41`, поездка33653. Период2026-10-16T00:00:00+03:00..2026-10-17T00:00:00+03:00. 25EA = BOX24+EA1, boxes1/lines1, точные повторения не удваивают. Доставка ON_TIME/FULL=1, оба наблюдённых процента100.000. Авторизоваться штатной локальной сессией, credentials не помещать в файлы/скриншоты. Пользователь теста вскоре будет retired; администратор продолжит видеть историю. Не строить UI вокруг тестового ID.

## Picker DTO и честная подпись

Корень `warehouse_id,start_at,finish_at,as_of,formula_version=PICKER_KPI_V1,operators[],scope=REGISTERED_OBSERVATIONS,work_coverage_certified=false,source_limitations[],stock_changed=false`.

Оператор: `operator_id,completed_lines` number, `boxes` decimal string|null, `box_reasons[]`, `quantities[{article,base_uom,quantity}]`, `registered_assembly_hours/registered_shift_hours` decimal string|null; `rates.{lines_per_assembly_hour,boxes_per_assembly_hour,lines_per_shift_hour,boxes_per_shift_hour}` decimal string|null. `time_basis=REGISTERED_CONFIRMED_INTERVALS`, `work_coverage_certified=false`, `uncovered_work_operations/uncovered_shift_operations[]`, `time_reasons.{assembly[],shift[]}`. Drill-down `facts[{operation_id,actor,at,task_id,line_id,article,base_uom,previous,cumulative,planned,delta,boxes,packaging_reason}]`; previous/cumulative никогда не суммировать на клиенте.

Обязательная короткая подпись «По зарегистрированным интервалам». Полнота учёта всей работы не сертифицирована; не писать «полная выработка смены подтверждена». Паузы вычтены только из сборки; смена содержит паузы. Aware clock — запись native факта, не датчик физического движения. Исторический BOX неизвестен → null, не0. Нет часов/факт вне интервала → null. Причины объяснить в help/details, не занимать половину экрана техническими надписями.

## Delivery DTO

Корень `warehouse_id,start_at,finish_at,formula_version=DELIVERY_KPI_V1,cohort_basis=LATEST_PLANNED_WINDOW_START_OR_UNPLANNED_OBSERVED_EVENT,deliveries[],timing,receipt,source_limitations[],stock_changed=false`.

`timing` числа ON_TIME/EARLY/LATE/NO_ARRIVAL/NO_PLAN, `observed_planned`, `on_time_percent_of_observed` decimal string|null. `receipt` FULL/WITH_ISSUES/PENDING числа, `received`, `full_percent_of_received` decimal string|null. Обязательные знаменатели: «из N прибытий с планом», «из N завершённых приёмок». Это не общий OTIF всей программы: ожидающие/нет плана видны отдельно, не считаются успехом. Не перемножать проценты. Отмены/недоказанные факты не объявлять просрочкой автоматически.

Строка delivery: `load_operation_id,store_address,trip_id,load_status,window_operation_id,window_version,window_start,window_finish,arrival_operation_id,arrived_at,on_time_state,receipt_operation_id,receipt_state,received_at,receipt_mode,line_count,issue_count,full_state`. Times — aware ISO|null. План заморожен до выезда, источник прибытия вручную подтверждённый; legacy пояс не придумывается. Drill-down через существующие экраны/GETplace и ясные IDs, не новый движок отчётов.

## Файлы и приёмка

Создай отдельную frontend feature `admin/wms_admin_frontend/src/features/platform/workspaces/kpi/` с index.tsx; свяжи с существующим меню рабочих мест, при необходимости ровно один существующий вход `WorkplaceHome.tsx` после RELEASE C0118. title/help на действиях, обычная локальная help статья в docs/help/public. Графическая компактная подача в стиле двойника, фильтр склада/периода, сохранение контекста. Локальная datetime форма обязана преобразовывать явный часовой пояс в ISO, показывать используемую зону компактно. Изменять delivery POST/UI фиксации прибытия в этой задаче не требуется, root обеспечит отдельно.

Один ACK с файлами → реализация → TS + desktop/390 + live positive/403 → RESULT_C0119/RELEASE. Без повторных native/load suites. Root делает общий gate/build/Oracle/slowSQL. При несовпадении DTO сообщи конкретную ошибку и продолжай независимую часть.
