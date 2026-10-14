from pathlib import Path
import json
files={}
read=lambda p:Path(p).read_text(encoding="utf-8")
page="wiki/database/nicora_ni032_same_source_bindings_20261013.md"
files[page]=read(page)+"""
## Итог873–875

866/869/872 applied, ERRORS[]/INVALID[]. Fresh867 wave546/task1099 DONE20: two own source6/6→2/6 retain separate reservation identity; target original4+8=12, other8 preserved, next_rt=null. Root source and physical replay returned saved result. Own P/H cleaned through original commands. Failed earlier867 correctly rolled back before stock commit, not passed.

New related850 after872: two distinct sources20+12 delivered, original12/other8/third14, capacity refusal/exact replay/owncleanup. Context report873 retained separately; original report08 source1096/1097 remains historical and not overwritten. Current SQL projection13.588ms/125buf, requeue8.27ms/151buf, continuation2.677ms: bounded windows remain, ownerresources/inventory; noindex without slow evidence.

Marked/weighted branches and independent concurrency remain open. Removing count1 did not disable complete transfer/reservation/target equality guards.
"""
files["reports/nicora/2026-10-13/10-same-source-report.md"]="# Несколько резервов одной паллеты\n\n"+files[page].split("## Итог873–875",1)[1]
files["reports/nicora/2026-10-13/10-same-source-report.json"]=json.dumps({"same_source":json.loads(read("tmp/context867.json")),"related_two_arrivals":json.loads(read("tmp/context850.json"))},ensure_ascii=False,indent=2)
p="reports/nicora/2026-10-13/index.html";files[p]=read(p).replace("</main>",'<article><h2>10 · Несколько резервов одной паллеты</h2><p>Task1099 DONE20, два исходных резерва сохранены; лишнего продолжения нет.</p><a href="10-same-source-report.md">Отчёт №10</a> · <a href="10-same-source-report.json">Факты JSON</a></article></main>')
for name in ["shared_capacity","same_source_bindings","shared_bindings","shared_binding_closure"]:
 p="db/migrations/2026-10-13_ni032_"+name+"/checkpoint.json"
 c=json.loads(read(p));c["state"]="APPLIED";c["native_validation"]="USER_ERRORS empty; USER_OBJECTS current INVALID empty";c["developer_evidence"]="case867 wave546/task1099; related case850 wave547/two arrivals; own P/H cleaned";files[p]=json.dumps(c,indent=2)
p="wiki/index.md";files[p]="- [Checkpoint875: same-source доставка](database/nicora_ni032_same_source_bindings_20261013.md):866/869/872 VALID, actual1099 DONE20/no next/owner12+8; related20+12 PASS, report10.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint875:866/869/872 VALID, fresh867 sameUID two bindings and one whole20/task1099/own12-other8/no continuation/replay/cleanup; related850 distinct sources20+12 owners12/8/14 passed after change. Report10/checkpoint APPLIED; marked/weighted/independent acceptance still open. SQL bounded retention noindex.\n"
p="wiki/requirements/nikora_delivery_v55/implementation_plan.json";plan=json.loads(read(p));inc=next(x for x in plan["increments"]if x["id"]=="NI03.2");inc["implementedSlices"].append("866/869/872 retain same-stock separate owner bindings; shared admission sum vs need; exact expected target closure and whole incoming continuation; actual task1099 DONE20 owner12/other8/no next and related distinct20+12/replay/owncleanup")
inc["pendingSlices"][0]="Other physical split modes; marked/weighted and independent concurrent multi-continuation acceptance"
files[p]=json.dumps(plan,ensure_ascii=False,indent=2)
files["задания на проведения тестов/NI03.2/2026-10-13_shared_bindings.md"]="""# Независимые задания Qwen: общие физические источники

Не запускать старые factories/cleanup на защищённых источниках. Работать новым приватным warehouse/SKU и очищать только свои P/H штатным ядром. Не считать authored scripts независимым PASS.

1. Источник20, один заказ имеет два HARD6/6, другой8; target4. Rebind target4 оставляет отдельные2/6; одна whole подача20, заказ12/другой8 в target, никаких лишних physical tasks/continuation. IDs/versions не объединяются.
2. Два источника20/12, владельцы12/8/14 с частичным shared owner. Уменьшенная capacity отказывает без товарного эффекта; затем20+12 приходит один раз. Intermediate remaining может уменьшиться свободным target; проверять итоговый owner reserve.
3. Другой target/склад/завершённый CASE/чужой домен/суммарный source-owner резерв больше unmet need: refusal before effect. Guardsum не заменять отдельными comparisons каждой строки.
4. Маркированные physical units с несколькими профилями: не удваивать quantity; сохранить unit keys/code lineage/reservation owner. Weighted capacity отдельно.
5. Пара независимых соединений: source retry, physical task race и unrelated source параллельно. Один physical winner, exact replay, payload conflict, rollback; никаких fake DONE/ACK.
6. Проверить current WARE/actor, bound200, idempotent recovery API/terminal. Снять скриншоты и SQL decision в reports/nicora/2026-10-13.

Авторская evidence: migrations866/869/872, reports10; её не переписывать и не считать собственной независимой проверкой.
"""
print(json.dumps(files,ensure_ascii=True))
