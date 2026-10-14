from pathlib import Path
import json
out={}
page="wiki/database/retailcase_ni061_partial_redelivery_20261011.md"
out[page]="""# NI06.1/NI05.3 — доставка 1+1+1 после частичной находки (306)
306 переиспользует 301 existingTASK_COMPLETE, originalINTERWARE_CUSTODY_RELEASE/prepare_onward, 302 originalST constructor/assignments/recoveryNEXT и прежние QC/LOAD/DEPART/STORE. Нового quantitywriter/receiver/fulfillment нет. В основе [[retailcase_ni061_partial_recovery_20261011]].

Actual tmp/context305.json/context305_recovery.json/context306.json: initialaccepted1 +found1 +found1. Все3 паллеты выполненными складскими заданиями перенесены из quarantine receiving в прежнийoutbound. К каждой создана штатная СТ; первое onward использует существующий первичный targetTT, найденныечасти —2 новыхплановыхTT. Каждый whole1 прошёл originalQC двумя профилями, LOAD1→P0, DEPART, STORE1. Текущая покупательская проекция последовательно accepted1→2→3 и unreceived2→1→0. Историяloss2 и суммаfound2 не увеличивают accepted до реальной STOREприёмки. OriginalFFSHIPPED3 остаётся одной строкой, 3 finalreceipt lineages, aggregatephysicalqty3, birth3units/6QR сохраняются. Protected20/20.

Отдельный физический маршрут/производственный выезд/driverlegal/governmentACK этим dev-case не подтверждены. Выполнение автором не независимое ревью. Исходникиsource305 запрещено повторно запускать: это уже выполненные события, не новаязадача на входе. После отправок также нельзя повторять старыеP1/P2 assertioncases; точные записанные команды и текущие getter безопасны.

SQL305: scoped all-case reader18.661ms mean/5exec/313buffers total includescold; unitselection currentpath $.key1.941ms/9exec/63buf, exactcurrent unit selection6.031ms/8exec/95buf. Сохранены sparse LOSS+OP indexes и bounds1000 reports/10000physicalunits. Старый ошибочный '$' child не считается текущим планом. При росте истории JSON анти-join по заявленным units требует normalized active-claim projection: inventory owner, после измеренной большой selected-matrix; не утверждать million/day loadproof. Cancellation незавершённого report следующий отдельныйcommand, без удаленияистории.

Полная независимая/аппаратная приёмка NI06.1 и второй физический loss-cycle той же единицы ещё не закрыты. Nestedcargo/consolidation остаются самостоятельным остатком.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Доставка после частичной находки](database/retailcase_ni061_partial_redelivery_20261011.md):306 actual1+1+1 originaltasks/ST/QC/load/depart/STORE; buyer3/originalFF3once/three lineages.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 11.10.2026 306: actualinitial1+twofound1 existingtasks/threeST/QC/load/depart/STORE; buyer1→2→3/unreceived2→1→0/originalFF3once/old3units6codes/protected20-20. No new nativeowner. 305 scoped SQL18.661/1.941/6.031ms; boundedloss-index retained, normalizedclaims backlog ownedinventory; cancellationnext.\n"
for name in ["ni06_1.md","ni05_3.md"]:
 p=Path("wiki/requirements/retailcase_delivery_v55/execution/active")/name
 out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n306 [частичная повторная доставка](../../../../database/retailcase_ni061_partial_redelivery_20261011.md): actualinitial1+found1+found1 through existing task/ST/QC/LOAD/DEPART/STORE; buyer3/unreceived0/threefinal lineages/sourceFF3once. Pendingcancellation and truephysicalsecondcycle, nestedconsolidation/independent/hardware/external.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));inc=next(x for x in j["increments"]if x["id"]=="NI06.1");inc["status"]="in_progress_bounded_ordinary_marked_partial_recovery";inc.setdefault("implementedSlices",[]).append("306 actual initial1+twofound1 existingtasks/threeoriginalST/QC/LOAD/DEPART/STORE; buyer1->2->3/originalFF3once/three lineages")
inc["remainingScope"]=["nested and aggregation interwarehouse cargo","physical consolidation and packing into one upper place","cancel unrecovered approved/reported finding and true recurrent physical-loss cycle","independent acceptance/hardware/current real ERP and government ACK"]
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
p=Path("wiki/runbooks/retailcase_active_work.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nLatest306 existing source305 all3palletsTASKplaced→threeST/QC/load/depart/STORE done. tmp/context306.json buyer3/unreceived0/originalFF3once/history2-found2-net0, allpalletcurrentP0/3units6birthcodes. Serv306 current. Never rerun source/initialreceipt/placement assertions. Exactreplays/currentgetters only. Next cancellation307/newownfixture if needed; true physical recurrentloss/aggregation/consolidation remain.\n"
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI06.1/306_partial_redelivery.md").as_posix()]="""# Qwen306 actual 1+1+1 final delivery
Read wiki/database/retailcase_ni061_partial_redelivery_20261011.md/context305_recovery/context306. Allthree shipments/finalreceipts alreadydone; do not birth/retryinitialreceive/P1placementcases.
SavedOP/body repeats preserveoneevent/FF/lineage, changedbody rejects. Customer threeproven final1+1+1 ->accepted3/unreceived0/sourceFFSHIPPED3once/historyloss2/found2/net0. Before each finalreceipt no early credit. Sharedownerpartial stillrequiresallocation; foreignloss/duplicatefinal/excess quantity deny.
Verify old3keys/sixbirthQR hashes, native and directguards; currentWARE/auth/body fenceUI/pending, originalsourcehistory untouched. No independent/hardware/Gov/driverlegal loadproof claimed. Further cancellation and sameunit actualsecondcycle separate.
"""
print(json.dumps(out))
