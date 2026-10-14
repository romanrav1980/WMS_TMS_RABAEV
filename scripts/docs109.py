from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for i,item in enumerate(m["components"]):
 if "package rrl_stock_metadata_tx" in (p.parent/item).read_text(encoding="utf-8-sig").lower():
  m["components"][i]="../2026-10-10_ni062_supplier_handover/003_metadata.sql";break
else:raise RuntimeError("Missing metadata component")
for group,name in [("startup_scripts","001_schema.sql"),("additional_scripts","002_guards.sql")]:
 item="../2026-10-10_ni062_supplier_handover/"+name
 if item not in m[group]:m[group].append(item)
out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Документальная передача поставщику](database/nicora_ni062_supplier_handover_20261010.md):109 APPLIED, departed108/source/independent SC/replay/outbox1/no second P; manual evidence.\n"+p.read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:109 manual documentary supplier handover follows actual departed108, immutable reference/SHA256/receiver/reporting actor; independent bound SC confirmation plus SAP pending event atomic in existing metadata transaction. Own non-admin/replay/conflict/same actor403/independent/second409/no goods actual PASS. Metadata permission allowlist explicitly extended for dispatch/SC; stock context still unavailable. SQL105.020/58.964/52.576ms retain unique source indexes/queue100, NI06.2 owner reviews history plan at growth."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni06_2.md","Ticket109: [документальная передача](../../../../database/nicora_ni062_supplier_handover_20261010.md), immutable signed-document reference/hash/receiver plus independent SC confirmation/SAP pending; actual dev no second goods. External supplier authentication/actual archive evidence/SAP ACK not claimed."),
 ("wiki/requirements/nikora_delivery_v55/implementation_plan.md","10.10.2026:105–109 quantity tare loss/independent decisions/current holder debt and vehicle, complete-good BOX return24→configured picking, existing supplier ST/physical load1/departure/documentary handover delivered. Current NI06.2 ordinary disposal and marked lifecycle remain; full sprint acceptance not inferred from tickets.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"));m["currentSprint"]="NI06.2";m["firstChange"]="Existing supplier return/disposal/marked lifecycle; preserve original stock root and existing WMS/TMS";out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni062_supplier_handover_20261010.md"]="""# NI06.2 — документальная передача поставщику,109
Migration2026-10-10-109-supplier-documentary-handover APPLIED7/0 plus metadata allowlist2/0 in RABAEV/orcl. New immutable RRL_SUP_RETURN_HANDOVER/CONFIRM with unique dispatch/report source, document reference/SHA256/receiver, different actor independent SC. Existing CFG warehouse metadata transaction serializes with stock root; no effect context or goods mutation.

Actual load must be DEPARTED; report actor current warehouse-bound/warehouse_return_dispatch. Current different SC actor store_return_approve and same warehouse confirms; original doc/source preserved. Exact payload+actor hash replay, conflicts/second document or closure refused. Atomic confirmation/SUPPLIER_RETURN_HANDED_OVER in existing SAP outbox; pending, no external ACK. Archive reference/hash is operator-declared signed-document evidence, not automatic supplier authentication; actual hardware/external signed document not verified in dev. API typed port and supplier-handover.html provide durable retries and queue100. Partial/refused supplier receipt must not use full close.

[Author case](../../scripts/ni062_supplier_handover_case.py) PASS tag4f70ad3ea7 on original SUP.LOAD:f877bb1524/departed108: bound non-admin report/replay, changed recipient409, same actor confirmation403, independent admin SC/replay, second closure409, SAP pending1, P0H0/no goods event. Synthetic document hash explicitly dev fixture, never real external acceptance. Fixture actor retired. Earlier permission-denied attempt had no fact; existing metadata allowlist extended explicitly, not permission bypass.

Slow105.020/58.964/52.576ms: retain source unique indexes/warehouse bounded100; NI06.2 owner checks repeated growing history plan. New tables/guards/metadata package VALID. Independent acceptance/actual signed-document archive/marked/partial disputes remain separate.
"""
out["задания на проведения тестов/NI06.2/109_документальная_передача.md"]="""# Qwen — NI06.2,109
Use own actual departed supplier dispatch; committed108/109 sources are immutable history, do not repeat fresh closure on them.
Verify predeparture denied; current warehouse/right required; document reference/hash/receiver preserved; exact report replay/changed payload/second source denied.
Same reporting actor cannot independently confirm. Different current SC warehouse-bound actor confirms once; payload conflict/replay/second confirmation; atomic SAP pending1. P/H and goods journal unchanged. External ACK and external supplier login not implied by documentary registration.
Check VALID/current manifest/source and slow query decision. Mark synthetic documentary evidence honestly. Partial/refused supplier quantity must not be falsely closed.
"""
print(json.dumps(out,ensure_ascii=True))
