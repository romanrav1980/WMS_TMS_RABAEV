# NI05.2: норматив тары физического TOP
14.10.2026 /1191. Установлено1192/1195/1197; actual1195 LOAD/1196 DEPART и current UI/read1198 подтверждены.

При заданных floor_variants машины проводка LOAD должна получать тип только верхнего физического места: CASE.PALLET_TYPE_ID или единственный HELD RRL_TARE_BOOK для HU в текущем складе. Внутренние CASE/BOX не умножают количество мест. Полная паллета STOCK без подтверждённого типа не получает тип по умолчанию: явный отказ.

Владелец — прежний RRL_STOCK_HU_LOAD_CORE и Root. Compile фиксирует тип/основание/версию профиля; assert_current выполняет повторное чтение под CFG shared, существующим vehicle/trip/dock ROW fence и до goods effect. Норматив совместимости общий RRL_VEHICLE_PROFILE_API.check_floor_capacity. У машины без floor_variants остаётся прежний PALLETS лимит.

Планируется additive immutable RRL_TT_LOAD_FLOOR_FACT,1строка на физический LOAD root, PK/FK→старый LOADfact, FKтип/vehicleprofile history. Это доказательство нормативного типа верхнего места, не новый товарный журнал. Запись после прежнего LOADfact в той же короткой Root TX; отдельный private-owner INSERT guard, UPDATE/DELETE запрещены. Исторические LOAD без доказательства не заполняются предположениями: при новой матрице остаются неподтверждёнными.

DEPART перепроверяет нынешнюю матрицу и типы всех LOADED root до статуса выезда; результат хранится в прежнем Root journal. Планировщик использует эти доказанные типы frozen LOADED places вместо числа дочерних CASE. Максимум200текущих LOAD/200типов; независимые машины параллельны, одна машина сериализуется существующим ROW20. Captured live sources/checkpoint и paired recovery в migrations2026-10-14_ni052_loading_floor. Dev RABAEV разрешён владельцем ранее.

1192: implementation prepared in captured core/depart owners and private physical-floor helper. Schema empty additive; paired rollback refuses to disable retained guard/facts and requires forward correction. Compile source excludes current load counts: concurrent independent roots on same vehicle can be rechecked against latest capacity rather than falsely marked stale. Before effect assert uses current matrix/type/book under CFG/vehicle fence; old untyped pending plan refuses new matrix. Application/physical result pending.

1197: final planning merges typed prepared places with selected immutable physical LOAD TOP proofs, once per LOAD operation rather than per ST/CASE; old LOADED without proof stays unknown. Bounded200ST/200physical TOP, loaded lookup uses bindIN. Application/typed read-through verification next; physical1195/1196 already passed on private33637, oneTOP/two nodes/3EA/outerrollback/replay/depart/no repeated stock.

## Результат1200

Actual33637/vehicle10100/profile2/3EA, oneTOP/two nodes/typeEU viaHELDbook; rollback/replay/load3.125/depart3.75/qty0/protectedP20H20. Nativeerrors[],704architecturePASS. [Report37](../../reports/retailcase/2026-10-13/37-physical-top-tare-report.md)/screens53–54. Positive physical flow preceded planner typed mapper; mapperbound read/unknown only afterinstall. Full STOCK-pallet type and fresh typed late-assignment remain gaps, no invented type. SQL2.988/7.014/oldtaresubtree14.893ms →retainboundedkeys/noindex (ownertransport/inventory).
