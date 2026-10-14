from pathlib import Path
import json
out={}
out["wiki/database/nicora_ni022_exact_pallet_share_20261011.md"]="""# Точная доля упаковки в прежней подготовке СТ
277 NI02.1/NI02.2. LegacyPreparation._pallet_rows прежде вычислял Decimal(quantity)/total и умножал округлённую долю на число упаковок. 24/72*3 могло дать 0.999999... и отклонить целую коробку. Новый domain/preparation_quantities использует Fraction, требует целое количество упаковок и точно представимую массу до9 знаков, без Float и округления исходного количества. Прежние ORDERS/паллета/строка/fulfillment/SAP preparation journal неизменны, второго splitter нет.

Фактически создан собственный источник72EA с прежним SKU QPOOL2e9b6614d9 и карточкой коробки24EA/10kg; исходное сообщение сохраняется. Три плановые паллеты по24EA/1коробке/10kg. Одна внешняя транзакция полного rollback и повтор сохранённого результата прошли; источник72 неизменён, защищённый P20/H20 сохранён. Половина коробки отвергается. tmp/context277.json хранит собственный источник/ответ; не повторять рождение fixture. Это не физический товар и не автоматическая укладка по габаритам.

SQL прежнего ADD_ORDER_ROW8.904ms/2, PALLET_ROWS_ADD4 2.796ms/6; решение владельца fulfillment/Oracle — сохранить прежние bounded writers, без нового индекса/кеша/увеличения timeout. Независимая проверка величин/непредставимой массы и реальной укладки остаётся в Qwen.
"""
for path,line in [
("wiki/index.md","- [Точная упаковка трети заказа](database/nicora_ni022_exact_pallet_share_20261011.md):277 исправлено округление1/3, прежняя подготовка дала3паллеты24EA/1box/10kg из72EA."),
("wiki/log.md","2026-10-11:277 exactFraction pallet share replaces context-roundedDecimal division in original preparation; integralpacks/exact9scale mass, no new splitter. Actualnewown72EA SAPsource -> original3plannedpallets24EA/1box/10kg; outerrollback/replay/source72/protected20-20. SQL8.904/2.796ms retainboundedwriters. Independent/automaticphysicalpacking not certified."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni02_1.md","11.10.2026:277 точная доля коробок/массы без округления1/3 в прежней подготовке; реальный собственный источник72EA ->3плановые паллеты24EA/1box/10kg, rollback/повтор/источник неизменён. Автоматическое восстановление старого splitter не заявлено."),
("wiki/runbooks/nicora_active_work.md","Latest277 app610: exact rational source pallet share, actual own source72 ->3original planning pallets24EA/1box/10kg in tmp/context277.json; noStock/P20H20. SQL8.904/2.796ms existingwriters retained. Native276/currenthistory shippedversion snapshot remains. Restart rootserv277 for current HTTP history UI/preparation. All18 independent/external/hardware acceptance remains pending.")
]:
 out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/runbooks/nicora_active_work.md");out[p.as_posix()]=out[p.as_posix()].replace("Native manifest275:","Native manifest276:").replace("App275/APIserv275b,","App277/APIserv277,")
out["wiki/index.md"]=out["wiki/index.md"].replace("current native276/app276/","current native276/app277/")
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI02.1").setdefault("implementedSlices",[]).append("277 exactFraction shares retain integral packages/9scale exactmass in existing ST preparation; actual72->3x24/1box/10kg")
out[str(p)]=json.dumps(j,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI02.1"/"277_exact_pallet_share.md")]="# Qwen277\nИсходный72EA/3box/30kg разделить3x24EA/1box/10kg; доля1/3 не отклоняет целое число. Halfbox12EA refused. Source72 and rawXML unchanged; existing writers/fulfillment/journal oneUOW/no stock. Nonfinite/zero/nonrepresentable9scale weight refused, rollback before published result. Exact replay oldlayout preserved. Author actual tmp/context277.json, independent run pending.\n"
print(json.dumps(out,ensure_ascii=True))
