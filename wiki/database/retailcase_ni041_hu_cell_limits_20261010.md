# NI04.1: ограничения физической ячейки и настройки единиц

055 implementation: дополняется slot adapter053 проверкой MAX_WEIGHT_KG/MAX_VOLUME_M3 опубликованной topology cell, помимо ограничений самого слота и legacy RRL_CELLS. Пока одна пустая ячейка на верхнее место, поэтому сумма равна подтверждённым измерениям этого HU. Несколько мест потребуют отдельной суммарной проверки.

Единица legacy LIMIT_HEIGHT уже добавлена в существующий receiving settings API/ARM. Старый caller, не передающий новое поле, сохраняет настройку; явный null её очищает. На приватном dev-складе save/preserve/clear/restore прошли. Старые default Decimal поля модели приведены к Decimal без изменения смысла настроек.

CASE preview/API подтверждены в native CASE12+8 fixture: одно место20/H20, два неизвестных gross листа и неизвестная тара CASE не объявлены известной массой. Старые internal CASE идентификаторы сохраняются до GS1 normalization, если совпадают с фактическим carrier code. Дополнительный запас не создаётся.

055 APPLIED, RRL_STOCK_HU_SLOT VALID, checkpoint319. Slotted task5/H2 passed with explicit topology-cell low weight denial, restored own fixtures. Settings save/preserve/clear/restore passed through existing config service. Same indexed target/slot lookup retained; broader multi-place aggregate scope remains open.
