# Приёмка физической матрёшки между складами
314 APPLIED в dev RABAEV/orcl, первый bounded slice один STOCK leaf внутри CONTAINER-only дерева200nodes/depth legacy16; одно исходное СТ и первое межскладское плечо. Multi-hop guard сохранён: source315 onward→третий склад был отклонён INTERWARE_MULTI_HOP_EXPLICIT_LINEAGE_REQUIRED; он не снят. Для actual314 использован новый firstleg SAPfixture316.

Schema: RRL_INTERWARE_PLAN nullable SOURCE_PLACE_UID и SOURCE_HU_JSON. ROOT_UID сохраняет товарный лист для прежних stock/unit/receipt/ownership механизмов; SOURCE_PLACE_UID отдельно обозначает физическое верхнее место. SOURCE_COMPOSITION_JSON остаётся точным исходным архивом load. Immutable header guard сверяет stockleaf/frozen load/currentepochs/зарезервированные unique newlink IDs. Старые flatplans используют NULL новых полей.

RRL_IW_HU_SOURCE предоставляет bounded readonlystock/sourcecontext и guarded metadata captureCFG6/current source dispatcher; context включает контейнеры и старые closed links, versions и новые IDs. Retained HU tare-book custody пока явно блокируется: другой owner должен провести её законный межскладской переход. Новый private RRL_IW_HU_REC_CORE только восстанавливает metadata/links, quantitywriter тот же Root/REC/BALANCE/UNIT. Whole receipt required; partial nested не заявлен поддержанным.

У фактической приёмки скан верхнего HU обязателен. Stockleaf barcode вместоверхнего HU отказан. Existing receipt3 updates SAMEphysicalunits/codes and stockleaf once, затем те же контейнеры получают receivingcell/nextversion и новые links. Старые source load/history/deactivated links сохраняются. Guards разрешают изменения только в native IN_FLIGHT exactsource/container/link plan с ordered row/HU anchors; прямое metadata изменение не легализовано. SAP/regulatory aggregates не подменяют warehouse hierarchy; externalACKfalse.

Actualsource316: ARTMAS/SUPPLY/SAPbirth3/6codes, original autoPUT/pick/ST, firstlegTOP→BOX→stock/LOAD/DEPART, guardedplan/sourcecapture; actual314 UNLOAD zeroquantity + RECEIPT3 by2aggregation scans. SamephysicalTOP/BOX IDs,2newlinks/currentWAREreceiving/P3H0/3oldunits6codes. Native late rollback removesstock/newlinks/containerlocation/receipt; exactHTTPretry stable. Protected20/20. tmp/context316.json and tmp/context314_received.json. НЕ повторять factory316/nativeinitial314.

Продолжение реализовано 317–319: это дерево размещено целиком, ответственность передана, второе плечо доставило магазину 3 EA; текущий запас P0. См. [[retailcase_ni061_nested_completion_20261012]]. Source315 remainsdeparted towardcustomer and cancomplete existingSTORE path; emptytestthirdwarehouse metadata hasno stock/sourceplan. Do not pretend itwasreceived.

Nativeobjects allVALID afterDDL/recompile/currentbody install. Runtime manifest/includes SQL represented. Rollback refuses retainednestedhistory; forward recovery needed ifphysicalreceipt exists. No DBcopy/new schema/instance.

Next: existing oneHU task placement, physical-place custody release, secondleg sameHU; multiST and multiSKU/partial nested, independenthardware/realERP/gov remain.
