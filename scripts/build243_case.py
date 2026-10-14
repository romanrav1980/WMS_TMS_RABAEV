from pathlib import Path
import json
s=Path("scripts/case239_decision.py").read_text(encoding="utf-8").replace("context239.json","context243.json").replace("IW239","IW243").replace("QX239","QX243").replace("CONTEXT239","CONTEXT243").replace("PASS239","PASS243")
s=s.replace('"reason":"Own dispatcher defers original shipment to later existing trip"','"reason":"Own dispatcher defers original shipment to later existing trip","incident_kind":"MISSING_PALLET","incident_detail":"Own expected pallet absent at receiving check; reported, not a stock write","evidence_reference":"OWN243.ACT:"+tag')
s=s.replace(' q.execute("select count(*),sum(BASE_QTY)',''' history=h.get(base+"/api/inventory/interwarehouse/plans/"+ctx["plan"]+"/decisions");assert history.status_code==200,history.text
 records=history.json()["decisions"];assert len(records)==2 and records[1]["incident_kind"]=="MISSING_PALLET"and records[1]["evidence_reference"]=="OWN243.ACT:"+tag,records
 # Subsequent wait must not erase prior reported incident.
 later={**wait,"operation_id":"IW243.AFTER.WAIT:"+tag,"expected_revision":2}
 api("/api/inventory/interwarehouse/decisions",later)
 rows=h.get(base+f"/api/inventory/interwarehouse/warehouses/{ctx['target_ware']}").json()
 current=next(x for x in rows if x["operation_id"]==ctx["plan"])
 assert current["decision_revision"]==3 and current["decision_kind"]=="WAIT"and current["incident_kind"]=="MISSING_PALLET"and current["incident_operation_id"]==winner["operation_id"],current
 page=h.get(base+"/api/inventory/interwarehouse/plans/"+ctx["plan"]+"/decisions?after_revision=1").json()
 assert [x["revision_no"]for x in page["decisions"]]==[2,3]and page["next_after_revision"]is None and not page["has_more"],page
 from app.oracle_gateway import OracleGateway
 from app.modules.inventory.infrastructure.interwarehouse_decisions import InterwarehouseDecisions
 from app.modules.inventory.contracts_store_returns import StoreReturnReceiveError
 q.execute("select ID from RUSERS where ID like 'WR234%'and nvl(DELETED,0)=0 fetch first 1 row only");foreign=q.fetchone()[0]
 try:InterwarehouseDecisions(OracleGateway()).read(ctx["plan"],foreign);raise AssertionError("foreign incident history escaped")
 except StoreReturnReceiveError as exc:assert exc.status==403
 q.execute("select count(*),sum(BASE_QTY)''',1)
# The reused bind fixture stores both context and proof; no duplicate source.
s=s.replace('print("PASS243 WAIT/replay/conflict/DEFER/native rollback/concurrent revision winner/original plan immutable/current routing/both expected departure blocks/existing queue/no quantity/version/protected20/20")','print("PASS243 missing-pallet reported incident+new existing target in one immutable decision/native rollback/concurrent revision winner/replay/source unchanged/current expected gate still blocked/history-after-revision/foreign403/last incident survives WAIT/original3unitsISSUED7/P0/protected20-20")')
print(json.dumps({"scripts/case243_incident.py":s},ensure_ascii=True))
