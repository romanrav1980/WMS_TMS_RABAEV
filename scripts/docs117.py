from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
old="../2026-10-10_ni062_case_work/002_command.sql";new="../2026-10-10_ni062_case_closure/003_command.sql"
assert old in m["components"];m["components"]=[new if item==old else item for item in m["components"]]
for group,names in {"components":["002_helper.sql"],"startup_scripts":["001_schema.sql"],"additional_scripts":["004_case_guard.sql","005_fact_guard.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni062_case_closure/"+name
  if item not in m[group]:m[group].append(item)
if "RRL_STOCK_CASE_CLOSE" not in m["packages"]:m["packages"].append("RRL_STOCK_CASE_CLOSE")
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Завершение расследованного расхождения](database/retailcase_ni062_case_closure_20261010.md):117 APPLIED, original two findings/current independent KRO/CLOSEDv5/SAP pending/replay/no quantity, open obligations/foreign case denied.\n"+p.read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:117 original STORE_CASE_WORK extended CLOSE with assigned latest two findings/current independent warehouse KRO/version/terminal quantities/current ordinary policy; immutable closure/SAP pending, no goods. Original weight case CLOSEDv5 PASSe0d3bf83d4, missing findings/self actor/unresolved original excess/foreign review denied. Read board closure1/discrepancy backlog0 and actual dossier closure/return source flags. SQL156.796/28.838/22.619ms retain source PK/case-finding indexes/bounded history; inventory/delivery owner plans growing case lineage. Checkpoint428 original package retained."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_2.md","Ticket117: [завершение расследования](../../../../database/retailcase_ni062_case_closure_20261010.md), ordinary original full-quantity mass case/two findings/independent scoped KRO/CLOSEDv5/history/SAP pending/no quantity; unresolved quantities and marked flow cannot close."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_2.md","Ticket117 prerequisite: original ordinary case closure now appears in daily facts and removes case from current open register only after explicit independent root decision. Source ERP message remains pending; close day not inferred.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/retailcase_ni062_case_closure_20261010.md"]="""# NI06.2/NI07.2 — завершение расследования,117
2026-10-10-117-investigated-case-explicit-closure APPLIED14/0 plus current actor scope helper2/0 RABAEV/orcl. Checkpoint428 actual RRL_STOCK_STORE_CASE_CMD, new private RRL_STOCK_CASE_CLOSE and immutable RRL_STORE_CASE_CLOSURE/guards VALID. Existing STORE_CASE_WORK Root/versions/action/findings reused, no new case engine.

CLOSE requires ASSIGNED case/two assigned different investigator latest immutable findings, independent current warehouse-bound KRO/store_loss_confirm/reason+decision reference. All original quantity obligations already LOSS_CONFIRMED|CLOSED; closing never resolves open quantities implicitly or manufactures return/loss. Current marked policy or source physical codes refuses ordinary closure until exact regulatory/unit workflow. Current actor must active. Other manager/loss writes also now warehouse-bound; assigned investigator can work authorised case without manager warehouse scope.
Sorted Root case/finding/closure resources, current version/source recheck. One transaction action/closure/headerCLOSED+version/SAP pending. Original report/amounts/quantities unchanged, no warehouse goods event. Header guard allows only explicitCLOSE transition and preserves assigned people/deadline. Corrections after closure require future explicit reopening/appeal, no hidden edit.

Existing raw investigations page adds closing reason/reference and historical closure/return source. Case review/current warehouse scope enforced for manager andKRO. Dossier hardcoded false return flags replaced with actual approvals/historical warehouse receipts, not current available stock. Board daily closure count/current open case removal separate from pending ERP.

[Author case](../../scripts/ni062_case_closure_case.py) PASSe0d3bf83d4 on original STORE.WEIGHT:948fbd9a72:22c5dc5ec4/warehouse2378876: initial/no findings409, actual two users/findings, assigned investigator with KRO permission403, other warehouse case review403, original Bea case unresolved EXCESS blocks closure. Independent bound KRO closesv5; replay/history1/SAP1/goods0. All own actors retired.
Read-only board shows closure1/discrepancy0 while ERP pending grows; actual dossier stores original KRO:e0d3bf83d4 and source findings. Source full quantities/mass exception reviewed, no fresh goods fixture/repeated old posting.
SQL156.796/28.838/22.619ms: keep case/sourcePK/finding index and bounded history; inventory/delivery owner checks repeated large lineage. Independent acceptance/appeals/return/excess obligation resolution/marked lifecycle and day closing remain open.
"""
out["задания на проведения тестов/NI06.2/117_завершение_расследования.md"]="""# Qwen — NI06.2/NI07.2,117
Own existing ordinary mass discrepancy/full quantities, assigned different investigators/latest findings and current warehouse KRO. Missing findings/self actor/foreign warehouse/stale version/open quantity obligations/required marking deny.
Root close action/version+1/immutable closure/source findings/SAP event together, no quantity event. Repeat saved result afterCLOSED; another operation cannot silently reopen. Original documents preserved.
Dossier shows actual return approval/historical receipt versus current availability; board closure1/current backlog removal, externalERP pending distinct. Manager review and writes warehouse-bound, assigned investigator authorised scope retained.
Old original case e0d3bf83d4 closed; do not replay as fresh fixture. Live VALID/source/checkpoint/slow decision and independent evidence; marked/excess/appeals remain separate.
"""
print(json.dumps(out,ensure_ascii=True))
