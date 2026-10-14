# Межскладское второе плечо в физической матрёшке
Migrations2026-10-12-312-nested-onward-leaf и2026-10-12-313-nested-binding-scope APPLIED в dev RABAEV/orcl. Все изменённые объекты VALID; before sources/manifest и rollback сохранены.

## Реализация
Прежний RRL_STOCK_HU_SHIP_CMD теперь находит готовую межскладскую onward СТ и СТ найденного остатка среди физических товарных листьев. Использует прежние SHIPPING_CORE/NEXT/UNIT/balance/loading owners. Бounded slice: ровно одна onward СТ и один целый STOCK leaf внутри дерева CONTAINER; несколько СТ/товарных листьев явно отказаны до изменения запаса. Журналы пока имеют один dispatch на operation_id, поэтому multiST не маскируется как поддержанный.

NEXT и recoveryNEXT разрешают HU_SHIP только с точным текущим native loading.trip и совпадающей resolved binding/ST. Простое списание верхнего HU без фактической погрузки не становится межскладской отправкой. Immutable dispatch guards сверяют это доказательство; отдельный исполнитель остатков не появляется.

Существующий gate выезда сохраняет полную/частичную приёмку, подтверждённую недостачу, температуру и целевой рейс. Для верхнего HU дополнительно проверяет APPLIED HU_SHIP, actualdispatch samebinding/receipt/ST/rootleaf/quantity/base и ровно один STOCK leaf сохранённого load archive. Сравнение физического верхнего UID с товарным UID заменено проверкой происхождения листа, а не ослаблением готовности.

Приёмка магазином сохраняет прежний STORE_RECEIPT. RRL_STORE_MARK_CORE выбирает один STOCK leaf внутри CONTAINER-only дерева. issued_manifest требует точный неизменённый archive реального APPLIED HU_SHIP/LOAD_FACT и прежний physical_before.unit_signature. QR coverage/current profiles/dispositions/quantities проверяются старым механизмом; UNIT_OR_AGGREGATION разрешает QR штук. Warehouse HU и regulatory graph остаются разными сущностями.

313 ограничивает lookup текущими WARE_ID/SOURCE_CELL и исключает уже проведённые исторические binding. Индексы RRL_IW_ONWARD_HU_SOURCE_IX и RRL_IW_REC_HU_SOURCE_IX(WARE_ID,ROOT_UID,SOURCE_CELL,ST_ID), проверены VALID; иначе повторный оборот того же UID выбирал бы старую СТ.

## Фактический путь312
Использован уже принятый source310P3/3units/6codes, без новой birth. Прежний PUT task переместил всё в outbound, CUSTODY release, native constructor onwardST и старое назначение рейса. HU_CREATE/ATTACH сформировали TOP→BOX→STOCK3; масса и количество не удвоены. QC6 прежних QR. Native HUSHIP late rollback восстановил P3/H0 и2links, удалил load/dispatch. Actualload одна physicalplace/dispatch3, sameOP replay. Links деактивированы с историей, запас0. ActualDEPART и STOREaccepted3, exactreceipt replay; исходный FF SHIPPED3 один раз, buyeraccepted3/unreceived0, protected20H20. tmp/context312.json сохраняет все фазы.

Не запускать initialprepare/load assertions после доставки. deliver312_nested.py только сохранённые repeats/getter безопасен в нынешнем состоянии. Source310initialreceipt/родительский sourcefactory не повторять.

## SQL и пределы
Новый departureproof cold2exec/60.227ms/189buf; archived source proof5exec/9.233ms/56buf. Решение: bounded200promises/200nodes, current root/load PK и exactbinding; warm actual nextfixture измерить прежде чем расширять. Двойной JSON archive scan заменить single stock projection при измеренном росте; owner inventory, не расширять до multiSKU без этого. Scoped313 lookup3exec/9.781ms/33buf; новые current-source indexes сохранены. Реальная нагрузка/hardware/independent acceptance не заявлены выполненными.

Остаток: приёмка warehouse nestedHU другим складом и восстановление структуры, multiple ST/stock leaves consolidated upperplace, aggregation repacking lifecycle, реальная независимая/аппаратная/ERP-government acceptance.

Источники: [312](../../db/migrations/2026-10-12_ni061_nested_onward/apply.sql), [313](../../db/migrations/2026-10-12_ni061_nested_binding_scope/apply.sql), [actual store delivery](../../scripts/deliver312_nested.py), [[retailcase_ni061_aggregation_scan_20261012]], [[retailcase_ni041_fullpal_hu_shipping_20261010]].
