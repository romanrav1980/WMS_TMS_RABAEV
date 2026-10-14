import json
from pathlib import Path
out={}
out["wiki/database/retailcase_ni081_candidate_scope_20261010.md"]="""# Маршрут кандидатов и режим действующего диапазона,160

Optional candidate_pick_route_id filters only newempty dynamicfaces to current activePUBLISHED route in samewarehouse. Demand/oldstock/oldrange remain wholeSKU/warehouse, explicit responsebasis/UI; no silent partialdemand fromroutefilter. Wrong/missing/foreign/nonpublishedroute404. Source/archive/recompute carries optionalroute, but omits None from oldcanonicaldraftrequest to preserve oldoperationreplay. Publishedoldhistory staysoriginal, changedsourcefacts requirefreshproposal.

Layout shows currentmappingmode/currentapprovaloperation/newreplenishmentallowed; old508DRAINING remains CASEactive/credit20/newrefillfalse, new519ACTIVE true. Closure/reopen history unchanged. RawUI routeinput, oldversusnewscope explanation, actor/WARE/article stalehistory clearing, pendingretry displays actualoriginalWARE/article. No newphysical effects, no subwarehouse-work filter claimed.

ActualHTTP146 scoped/unscoped equal quantityscenario44-old20→whole24, activeoldrange2/proposednew518→total3 untiloldrange drained. Nativecurrentphase508/519 correct, wrongroute999999999 rejected404. Originalcancelled RANGE157.SAVE2:52470cc7 oldno-route SAVE replay returnsoldDRAFT exact, currentGETcancelled, no metadata/stockmutations. P20H20 unchanged. Architecture513/0/79PASS/NodePASS.

SlowSQL initialscoped candidate112.326/131.195ms, layout31.991ms/3, routePK6.227ms/2. Inspected relevantliveindexes: noCELL-prefix on CASEline, FROM/TO-cell on warehouse tasks, TARGET-cell on repl tasks. Decision applied versioned2026-10-10_ni081_cell_commitment_indexes (4statements): CELL_CODE+CASE_TASK_ID; FROM_CELL+STATUS; TO_CELL+STATUS; TARGET_CELL_CODE+STATUS. Quantitycolumns notindexed, avoiding indexupdates on everypick. Also split optionalroute SQL predicate into fixed equalityonlywhenprovided, avoiding bindOR. Actualcase rerun unchanged. Live indexmetadata mirrored/currentmanifest/fullbundlegenerated, bounded101rowcandidate read retained. Not industrialcapacity proof; inventoryowner checkactualplan/cardinality onlargehistory beforetopology scaling, no globalstatistics sweep.

CurrentFixture old145undated expectation obsoleteafter158explicitowned orderdates; don't reset. NS59 ordinarydev rangeworkflow now includesproposal/approval/drain/scoping; NI08.1 resource recommendations andjoint stricttransport-driver-time admission remain next.
"""
p=Path("wiki/index.md");out[str(p)]="- [Маршрут кандидатов и режим диапазона](database/retailcase_ni081_candidate_scope_20261010.md):160 scoped newfaces/wholeSKU demand/currentdrain mode/oldreplay retained; cell-prefix commitment indexes.\n"+p.read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:160 candidatepublishedroute scope only/newlayoutmode/currentapproval, oldwarehouseSKUdemand unchanged. Actual146Scoped/unscoped same44-old20+24, wrongroute404, oldno-routeSAVEDRAFT replay retained/P20H20. Initialcandidate112/131ms prompted existingindexinspection and4cell-prefix commitmentindexes +fixedroutepredicate; actualcase unchanged/nativeindexesverified/currentmanifestgenerated. Architecture513/0/79PASS/nodePASS; industrialplan/cardinality backlogownerinventory.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nTicket160 scopedpublishedroute candidate read/currentdrainmode/historyoldcanonicalreplay andcell commitment indexes; see database/retailcase_ni081_candidate_scope_20261010.md. No subwarehousework or strictdriver/time admission claim.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":row.setdefault("implementedSlices",[]).append("160 candidate-route scope/currentdrainmode/oldreplay/cell commitment indexes")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/160_маршрут_кандидатов.md"]="""# Qwen —160
Routefilter onlynewemptyface candidates, notwarehouseSKU demand/oldstock/oldrange. Wrong/foreign/inactive/unpublishedroute404. Scoped/unscoped44-old20+whole24 unchanged current146. Mode508draining/newrefillfalse/519active true, oldmappingCASE/hard preserved. Source/archive/approval recomputation routepropagated; None omittedoldcanonicalrequest so original157SAVE2 no-route replay stilloldDRAFT whileGETcancelled. ChangedWARE/article/actor rawUI clearsstalehistory, pendingretry displaysoriginaltarget.
4cell-prefixindexes byactualmissingprefix evidence andfixedroutepredicate; noquantityindex/writeamp or globalstats sweep. Checkactualplan/cardinality largehistory independently, no loadcapacity claimed. Actor/scope/source staleness andpartial configrollback rules158 retain; no newphysicaleffects/P20H20. Do not rerun old145undatedfixture without declaredsource rollback.
"""
print(json.dumps(out,ensure_ascii=True))
