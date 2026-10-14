# NI07.2: перенос отобранной плоской паллеты

743/746 APPLIED в RABAEV, USER_ERRORS=[]/INVALID=[]. Существующий RRL_ST_DEFER_API теперь допускает полностью завершённый отбор плоских товарных паллет. Прежние unassign/assign_sts, сортированные locks/CONFIG6, reason/reference/version/sourcehash и immutable decision сохранены. Новое решение не меняет P/H, исходный заказ, физические ключи, журнал отбора или завершённое задание.

RRL_ST_DEFER_PHYSICAL сопоставляет все текущие fulfillment с DONE PICKING_MOVE, исходной UID и фактическим единственным положительным остатком текущего склада. P и H равны сумме факта для всей паллеты; один физический UID с несколькими fulfillment считается через общий LOT_FACT_QTY. Нельзя переносить смешанный picked/unpicked состав, открытое физическое задание, CASE, вложенный HU, действующую погрузку или выезд. Onward/recovery ST требует изменения своего неизменного межскладского плана; обычный defer не переписывает frozen target trip.

Для picked источника source hash включает physical_preparation: fulfillment/task/picked operation/UID/фактическая ячейка/исходная ячейка отбора/количество/stock versions. Для прежнего unpicked источника новый материал не добавляется, старый hash сохраняется. Cached результат выдаётся после текущих прав и без повторного проведения.

Actual744 использовал уже принятую SAP688 паллету с internal UID47 и исходными3units6codes. Новый dev demand/wave/ST/два будущих рейса; исходная purchase receipt не пересоздавалась. Прежнее root reservation3, pick move3 и bind сформировали P3/H3/FF PICKED3. Положительное новое движение соответствует дальнейшему использованию тех же единиц. Не повторять factory688 и начальные P3/H0 assertions. Context744 стадия DEFERRED_PREPARED; context688 historical birth/PUT сохранён.

Actual745: whole ST перенесена на следующий из двух запланированных дней. Outer rollback вернул исходное назначение и убрал незакоммиченный decision. После commit exact replay совпал. P3/H3/FF PICKED3/UID47 сохранены, новых RRL_EVENTS по defer operation нет; защищённый P20/H20 неизменён. Физический перенос в ожидание не выполнен этой командой: result.physical_move_required=true, operational_admission=false. Форма объясняет необходимость штатного складского задания. CASE/nested перенос и полный NS58 остаются открыты.

746 расширяет snapshot на фактическую текущую ячейку, сохраняя original_picked_cell; immutable completed task не переписывается. Запрет frozen onward ST добавлен явно. После746 compilation VALID; дальнейший positive replay/context и bounded original unpicked regression указаны отдельно после исполнения.

SQL745 first43.655мс/113buffers, steady5.325мс/38buffers. Решение transport: сохранить bounded200 fulfillment и существующие FK/UID-cell индексы; при большом числе переносов профилировать native CONFIG6 contention/план, не убирать consistency fence ради параллелизма.

[Миграция](../../db/migrations/2026-10-12_ni072_prepared_st_deferral/apply.sql) содержит captured body/SHA/rollback. Ни второго назначения, ни второго stock writer.

## Checkpoint748–759: граница физического продолжения

После746 actual748: current native/HTTP context готовой СТ и exact saved745 совпали; old unpicked276 replay unchanged. Encoding747 PASS.

753 проверил общий MANUAL PUTAWAY на собственном источнике в rollback: ядро отказало TASK_DOMAIN_HANDLER_REQUIRED. Guard не отключался. Fresh metadata task отменено существующим WarehouseTaskService;759/758 подтвердили P3/H3, CANCELLED и отсутствие committed PROBE stock operation. Cell DW753 retained как dev metadata. Перенос в ожидание требует отдельного typed source handler в существующих RRL_STOCK_TASK_PLAN/CORE/DOMAIN, привязанного к defer decision; перенос через произвольный MANUAL не допускается. RRL_STOCK_TRANSFER_CORE.move остаётся единственным исполнителем переноса и резерва.

Следующий ticket: настройка выделенной ячейки ожидания того же склада, создание штатного задания из подтверждённого решения defer, source/resource declarations, проверка latest decision/current exact stock/FF before move и сохранение первоначального picked task. Root TASK_COMPLETE должен атомарно провести move+H carry+unit cells+DONE/SYNCED/outbox. CASE/nested и frozen onward route — отдельные источники; не расширять общий guard для всех MANUAL задач.
