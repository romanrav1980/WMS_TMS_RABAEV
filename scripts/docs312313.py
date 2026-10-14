from pathlib import Path
import json
out={};page="wiki/database/nicora_ni061_nested_onward_20261012.md"
out[page]="""# Межскладское второе плечо в физической матрёшке
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

Источники: [312](../../db/migrations/2026-10-12_ni061_nested_onward/apply.sql), [313](../../db/migrations/2026-10-12_ni061_nested_binding_scope/apply.sql), [actual store delivery](../../scripts/deliver312_nested.py), [[nicora_ni061_aggregation_scan_20261012]], [[nicora_ni041_fullpal_hu_shipping_20261010]].
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Матрёшка второго межскладского плеча](database/nicora_ni061_nested_onward_20261012.md):312–313 actualTOP/BOX/STOCK3/oneplace/LOAD-DEPART-STORE/customer3/sourceFF3once; scoped current bindings.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 312–313 APPLIED native existingHU shipping + onward scope/loading guards + actual departure and frozen nestedoneleaf STORE mark proof. Source310alreadyP3→TOP/BOX/leaf3→late rollback→actualLOAD/DEPART/STOREaccepted3, originalFF3once/samecodes/protected20/20. NativeallVALID; Source313indexes currentware/cell/historyexcluded, read3/9.781ms33buf. Departure cold2/60.227ms189buf: keep bounds/current indexes, projection rewrite owner inventory when expanded.\n"
p=Path("wiki/runbooks/nicora_active_work.md");t=p.read_text(encoding="utf-8").replace("Current native311/app311/serv311.","Current native313/app311/serv311.")
t+="\nLatest312–313 source310 now physicallydelivered/customeraccepted3, P0; TOP IH312 andBOX IB312 historicalSHIPPED/unlinkedarchive, oldstockleaf FULL source retainsphysicalkeys6codes/sourceFF3once. tmp/context312 complete. Source311 stillP3 receiving andcanformnext nested source withoutbirth. Do not rerun case312initial/native rollback assertions. deliver312exactrepeats safe. NativeallVALID/ledger312313APPLIED; UI unchanged311. Next receiving sourcewarehouse nested oneSTleaf with explicit physical-place vs stock-leaf keys and preservednewlinks; no fake use of predeparture unload.\n";out[p.as_posix()]=t
for name in["ni06_1","ni04_1"]:
 p=Path("wiki/requirements/nikora_delivery_v55/execution/active/"+name+".md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n312–313: existing TOP→BOX→onewhole onwardSTOCK3 actualLOAD/DEPART/STOREaccepted3, sourceFF3once/native rollback/replay; currentWARE-cell/historyexcluded. Warehouse nested first-leg receipt and multiST consolidation remain open. [[../../../../database/nicora_ni061_nested_onward_20261012]].\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));inc=next(x for x in j["increments"]if x["id"]=="NI06.1");inc.setdefault("implementedSlices",[]).append("312–313 whole onward STOCK leaf under nested physicalHU -> actualLOAD/DEPART/STOREaccepted3, originalFF3once; currentWARE-cell/history scoped binding")
inc["remainingScope"]=["warehouse nested first-leg receipt and physical tree reconstruction","multiple ST/stock leaves consolidated upper place","aggregation invalidation/repacking lifecycle","true recurrent physical-loss cycle","independent acceptance/hardware/current real ERP and government ACK"];out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/312_nested_onward.md").as_posix()]="# Qwen312–313\nContext312 alreadydelivered3: no source/prepare/initialload rerun. Existing repeatGET andsavedSTOREcommand safe. Fresh whole nestedTOP/BOX/oneSTOCK source onwardST: sourceWARE/currentbinding/targetTT/mass/slot/QC versions/native loading required. Native latefail rollsback P/UNIT/journal/outbox/links; exactretry returns savedresult. Parent/rootdifferent fromleaf mustnotblock legitimate departure/store, yet frozenarchive/leafUID/QTY/currentunit_signature required. Multiple onwardST ormultiple stockleaf explicitly fail beforeP. Foreignwarehouse and alreadydispatched historical binding excluded; test fresh repeatedUID source lookup positive/oldhistory absent. No fake second customerFF/legalACK, no predeparture-unload workaround at targetwarehouse.\n"
print(json.dumps(out))
