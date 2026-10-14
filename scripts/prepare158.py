import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py");s=p.read_text(encoding="utf-8")
start=s.index('                cur.execute("""select count(*)')
end=s.index('        except ValueError',start)
section=s[start:end]
inner,outer=section.split('            sources=',1)
inner="\n".join(line[8:]if line.startswith("        ")else line for line in inner.splitlines())+"\n"
outer='            sources='+outer
outer="\n".join(line[4:]if line.startswith("    ")else line for line in outer.splitlines())+"\n"
helper='''    def snapshot(self,cur: Any,ware: int,article: str,start: date,end: date,forecast: Decimal|None,
                 forecast_unit: str|None,actor: str,pallet_weight: Decimal|None=None,
                 costs: list[dict[str,Any]]|None=None) -> dict[str,Any]:
'''+inner+outer+"\n"
s=s[:start]+'''                return self.snapshot(cur,ware,article,start,end,forecast,forecast_unit,actor,pallet_weight,costs)
'''+s[end:]
pos=s.index("    @staticmethod")
s=s[:pos]+helper+s[pos:]
out[str(p)]=s
out["wiki/database/nicora_ni081_range_apply_design_20261010.md"]="""# Slice158 — утверждение original range и вымывание

Next deliver native apply core delegated from original RRL_PICK_RANGE_PROPOSAL_API, preserving immutable operation journal. Three additive relations: immutableapproval(sourceproposal/operation+frozenproof), drain(originalPFA mapping/fromapproval), drainallow(originalrepl/task IDs+maxoriginalquantity), drainclose(originalPFA/operation), approvednewmapping relation. Deferred FK tooperation permits sameTX core effects before outerimmutable operation insertion/result, all rollback toownsavepoint. No stockquantity/second task engine.

Pythonapprover acquires existing stock_configuration_transaction onlyforpublish, reads originalDRAFTscope/request/source and recalculates samecursor SlottingDemand.snapshot afterexclusiveCONFIG, comparesoriginalsourceSignature. Native currentactor/WARE/right andCONFIG6, no cancel/priorapproval, exactsame source, SCENARIO_ONLY/undated0, complete nominalrecommendation, explicit operatorgeometry/compatibility inspection and reason. Never interpret DRAFT asapproval. Native rechecks candidateempty/P/H/CASE/task/dynamicassignment/currentpublishedsameWAREroute and originaltemplatecurrent. Assign using existing RRL_PICK_TOPOLOGY_API.assign_articul, clone originalextendednorms, verify RRL_STOCK_REPL_CAPACITY.unit_volume/budget + declaredgross vs currentMAX; alloneUOW.

Old originalmappings remain ACTIVE and CASEpickable. Snapshot existingopen repl IDs/QTY andordinary task IDs/demandlimits; nativecapacity uses new_target_allowed(cell,article,excludeRepl) so newreplenishmentbudget0, oldlistedcommitments allowed, no quantityincrease abovefrozen. Newrepl insertion/retarget/qty expansion guard; current old task completion preserved. Existing original resolve_pick_face selector/minimax preferapprovednewrange, but activeCASE/HARD/task targets not rewritten. Manualtransfer target semantics separate fromautomatedreplenishment; do not emulatequarantine byblockingentirecell.

Finishdrain onlycurrent P/H zero plusno unfinishedCASE/repl/tasks/actualplanningcommitment. Deactivate exactoldPFA throughoriginalnativeassign, recordimmutableclose; preservehistory. Originalproposal cancel mustrejectalreadyapproved. APIGET showscurrentapproval/drain state while oldoperationreplay stayshistorical. UIpending sameop/body/actor/API recovery, separate inspectedpublish action andemptydrainclose. No automaticbigloads/broadchecks.

Own fixtures: original508/PFA207/QGd9a5c53b54/SKU QNATIVED9A5C53B54/P20H20/unfinishedCASEwave395. Q157route146 emptyfaces518/519 noassignment. ACTIVE/ACTIVE2:52470cc7 drafts useforecast1 but undated20, cannotapprove ascomplete period. For positiveapproval either use explicitlyowned QA headers1920/1921 planneddate10Oct andforecasts21→old20+whole1 (documentsourcefixture advancement; old145 expectsundated wouldthenbeobsolete), or independentnewownedscenario; no realdata date inference. Newrevision mustnotquietly reuseoldDRAFT afterdateschange: expectedsourcehash stale refusal/newdraftrequired. ExistingPALLET_MULTIPLE1 is only QAnominal, actualstockwhole20 willstillbe rejected by smallface volume. Native volume publicunit_volume alreadyreuse.

RRL_STOCK_MATH.quantity(text,scale9) exists. RRL_PICK_TOPOLOGY_API.resolve_pick_face activeCASE+validdates thenpriority/order, lines351–357 currentbody; addpolicyonlyforfuturetargetselection preservingoldtaskIDrecords. Actualcurrentbody shouldbe captured asmaintainedcontract beforepatch, specinterfaceunchanged. Need inspectcase source admission consumers toensurefreeoldstock can stilldrain; do notclaimNS59complete ifall futureplanningexcludesoldstockwithoutdrainpath. Allmetadatawriters useCONFIG6, physicalcommandssameCONFIGshared fence; draft157 intentionallydoesnotlockphysicalstate. No externalSAPS/ACK orcanonicalwarehouseTZfabrication.
"""
print(json.dumps(out,ensure_ascii=True))
