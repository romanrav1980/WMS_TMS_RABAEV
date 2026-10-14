# NI04.2 — версия физического количества для измерений
10.10.2026.072 APPLIED в RABAEV/orcl; foundation для measured standalone stock placement, следующий slice ещё не реализован.

RRL_REMAINS.PHYSICAL_VERSION — монотонный NUMBER epoch на существующей UID/cell строке. Изменение P в единственном BALANCE_CORE increment1, включая рождение/перемещение/списание/исправление. Изменение только HARD сохраняет epoch, хотя прежний STOCK_VERSION продолжает увеличиваться. Qty6→5 не возвращает прежний epoch; прошлые измерения не воскресают только от совпадения числа.

PHYSICAL_VERSION_GUARD требует существующий STOCK effect/context/UID/cell/lock и точную формулу нового epoch. Это контроль метаданных, не второй исполнитель остатков. Oracle transaction/journal/outbox/P/H invariants и stock optimistic version не заменены. Исторические строки получили0 как старт будущей версии, не утверждение отсутствия старых движений.

RRL_STOCK_HU_UNIT_SIGNATURE считает bounded sorted physical unit key/BASE qty/UOM digest (до10000, STOCK_STATUS!='ISSUED', actual current UID/cell). HARD allocation не меняет physical signature. Same-quantity marked-unit replacement меняет unit digest независимо от P epoch. Warehouse signature не государственный ACK.

Добавлены nullable HU_PHYSICAL_VERSION/HU_UNIT_SIGNATURE в existing slot claim для следующего measured stock leaf slice. Container claims и текущие функции не требуют этих полей. Rollback не должен выполняться при активном зависимом measured-stock placement; additive columns/history сохраняются.

Own scripts/ni042_physical_epoch_case.py passed: birthP5/H0→epoch1; HARD2/release двигают STOCK_VERSION, сохраняют physical1; countP6→2/countP5→3; direct epoch rewrite denied, signature64hex; own count0/release cleanup/journal retained. Изменён именно stock core, поэтому выполнен один связанный business case, без широкого набора.

Slow SQL keyed stock snapshot/UPDATE использует прежний unique UID/cell и exact STOCK_VERSION compare; добавленный epoch не добавляет отдельной SQL записи. Решение — одна guarded row update, без индекса на изменяемый counter; мониторить hot UID wait/throughput в NI08. Промышленная нагрузка этим case не доказана.

Remaining: bind measured standalone stock claims to physical epoch/unit digest, source depletion/actual physical release handling, direct CASE placement and variable-weight/BOX identity business scope.
