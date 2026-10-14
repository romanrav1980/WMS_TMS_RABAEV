import json
from pathlib import Path
p=Path("scripts/check513_cost_period_projection.py");v=p.read_text(encoding="utf-8")
v=v.replace("class Cursor:","class Cursor:\n def setinputsizes(self,**kw):pass")
v=v.replace(" def fetchone(self):"," def fetchone(self):\n  if 'RRL_BOX_ASSEMBLY_READ'in self.sql:return ([dict(state='READY',business_date=d)for d in ['2026-10-11','2026-10-12','2026-10-12']],)")
out={str(p):v}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/assembly_period.py");v=p.read_text(encoding="utf-8")
a=v.index("        identities={}");b=v.index("        lines=[]",a)
v=v[:a]+v[b:];v=v.replace('            for clock in box_assembly_clocks(cursor,tree,ware,region):','''            nodes=tree.get("nodes",[])
            if not 1<=len(nodes)<=200 or len({n.get("uid")for n in nodes})!=len(nodes):
                raise LogisticsCostError("COST_FROZEN_TREE_BOUND","Нужен точный ограниченный архив")
            for clock in box_assembly_clocks(cursor,tree,ware,region):''')
v=v.replace('                lines.append({"load_operation_id":load,**clock})','''                lines.append({"load_operation_id":load,**clock})
                if len(lines)>10000:
                    raise LogisticsCostError("COST_BOX_BOUND","Не более 10000 физических коробок")''')
out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/infrastructure/box_costs.py");v=p.read_text(encoding="utf-8")
v=v.replace("                lines.extend(period_lines)","""                lines.extend(period_lines)
                if len(lines)>500:
                    raise LogisticsCostError("COST_DETAIL_BOUND","Не более 500 расчётных строк в одном проведении")""")
out[str(p)]=v
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name in ["RRL_HU_PACK_CLOCK","RRL_BOX_ASSEMBLY_READ"]:
 if name not in m["packages"]:m["packages"].append(name)
for name in ["../2026-10-12_ni071_cost_periods/apply.sql","../2026-10-12_ni041_box_packing_clock/apply.sql","../2026-10-12_ni071_box_assembly_source/apply.sql"]:
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/database/nicora_ni071_cost_periods_20261012.md");v=p.read_text(encoding="utf-8").replace("Статус: подготовлено, применение и авторский сценарий ещё не завершены.","Статус: применено в RABAEV/orcl; bounded author cases513/515/519/520 выполнены, полный спринт не закрыт.")
v+='''\n515: fresh measured CASE7/14 original codes, one dated BOX cost2.75; two concurrent operations one winner/one COST_ALREADY_CHARGED, exact replay. Original5 lines/13.50 unchanged. 519: actual ordinary BOX3EA packing →LOAD/DEPART →native date source →cost2.25. Source519 old scenario stopped after LOAD because status now requires actor; exact retained load resumed, no source recreated. Both source P0, protected20/20 unchanged.
513 projection: one source across two dates ->1×2.50 +2×3.00 =8.50, historical versions separate. This is not a physical two-day warehouse rehearsal.
518: authoritative readonly RRL_BOX_ASSEMBLY_READ used by preview, Python date partition and native guard; rejects changed start operation/version/instant/warehouse and unknown old BOX clock (520). Original CASE proof stays READY.
SQL521: native clock read6.653ms/51 buffers, source claim insert19.009ms/237, cycle latest0.322ms/7.27, exact cycle join1.691ms/18.11. Decision finance/inventory: keep current prefix PKs, 200 nodes/source/200 loads/500 dated rows and 10000 preview boxes; reject overflow before writes. Owner finance: batch clock resolution/partition verification if multi-box warm latency exceeds50ms; no redundant index without plan evidence. No throughput claim from single BOX.
Next: physical multi-date case, larger bounded loads and remaining transport/point/unload norm sources, real finance SAP agreement and independent acceptance.
'''
out[str(p)]=v
p=Path("wiki/database/nicora_ni041_box_packing_clock_20261012.md");v=p.read_text(encoding="utf-8").replace("Подготовлено516, применение и сценарий ожидаются.","Применено516/518, native VALID. 517: empty BOX no clock, first attachment/replay, fully empty/new attachment creates immutable cycle2; P5H2 unchanged before fixture cleanup. 519 actual original BOX3 goods/LOAD/DEPART/cost2.25, 520 forged clock and foreign warehouse denied.")
v+='\nComplete packing clock history is retained after test stock cleanup. ctx517/519 must not be reset; source519 is already departed/charged. Multiple-day physical scenario remains independent evidence pending.\n'
out[str(p)]=v
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"));m["planRevision"]=18
m["firstChange"]="NI07.1: actual ordinary BOX clock and dated source partition delivered512-520; continue remaining transport/point/unload cost norms with existing tariff owners; independent and real external acceptance remain."
for item in m["increments"]:
 if item["id"]=="NI07.1":
  item["status"]="in_progress_box_assembly_period_partition_delivered"
  item["implementedSlices"].append("512–520 actual CASE/ordinaryBOX shared native assembly authority; dated lines with single source claim; actual2.75 CASE and2.25 ordinaryBOX; concurrency/replay/legacy5 amounts13.50 preserved; two-date projection8.50 only")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.md");v=p.read_text(encoding="utf-8")
