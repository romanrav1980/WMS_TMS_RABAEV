from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));base="../2026-10-12_ni061_ordinary_consolidation/"
for f in ["001_schema.sql","002_shipping.sql","003_next.sql","004_depart.sql","005_recompile.sql"]:
 if base+f not in m["additional_scripts"]:m["additional_scripts"].append(base+f)
m["startup_scripts"].append(base+"001_schema.sql")
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
page="wiki/database/nicora_ni061_ordinary_consolidation_20261012.md"
out[page]="""# Консолидация нескольких обычных межскладских СТ
327 APPLIED, actual328–332. Прежний верхний HU теперь отправляет несколько принятых немаркированных товарных паллет с собственными СТ. Никакой новый планировщик/таблица остатков/реестр HU не создан.

RRL_INTERWARE_ONWARD_DISPATCH primary key: OPERATION_ID + ST_ID; уникальность BIND_OPERATION_ID и RECEIPT_OPERATION_ID сохранена, все прежние строки сохранены. FK operation→Root сохранён. Для каждого СТ исходящее сообщение имеет отдельный operation+ST hash. Root закрывает все реальные ресурсы в общем порядке, затем проверяет состав и прежние QC, проводит существующий SHIPPING_CORE для каждой товарной паллеты, сохраняет один физический load/topplace и несколько immutable dispatch. Готовность выезда проверяет конкретный ROOT_UID/qty каждого receipt внутри общего архива; не требует единственного товарного листа.

Маркированная multi-leaf матрица и объединение recovery запрещены явно; CASE не разрешается этой новой веткой. Прежние одиночные маркированные HU продолжают работать. Для multi-ST доказанного немаркированного CONTAINER/STOCK дерева остаются прежние пределы200nodes/200allocations, exactwhole binding, currenttargettrip/WARE/cell/native locks.

Actual source328 и329 — разные исходные заказы/первые рейсы, по3EA; старые receipt/task/custody/конструкторСТ/назначение/QC, один целевой рейс, физический TOP с двумя STOCK. Actual331 один HU_SHIP: P0 двухпаллет, две dispatch строки/sixEA/две ST-membership/одно верхнее место. Поздний rollback вернул обеP3 и удалил оба dispatch. Повтор стабильный. Actual332 выезд и STORE приёмка: по3EA accepted у каждого исходного заказа/FF3once, protected20/20. tmp/context330.json включает весь сохранённый путь. Фабрики328329/initial331 не повторять: товар доставлен.

Тестовая машина имеет2 заявленных плановых места, actual нагрузка1TOP. Общая оценка транспортного плана до физической погрузки пока считает два логических СТ как2места; это отдельный backlog transport: учитывать доказанный текущий верхний HU перед assignment, не выдавать пустое/неполное предложение за физическую упаковку. Не заявлена экономия плановой вместимости.

324–326 также завершили отдельный source322 после atomic wholeHU replan: новое1HU задание→custodytop→secondleg→STORE3/old6codes. P0; context326 repeat safe, factories и initialP3 assertions forbidden.

Rollback327 отказывается при retained multi-ST dispatch history. Полная независимая/Qwen/оборудование/реальные внешниеACK ещё не выполнены. Следующий функционал: маркированные несколько товарных листьев с собственными матрицами и корректным распределением приёмки по товарным строкам.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Консолидация обычных межскладских СТ](database/nicora_ni061_ordinary_consolidation_20261012.md):327–332 twoST×3EA/oneTOP/twoimmutable dispatch/actualSTORE bothorders3; marked multi-leaf next.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 327–332 liveVALID: composite OP+ST dispatch PK preserves olduniques/FKs/history; perSToutbox IDs, exactleaf departure proof, markedmulti/recovery denied. Actual328329 receipts3+3/oldtasks/custody/ST/QC/oneTOP→331rollback+actualLOAD(two dispatch)→332STOREtwo originalordersaccepted3each/noFFrepeat/protected20/20. Source322 replan completion324–326 delivered3/P0. Transport planning physicalconsolidation counting retainedbacklogownertransport, fixturecapacity2/actualTOP1.\n"
p=Path("wiki/runbooks/nicora_active_work.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nCurrent332: native327 allVALID; actualordinary2ST/6EA/oneTOP delivery complete context330 includesSTOREbothorders3; source328329 source factories/initial331 forbidden. Source322 nowSTORE3/P0 context326; no initialP3 checks323324325. Next markedmulti-leaf matrices and receipt perSKU; no bypass currentgov/source/archivedproof.\n"
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n327–332: ordinary twoST×3EA received/placed/custody/packedoneTOP/LOAD/DEPART/STOREtwoorders3 each actualdev. Compositeimmutable dispatchOP+ST, separateoutboxIDs, oldFFonce. Markedmulti/recovery/firstlegmultiSKU/partialnested/independent remain. 324–326 wholeHUreplan completion delivered3.\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for x in m["increments"]:
 if x["id"]=="NI06.1":
  x["implementedSlices"].append("327–332 actual ordinary two onward ST3EA+3EA in one physicalTOP, exactcomposite dispatch/perSToutbox/late rollback/replay/DEPART/STORE both originalordersaccepted3once")
  x["remainingScope"]=[v.replace("multiple ST/stock leaves consolidated upper place","marked multiple ST/stock-leaf matrix; multi-SKU first-leg nested receipt; recovery consolidation")for v in x["remainingScope"]]
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/332_ordinary_consolidation.md").as_posix()]="# Qwen327–332\nДва исходных немаркированных3EA заказа/receipt/старыхtask/custody/ST/QC →oneTOP6EA. OP+ST PK и прежние bind/receiptuniques; twooutbox IDs; позднийfailsecondleg rollback обеP/журналы/load/links/outbox. BareHUship/foreignTT/missingQC/неполныйphysicalbinding/markedmulti/recovery denied. Actualcontext330 alreadySTOREaccepted3each: factories328329/initial331 forbidden. Existing delivery receipts не суммировать дважды в обоих заказах. Plannedfixturevehicle2logicalplaces vsactualTOP1 — нетclaim о физической экономии плановой capacity.\n"
print(json.dumps(out))
