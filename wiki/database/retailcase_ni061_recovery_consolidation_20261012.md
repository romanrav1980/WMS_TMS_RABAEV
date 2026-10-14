# Найденный товар в общем физическом месте
Миграция2026-10-12-367-recovery-consolidated-dispatch APPLIED RABAEV/orcl, all currentVALID. Переиспользованы recovery approval/receipt/placement, ST constructor/assignment, QC, HU_SHIP, departure и STORE receipt. Не добавлен второй shipment/fulfillment writer.

RRL_IW_RECOVERY_DISPATCH PK теперь OPERATION_ID+ST_ID; BIND_OPERATION_ID/RECOVERY_OPERATION_ID unique сохранены. Outbox EVENT_ID hash(operation+ST), поэтому несколько correctiveST одного HUcommand не теряют сообщения. Dispatch rowanchor по operation сохраняется: immutable writes только в одной native captured operation, никакого последующего update/delete. Source validators повторно проверяют eachwholeplacedreceipt/currentactor/WARE/trip/unitfingerprint и exact captured HU shipment binding.

HU compiler допускает recovery вместе с originalonward в bounded200 STOCK/CONTAINER tree, same existing whole leaf consumption/current perSKU UNIT matrices. Recovery guard принимает только captured LOAD_SHIPMENT/HU_SHIP в actual nativeTX; HUbranch сверяет resolved recovery ID+binding+ST отдельно, затем immutable bind/recovery/placement/source qty/UOM. Старое REQUIRE_COMMAND LOAD_SHIPMENT-only давало отказ на пробном HU load; исправлено explicit nativebranch, без снятия guards.

Actual source368:3old marked units/6codes shipped firstleg; accepted1, independentlyconfirmedloss2, found1+found1 by exact oldkeys/codes, three originaltasks placed1each. Existing custody/ST/assignment/QC -> oneTOP IH372:c7f60695a8/threeST. Trial373 twoexact recoverydispatch+oneoriginal/P0 then wholetransactionrollback restoredP1each/dispatch0. Actual373 thenDEPART374+STORE374: buyeraccepted3/unreceived0, originalFF3 once, history2-found2-net0, old6codes retained, protected P20/H20 unchanged. Context372 fully delivered; source368/found/initial373 factories forbidden. Replay complete originalcachedreceipts only.

Transport capacity still plans three logicalSTplaces; fixture ownvehicle PALLETS3, physicalloadoneTOP. Do not claim automatic planning capacity saving. No real governmentACK/hardwareproof.

SQL374 dispatch INSERT5.995ms/271buf fourexec; sourcebindlookup.198ms/83exec; constructorproof11.729ms/104buf; legacyFFread10.175ms; currentbound selection13.394ms. Inventory decision: retain STunique/bind/receipt indexes/200nodebound; batch source binding projection if grouped receiving grows, ownerinventory backlog. No million-op claim.

Remaining: firstleg groupedmultiSKU receiving preservingtop/group contract; repeatedphysical shortagecycle; aggregation-only recipient modes; real regulationACK/independent Qwen. Recoveryconsolidation is now covered, wholeNI06.1 not complete.
