from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni061_dispatch_decision")
summary="""# NI06.1: решение диспетчера при задержке межскладского подвоза
239 APPLIED RABAEV/orcl. Append-only RRL_INTERWARE_DECISION keeps original plan, deadline, first shipment and unit manifest unchanged. WAIT preserves current target trip and ready deadline, records prospective expected arrival/reason/reference. DEFER selects different EXISTING planned trip in receiving warehouse, before physical warehouse receipt only; warehouse-task rerouting after receipt remains a separate unimplemented case. Revision optimistic check, canonical operation hash/replay, native current active actor/transport_dispatch_edit/target WARE before cached result and after sorted old/new TT locks. Metadata uses original CONFIG exclusive fence, stock owners keep shared fence; no metadata quantity writer.
RRL_INTERWARE_ROUTING resolves current trip/dock/ready deadline from latest immutable decision; original ARRIVAL_DUE and original ready deadline remain visible. Existing receiving/putaway/onward ST constructor and bind guard consume effective route. Dedicated typed API and existing raw screen preserve durable operation intent; current snapshot supplies expected_revision. Original stock root and all previous assignment/QC/load/departure checks retained.
Departure now freezes incoming promises and rejects any expected interwarehouse plan not physically loaded through its original receipt/onward ST/current active LOADED fact/APPLIED root. Rechecks after existing native vehicle/trip/dock locks. Unloaded/received/placed/QC-only is not departure clearance. Gate query starts indexed candidate original target trip UNION indexed decision target trips and resolves only candidates, bounded200; no per-row resolver across global plan table.
Actual own source09f6017c2a: sourceST641373/TT33549/FULL.QA:09f6017c2a/3 original units/6 QR. Original target33550/dockQO225 retained. WAIT revision1/replay/payload conflict, DEFER concurrent one winner revision2 to33551/dockQX239, native rollback no decision; both expected target departures blocked before cargo. Existing queue current route and original route visible. Existing receive3/PUTAWAY961/native completion/custody release/ST641375/original assignment/QC6/load/depart33551 succeeds after real loading. Same original keys/birth/codes, source stock0/units3 ISSUED10, no second customer fulfillment. Native foreign actor replay refused before saved result; protected6667491 P20H20. Native admin task completion is development evidence, not independent terminal qualification.
Quality239:24 cases/both TypeScript checks/561 files/0 cycles/76 debt, JS syntax pass. Actual cold queue463.898ms/1, candidate departure8.031ms/3, route lookup0.873ms/19, append20.388ms/3. Keep explicit trip indexes and bounded source; NI06.1 owner profiles latest-revision joins and warehouse OR/anti-join at sustained queue volume before throughput acceptance. No external ACK or full sprint completion claim. Nested/consolidation/temperature/after-receipt rerouting/partial interwarehouse discrepancy remain.
Initial root server restart was still starting when source helper contacted HTTP; connection refusal before stock birth, metadata fixture left unconsumed, no warehouse copy/reset. Confirmed API readiness then fresh own source above; original source helper context230 retained. Current installed bundle generated only.
"""
out["wiki/database/retailcase_ni061_dispatch_decision_20261011.md"]=summary
out[str(f/"010_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-239-interwarehouse-dispatcher-delay-decision'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Immutable dispatcher WAIT-DEFER over original interwarehouse owners and expected cargo departure gate',sysdate,user,'db/migrations/2026-10-11_ni061_dispatch_decision/apply.sql','db/migrations/2026-10-11_ni061_dispatch_decision/rollback.sql','APPLIED','Own source09f6017c2a original33550 preserved/current33551/WAIT1-DEFER2/concurrent one winner/native rollback/current scope; receive3/PUTAWAY961/ST641375/QC6/physical loading/departure success. Original3 units/code6/protected20-20; allVALID/quality239. Partial dev scope, no external ACK.');
commit;
"""
names=["001_schema.sql","002_routing.sql","003_guard.sql","004_depart_gate.sql","005_depart.sql","006_receiving.sql","007_placement.sql","008_onward_guard.sql","009_candidate_indexes.sql","010_ledger.sql"]
out[str(f/"apply.sql")]="".join("@@"+x+"\n"for x in names)
out[str(f/"verify.sql")]="""select name,type,line,text from user_errors where name not like 'BIN$%';
select operation_id,plan_operation_id,revision_no,decision_kind,previous_tt_id,target_tt_id from RRL_INTERWARE_DECISION where PLAN_OPERATION_ID='IW225.PLAN:09f6017c2a'order by revision_no;
select TARGET_TT_ID,RRL_INTERWARE_ROUTING.target_trip(OPERATION_ID) CURRENT_TARGET from RRL_INTERWARE_PLAN where OPERATION_ID='IW225.PLAN:09f6017c2a';
select STATUS from RRL_TT_HU_LOAD_FACT where TT_ID=33551;
"""
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_INTERWARE_DECISION;if n>0 then raise_application_error(-20990,'DISPATCH_DECISION_FACTS_EXIST_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_rrl_stock_trip_depart_cmd.sql
@@000_before_rrl_stock_interware_rec.sql
@@000_before_rrl_stock_interware_put.sql
@@000_before_rrl_interware_onward_bind_guard.sql
drop trigger RRL_INTERWARE_DECISION_GUARD;
drop package RRL_INTERWARE_DEPART_GATE;
drop package RRL_INTERWARE_ROUTING;
drop table RRL_INTERWARE_DECISION;
drop index RRL_IW_PLAN_TARGET_I;
"""
out[str(f/"README.md")]=summary
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));prefix="../"+f.name+"/"
for pkg,name in[("RRL_INTERWARE_ROUTING","002_routing.sql"),("RRL_INTERWARE_DEPART_GATE","004_depart_gate.sql"),("RRL_STOCK_TRIP_DEPART_CMD","005_depart.sql"),("RRL_STOCK_INTERWARE_REC","006_receiving.sql"),("RRL_STOCK_INTERWARE_PUT","007_placement.sql")]:
 matches=[x for x in m["components"]if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+pkg+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
 m["components"]=[x for x in m["components"]if x not in matches]+[prefix+name]
 if pkg not in m["packages"]:m["packages"].append(pkg)
m["startup_scripts"].append(prefix+"001_schema.sql")
m["additional_scripts"]+=[prefix+"003_guard.sql",prefix+"008_onward_guard.sql",prefix+"009_candidate_indexes.sql"]
# Remove older canonical onward guard source only, preserve other guards.
m["additional_scripts"]=[x for x in m["additional_scripts"]if x==prefix+"008_onward_guard.sql"or not re.search(r"create\s+or\s+replace\s+trigger\s+RRL_INTERWARE_ONWARD_BIND_GUARD\b",(p.parent/x).read_text(encoding="utf-8"),re.I)]
out[str(p)]=json.dumps(m,indent=2)+"\n"
for path,line in[("wiki/index.md","- [Решение по задержанному подвозу](database/retailcase_ni061_dispatch_decision_20261011.md):239 immutable WAIT-DEFER/current33551/original33550/expected cargo gate/old961-ST641375-QC-load-depart/same3units6codes."),("wiki/log.md","2026-10-11:239 dispatcher WAIT1-DEFER2 immutable metadata over original plan/current target scope/canonical replay/revision concurrent winner/rollback. Expected incoming cargo blocks native departure until original receipt-onward active physical LOADED APPLIED fact; sorted TT locks/current closure. Indexed candidate union avoids resolver global scan/bound200. Own09f6017c2a original33550 retained/current33551; receive3/961/ST641375/QC6/load/depart/same3units6codes/protected20-20. Quality24/bothTS561cycles0debt76/nativeVALID. SQL8.031/0.873/20.388ms,cold queue463.898ms keep bounds/indexes/profile latest-WARE-anti-join at volume. After-receipt/nested/temperature/partial acceptance pending; no full sprint or externalACK claim."),("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md","11.10.2026:239 WAIT/DEFER before warehouse receipt implemented; original33550/current33551/expected incoming departure refusal before actual loading; old receive3/task961/ST641375/QC6/load/depart/same codes. Metadata revision/replay/current WARE/native rollback/concurrent winner; after-receipt task reroute/consolidation/nested/temperature/partial discrepancy remain.")]:
 p2=Path(path);out[path]=p2.read_text(encoding="utf-8")+"\n"+line+"\n"
p2=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p2.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("239 immutable dispatcher WAIT-DEFER/current route/expected incoming native departure gate/old receive-putaway-onward-QC-load-depart/original3units6codes");j["firstChange"]="Implement remaining NI06.1 physical discrepancy and task reroute through existing receiving and warehouse task owners; do not replace old TMS assignment.";out[str(p2)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"));out[str(root/"NI06.1"/"239_dispatch_decision.md")]="# Qwen:239 — решение диспетчера по задержке\nНезависимо проверить immutable WAIT-DEFER/current actor-right-WARE before replay and after lock; expected_revision concurrent one winner/rollback/same ID payload conflict. WAIT preserves deadline/trip; DEFER before receipt only/existing planned target warehouse trip. Existing receiver-putaway-onward use effective route, original plan and first shipment retained. Native depart refuses promised but unloaded/unreceived/placed/QC-only cargo; succeeds only original active LOADED APPLIED fact, frozen closure/current recheck/config fence/sorted TT locks. Case09f6017c2a old33550/new33551/961/ST641375/3units6codes author evidence; no fake terminal or independent acceptance. Review slow queue/latest revision/WARE OR/anti-join; bounded candidate union200/indexes. No second stock or fulfillment/provider ACK.\n"
print(json.dumps(out,ensure_ascii=True))
