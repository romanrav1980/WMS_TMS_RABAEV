from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=["../2026-10-10_ni061_two_legs/003_metadata.sql" if x=="../2026-10-10_ni062_supplier_handover/003_metadata.sql" else x for x in m["components"]]
for group,name in [("startup_scripts","001_schema.sql"),("additional_scripts","002_guards.sql")]:
 item="../2026-10-10_ni061_two_legs/"+name
 if item not in m[group]:m[group].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki-raw/wms_admin_ui_reference/admin-nav.js");s=p.read_text(encoding="utf-8")
if "key: 'interwarehouse'" not in s:s=s.replace("  { key: 'supplier-handover'","  { key: 'interwarehouse', label: 'Межскладской поток', href: 'interwarehouse.html', icon: 'orders', permission: 'transport_dispatch_view' },\n  { key: 'supplier-handover'",1)
out[str(p)]=s
out["wiki/index.updated.tmp"]="- [Связь существующих межскладских плеч](database/retailcase_ni061_two_legs_20261010.md):118 APPLIED, actual departed standalone cargo/original ST/existing target TT/docks/deadlines/replay/no stock birth; physical receipt next.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:118 immutable interwarehouse plan on actual SINGLE.FULL.LOAD:9b15cf997d/source ST641280/TT33498/WARE10263663 to existing own TT33521/target9104, source-bound dispatcher/replay/conflict/second/foreign denied PASS ec6052b26e. No stock journal/birth/ST creation. Source first leg blocked from final store receipt. API/ARM durable intent and source/target queue; ordinary standalone scope only. SQL48.671/29.655/24.096ms retain source unique/target deadline index and100-row queue; inventory/transport owner monitors growing history. Checkpoint429 metadata retained; full NI06.1 still open."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md","Ticket118: [связь существующих плеч](../../../../database/retailcase_ni061_two_legs_20261010.md); ordinary standalone departed cargo/existing source ST and target trip, immutable deadlines/docks/source ownership. Physical unloading/receipt/onward fulfillment, nested and marked scope remain open.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/retailcase_ni061_two_legs_20261010.md"]="""# NI06.1 — связь существующих плеч,118
Migration2026-10-10-118-existing-trip-interwarehouse-plan APPLIED9/0 RABAEV/orcl. RRL_INTERWARE_PLAN/guards and metadataVALID; checkpoint429 actual metadata before118. Existing legacy assignment/load/TT/ST reused, no second planner.
Current source-bound transport_dispatch_edit; native warehouse CONFIG fence before sorted existing TT locks, source composition frozen via INSERT SELECT. Source actual DEPARTED/singleST/STOCK/FULLPAL/no store receipt/no current balance/current ordinary SKU policy/one leaf/no unique-unit composition. Target different warehouse/existing plannedTT/unblocked docks/ordered aware UTC arrival+ready deadlines. Original source immutable; unique source prevents two intermediate routes. Exact operation hash+saved result, conflict409.
Source first leg cannot be accepted as final store delivery. Plan is metadata, not physical custody or warehouse stock; no P/H/journal/customer demand duplication. Next119 separate actual unloading and native receiving. Marked/nested/multi-place must use future exact unit/tree flow, not fall through ordinary path.
Typed API /api/inventory/interwarehouse/plan and warehouses/{id}; raw interwarehouse page uses per-user/API durable intent and retry, current warehouse queue and both legs/docks/deadlines/pallet identifier.
Author case scripts/ni061_two_legs_case.py PASS ec6052b26e: source SINGLE.FULL.LOAD:9b15cf997d/UID FULL.QA:9b15cf997d/ST641280/TT33498/WARE10263663; target9104/existing ownTT33521/inbound QIIec6052b26e/outbound QIOec6052b26e. Current bound nonadmin/replay/conflict/second/foreign403, sourceP0H0/old member1/new goods0. Reporter retired; physical receipt not yet executed. Do not rerun fresh case on this already planned source.
SQL48.671/29.655/24.096ms retain source unique/target deadline index and100-row queue; inventory/transport owner assesses growing plans. Full NI06.1/customer onward ownership/temperature/packing/consolidation/marked/external acceptance remain open.
"""
out["задания на проведения тестов/NI06.1/118_существующие_плечи.md"]="""# Qwen — NI06.1,118
Use own ordinary standalone already departed cargo/one original ST and existing target planned TT. Current source dispatcher and target inbound/outbound docks, different warehouses/trips, ordered timezone deadlines. Plan no stock birth/no new ST/trip/customer fulfillment.
Replay identical saved result; changed payload409/second source plan409/foreign queue403. Loaded not departed/store accepted/current nonzero balance/required marks/nested CASE/HU/no exact composition deny. First-leg final store receipt denied after plan.
Verify Oracle guards/source/checkpoint/metadata CFG-before-sortedTT; queue bound100 and source-target visibility. Physical unloading/receipt separate next119. Existing ec6052b26e source already planned; use continuation, do not create same fixture twice. Record longest SQL and explicit decision, independent evidence separate from author case.
"""
print(json.dumps(out,ensure_ascii=True))
