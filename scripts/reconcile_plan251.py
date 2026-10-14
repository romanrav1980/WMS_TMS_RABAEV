from pathlib import Path
import json,re
out={}
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
j["planRevision"]=13
for ident,status,slices,evidence in[
 ("NI07.1","in_progress_bounded_finance",["111 existing warehouse normative cost/version/detailed recognition","112 original dual-role extra expense approval","113 actual immutable goods allocation","114 reversal/correction journals preserve original amounts","115 original durable financial SAP outbox and exact monetary semantics"],"wiki/database/nicora_ni071_outbox_20261010.md"),
 ("NI07.2","in_progress_current_reconciliation",["116 current consistent day-aware warehouse/ERP/P-H-unit report","117 original delivery-case closure reflected in daily/current backlog","119 existing interwarehouse unload/receipt facts and current backlog"],"wiki/components/nicora_ni072_reconciliation_20261010.md")
]:
 item=next(x for x in j["increments"]if x["id"]==ident)
 item["status"]=status;item["implementedSlices"]=list(dict.fromkeys(item.get("implementedSlices",[])+slices));item["evidence"]=evidence
 item["acceptanceStatus"]="author_bounded_cases_full_increment_independent_external_open"
for ident in["NI07","NI08"]:
 parent=next(x for x in j["sprints"]if x["id"]==ident)
 parent["status"]="in_progress_bounded_reuse"
 ids=parent["incrementIds"]
 parent["implementedSlices"]=list(dict.fromkeys(v for x in j["increments"]if x["id"]in ids for v in x.get("implementedSlices",[])))
 parent["progressNote"]="Initial planned status was stale; durable wiki/native functional slices are recorded. Full acceptance/remaining business scope stays open."
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.md");s=p.read_text(encoding="utf-8")
s,n=re.subn(r"\*\*Текущий — .*?\*\*","**Текущий — [NI08.1](execution/active/ni08_1.md), in_progress; зависимые доработки NI05.2 и сверки NI07.2 выполняются на существующих владельцах**",s,count=1)
assert n==1
out[str(p)]=s+"\n11.10.2026, редакция13 учёта исполнения: исправлены устаревшие planned статусы NI07/NI08 по уже существующим111–119 и133–250. Это сверка прогресса, без объявления всех сценариев принятыми или изменения18increments/363scenarios. JSON — актуальный currentSprint; старые начальные статусы в отдельных карточках остаются исторической датой создания, последующие ticket записи отражают выполнение.\n"
out["wiki/runbooks/nicora_active_work.md"]="""# NICORA: текущая работа
User priority is NICORA18 functional increments, not redoing completed TMS2 original17. Continue autonomously until all requested increments complete or12Oct202606:00MSK=03:00UTC. No GitHub publication without fresh explicit request. No subagents in this session. >=80% functional, targeted changed behavior only.
RABAEV/orcl127.0.0.1:1521 is dedicateddev; original single RRL_STOCK_POSTING_API quantity writer ACTIVE/compatibilityOFF. No new schema/instance/database copy. Quarantine is unavailable cells.
Current native manifest250. Latest new native changes248 original TT wall-time approval and correct new TT plannedstatus;250 same approval transaction current source-valid other vehicleORdriver envelope gate. Generated maintained bundle is not applied onACTIVE.
Current app251 loadingstatus oneREADONLY/current actor-Ware/all loadjournal proof. API rootserv.bat; frontendfront.bat; terminalterminal.bat. After native package spec/body migration restartAPI: ORA04068 stalepool otherwise requires sameID recovery. Never printsettings/passwords or serverstdout.
Plan JSON revision13/currentNI08.1; roadmap Markdown oldNI06.1 corrected. NI07/NI08 initialplanned status contradicted durable111–119/133+ wiki and is now boundedinprogress; independent/external/full acceptance remain. Driverrest/realroute/sharedwarehouse readiness still unfinished. Do not equate timezone approval with operational admission.
Read [[../database/nicora_ni081_time_resource_20261011]], [[../database/nicora_ni081_cross_zone_20261011]], [[../database/nicora_ni052_loading_read_20261011]], [[../components/nicora_ni072_reconciliation_20261010]] for next smallest sources. Latest actual cases250sameown33564/33567 future14Oct/no goods/peer cancelled; parentapprovedempty preserved. 251existing33558twoRootready/33541pending/WR234own33543 and foreign403/no writes.
Protected own WARE6667491/SKUQNATIVED9A5C53B54 P20/H20/wave395/CASE1031+1032 untouched. Existing own219 TT33541 still has pendingST, tare219return handoff held; don't fake cancellation/capacity. Old movementhistory never automatically summed/deleted for business acceptance.
"""
p=Path("wiki/index.md");out[str(p)]="- [Текущая работа NICORA](runbooks/nicora_active_work.md): onramp11Oct/current manifest250/app251/planrev13/next remaining functional scope.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n2026-10-11: reconciled stale parentNI07/NI08 and incrementsNI07.1/07.2 plannedstatuses against existing111–119/133–250 durable wiki/cases/native. Planrevision13/currentNI08.1 preserved18increments363scenarios/fullacceptanceopen; Markdown staleNI06.1 pointer corrected. Added current NICORAonramp at index start; no new business completion claimed.\n"
print(json.dumps(out,ensure_ascii=True))