v=v.replace("**Revision 17, 12 октября 2026 года.**","**Revision 18, 12 октября 2026 года.**")
v+='\nRevision18 /512–520: NI07.1 ordinary BOX physical packing clock and separate actual assembly date rows delivered; one source claim preserves once-only charge. Actual new CASE2.75/BOX2.25 and immutable5 old lines13.50; two-date model8.50, physical multi-date rehearsal not claimed. Remaining transport/point/unload norms and real/independent acceptance stay open.\n'
out[str(p)]=v
for name,entry in [
("wiki/index.md","- [NI07.1 checkpoint522](database/nicora_ni071_cost_periods_20261012.md): actual CASE2.75/ordinaryBOX2.25, one source claim, shared native dates, historical5 lines13.50 preserved; planrevision18.\n"),
("wiki/log.md","\n12Oct512–522: dated finance lines/source claim and first scanned BOX packing clock/shared native readonly authority applied in RABAEV. Actual515 CASE2.75 one concurrent winner,519 ordinaryBOX3 goods LOAD/DEPART/cost2.25; old5 cost lines13.50 unchanged; 520 forged proof denied. NativeVALID/architecture650 PASS. SQL521 bounds retained, batch ownerfinance above50ms. Model two-date8.50 is not physical full-sprint acceptance. Publication authorized by latest user only after all sprints complete, exclude SAP material.\n"),
("wiki/requirements/nikora_delivery_v55/execution/active/ni07_1.md","\n512–520: ordinary BOX actual first packing clock/current immutable cycle and shared native CASE/BOX resolver; dated lines split one load with one source claim. Actual CASE2.75/concurrentwinner and BOX2.25 after DEPART/old5 lines13.50 unchanged; model2 dates8.50. Remaining physical multi-date/transport point unload norms and real/independent acceptance open.\n")]:
 p=Path(name);v=p.read_text(encoding="utf-8");out[str(p)]=entry+v if name=="wiki/index.md"else v+entry
p=Path("wiki/runbooks/nicora_active_work.md")
entry="""Checkpoint522: planrev18/native518/APIneeds final restart for shared resolver/architecture650. ctx515 measured CASE cost2.75; ctx519 actual ordinary BOX cost2.25/TT33622/WARE14526684/tagdc223cc37e fullydeparted, no source reruns; ctx517 BOX two cycles history retained. Legacy5 amounts13.50 preserved. Next transport/point/unload norm reuse sources and other remainingincrements. Shared native clock read CASE and BOX; physical two-date proof not yetdone, model513 only. Latest user authorizes full commit/GitHub AFTER all sprints; SAP sources still excluded. Do not stop at former06MSK deadline, continuation supersedes it.

"""
out[str(p)]=entry+p.read_text(encoding="utf-8")
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[str(root/"NI07.1/522_box_assembly_period_partition.md")]="""# NI07.1 /512–520: независимое задание Qwen
Read wiki/database/nicora_ni071_cost_periods_20261012.md and nicora_ni041_box_packing_clock_20261012.md first. Author cases are not independent acceptance.
Existing dev RABAEV only; no initial factories517/519/514 and no stock deletion. Protected20/20 unchanged.
1. Inspect native resolver and root-first BOX attachment: empty creation has no start; replay same operation retains clock; complete empty/repack starts new immutable cycle; partial changes preserve start.
2. Read ctx515/519 saved results; exact replay, original charge amount2.75/2.25 and historical5 rows13.50 unchanged. Another operation on same source cannot charge a different date.
3. In isolated fresh fixture demonstrate one LOAD with boxes from two genuine/specified assembly days and rates; separate dated quantity/amount, source total once, full rollback on one missing rate/unknown clock. Model513 is insufficient for this physical case.
4. Forge clock operation/version/instant/WARE, legacy unknown clock and missing CASE start: refuse without cost run/claim/lines/outbox. Current warehouse permission also checked before saved replay.
5. Invoice/trip summary separates dates/rate versions and currencies, decimal exact; source row keys include date, no duplicate UI row keys; parent carrier bill not overwritten.
6. Review actual longest SQL and decide batching/limits/index only from evidence. Hardware/external SAP ACK not inferred. Report PASS/FAIL/NOT_RUN by requirement with exact SQL/API facts.
"""
print(json.dumps(out))
