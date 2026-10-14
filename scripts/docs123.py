from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
item="../2026-10-10_ni061_final_delivery/001_hop_guard.sql"
if item not in m["additional_scripts"]:m["additional_scripts"].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/index.updated.tmp"]="- [Итоговая межскладская доставка исходному заказу](database/nicora_ni061_final_delivery_20261010.md):123 APPLIED, original shipped3 stays3/final accepted3/first-to-final lineage/no stock repeat, ordinary two-leg slice end-to-end; marked/nested/packing remain open.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:123 original1902 sourceFF64 remainedSHIPPED3/old source firstLOAD, intermediate119 receipt did not credit client; existing final STORE_RECEIPT:f94129cb2b on onwardLOAD:f755e2320c → accepted3/unreceived0/shipped3 only/no warehouse event/P0H0. Author actualreceiver/right/addressbinding/scans/replay/second denied; all assertions passed before Windows stdout-arrow failure; ASCII case restored and existing read continuation confirms PASSED. Bounded readonly receipt CTE retains original→final lineage; direct deliveries unchanged, unsupported multi-hop PLAN denied by newguard APPLIED4/0. Ordinary NI06.1 physical loop118..123 implemented dev; full marked/nested/packing/temperature/independent acceptance remainsopen. SQL31.178/34.825/10.082ms source unique/PK/requestbound200/receipt2000 retained, delivery owner larger original-lineage plan review."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md","Ticket123: [итоговая доставка](../../../../database/nicora_ni061_final_delivery_20261010.md); ordinary full standalone two-leg loop118..123 complete in author dev: first warehouse departure→second unload/receive/task→onward native ST/load/depart→store original accepted3/shipped3 only. Full sprint remains partial: marked/nested/consolidation/packing/temperature/partial discrepancy/independent acceptance not complete.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni06_1.md");s=out[p.as_posix()].replace("Статус: planned_delta","Статус: in_progress_bounded_ordinary_two_leg_dev")
out[p.as_posix()]=s
for rel in ["wiki/requirements/nikora_delivery_v55/implementation_plan.json","wiki/requirements/nikora_delivery_v55/sprints.json"]:
 p=Path(rel);m=json.loads(p.read_text(encoding="utf-8-sig"));m["currentSprint"]="NI04.3"
 if rel.endswith("implementation_plan.json"):
  m["currentStream"]="NI04"
  for item in m["increments"]:
   if item["id"]=="NI06.1":
    item["status"]="in_progress_bounded_ordinary_two_leg_dev"
    item["acceptanceStatus"]="author_dev_slices_118_123_not_full_sprint_acceptance"
    item["evidence"]="wiki/database/nicora_ni061_final_delivery_20261010.md"
    item["remainingScope"]=["marked and nested cargo","consolidation and packing","temperature and topology slot proofs","partial discrepancy and explicit ownership","independent acceptance and real external ACK"]
 out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["wiki/database/nicora_ni061_final_delivery_20261010.md"]="""# NI06.1 — итоговая доставка исходному заказу,123
Read projection reuses native STORE_RECEIPT and OrderDelivery. Schema guard migration2026-10-10-123-original-order-final-delivery-lineage APPLIED4/0 RABAEV/orcl; new RRL_INTERWARE_HOP_LIMIT_GUARDVALID. Further intermediate plan on an onward load denied until explicit multi-hop ownership is implemented; supported current chain is two shoulders.
OrderDelivery keeps original shipped legs/customer/source fulfillment, in one existing Oracle READ ONLY snapshot. Bounded requested original loads200→direct final loads or typed RRL_INTERWARE_ONWARD_DISPATCH second load→actual store receipt lines2000. Original quantity credit once by exact UID/SKU/BASE/whole source; first intermediate warehouse receipt never credited to customer. New receipt_lineage exposes original load/actual final load/receipt/UID, original fulfillment/stock journal unchanged.
Direct routes retained, no second projection writer/no extra customer order/fulfillment. Source warehouse originalFF64/1902 SHIPPED3 remains actualfirstLOAD, onwardST641316 has0FF. Quantity shipped still3, final accepted3/unreceived0 only after authenticated actual second-leg store receipt. Original document headerIMPORTED remains unchanged; status reports shipped-volume scope, no externalERP close inferred.
Author scripts/ni061_final_delivery_case.py: actual WAITING/unreceived3 before final, own final receiver/right/address policy+binding/BARCODE, badscan409, existing confirm/replay/second409, exact accepted3/original→final lineage/no goods/P0H0/customer64 unchanged. Original address is own legacy fixture explicitlyconfirmed122. All assertions passed before Windows stdout arrow UnicodeEncodeError; ASCII source restored after local editing error; scripts/ni061_final_delivery_existing_case.py confirms existing actual receipt INTERWARE.FINAL.RECEIPT:f94129cb2b. ActorQIFf94129cb2b retired. Do not rerun fresh one-time case; no new receipt needed.
SQL31.178/34.825/10.082ms retain source unique/PK and requested200/receipt2000 bounds; delivery owner checks growing two-leg lineage plans.
Ordinary full standalone physical loop118..123 complete in author dev: original first load→plan→actual unload0/receive3H0→existing task829/outbound3→custody release→existing onwardST/load3/P0H0→departure0→final accepted3. Full NI06.1 remains partial: marked/nested/consolidation/packing/temperature/partial discrepancy/slots/independent and actual equipment/external acknowledgment.
"""
out["задания на проведения тестов/NI06.1/123_итоговая_доставка.md"]="""# Qwen — NI06.1,123
Original fulfilled/shipped3 customer1902/sourceFF64/firstload unchanged. Intermediate warehouse119 receipt not clientaccepted. Existing final store/current exact addressbound receiver/policy/scan/immutable composition/replay/second deny → accepted3/unreceived0 while shipped still3; no stock event or customerFF duplication.
Readonly OrderDelivery same snapshot original legs/requested<=200/receipt<=2000, lineage maps first→secondactualLoad→finalReceipt. Direct deliveries retained; unsupported third shoulder mustdeny explicitmultihop guard. Marked/nested/sharedpartial/temperature separate.
Original finalf94129cb2b already accepted/software fixture; do not rerunfreshcase. Prior assertionssucceeded before stdoutencoding failure; continuationreadonly PASS plus originalAPI audit exact200. Verify live guard/source/SQLdecision, separateindependent evidence.
"""
print(json.dumps(out,ensure_ascii=True))
