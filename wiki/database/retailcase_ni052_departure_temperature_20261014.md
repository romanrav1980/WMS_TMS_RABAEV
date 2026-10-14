# NI05.2 — температура перед выездом
Миграция2026-10-14-1170-departure-temperature подготовлена; ещё не применена.

Общий thermal helper получает phase=MANUAL_AT_DEPARTURE; прежний load core использует defaultMANUAL_AT_LOADING. Температурный товар требует нового подтверждения непосредственно перед выездом с текущей версией профиля. Под CFG/vehicle/TT/ST locks повторяются текущие диапазоны и профиль до смены статуса рейса. Повтор загрузочного подтверждения с origin загрузки не разрешает выезд.

Результат фиксируется в неизменяемых RESOLVED_PLAN_JSON/RESULT_JSON существующей Root операции TRIP_DEPART, вместе с исходным depart_instant, journal/outbox и RRL_TT_VEHICLE_SOURCE. Отдельного температурного журнала выезда и новой quantity транзакции нет. Товар повторно не списывается.

Оригинальный loading1160 уже установлен; отдельный тест1168/1169 загрузил собственный3EA при3.125°C: missing/20°C rejected before goods, outerrollback returned P3/H3 and nofacts, finalP0/H0/replay, protected987P20/H20. First test setup omitted mandatory PICK_CELL; resumed same retained lot/trip, не создавая заново запас.

API/интерфейс имеют отдельный ввод для выезда с разрешением transport_dispatch_close. Старые запросы без блока не приобретают null-поля в canonical metadata. Status читает сохранённое подтверждение через исходный departure operation/class-source PK в том же readonly scoped snapshot. Датчик/непрерывный контроль/придуманный TTL не заявлены. Source checkpoint/apply/verify/forward-only recovery сохранены. Native positive departure ещё ожидает.

1172: native positive sameoriginal33636/LOAD3.125→DEPART3.75/replay; missing/new20°C denied, outerrollback restores LOADED/no departure-source, finalRootresult/currentstatus captures both values; DEPARTquantity journal0, protectedP20H20. Helper/core/root/depart/triggererrors empty/VALID. Currenttemperature on departure is manual confirmation, not sensor or continuous control.

Actual longest thermalquery675.298ms/13575buffers despite JOIN hints. Prepared1173 replacement uses DBMS_SQL with ≤200 named numeric IN binds and ≤1000SKU rows; at most200 query shapes, IDs never embedded as literals. Every success/failure closes cursor. Existing1171 guard/range semantics and histories preserved. Paired performance rollback returns1171 protected code; data retained. Apply/measurement pending; physical flow1172 predates query rewrite.
