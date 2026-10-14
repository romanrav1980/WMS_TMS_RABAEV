import json
from pathlib import Path
out={}
entry="""\n551: corrected original GET /api/admin/transport/tariffs and /table-info to actual RRL_TRANSPORT_PRICE. Removed dead request models containing invented per-km/pallet columns and float rates. No guessed table selection, REGION/TRANSPORT_TYPE SQL, or successful error-row response. PRICE/PRICE_FOR_HOURS/PRICE_FOR_ADDR mean vehicle/hour/point; exact decimal strings, existing original PRICE_NAME key filter, type prefix/TYPE_TR filter, bound500. Existing native source tariff writer is not invoked.
Direct actual Oracle551: own original source1 price120/hour2/point5, exact filters, unknown region empty, published head3 unchanged. SQL551 5.746ms/38buffers and4.065ms/7buffers cold: retain bound500 and exact source/current tiny catalog; finance owner reviews ID/type/region indexes after duplicate/growth audit. No load/goods/financial journal change. Architecture657/0cycles/76debt PASS.
550 frontend TS PASS; UTF8 PASS; native USER_ERRORS/INVALID empty. Browser/reload and independent acceptance remain open. API restarted rootserv550 then catalog551 autoreload pending; final startup required before HTTP catalog reliance.
"""
p=Path("wiki/database/retailcase_ni071_transport_tariff_sources_20261012.md");out[str(p)]=p.read_text(encoding="utf-8")+entry
for name in ["wiki/database/retailcase_ni071_transport_norms_20261012.md","wiki/database/retailcase_ni053_unloading_facts_20261012.md"]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8").replace("Typecheck550 pending at documentation preparation","Typecheck550 PASS, UTF8 PASS, native errors/invalid empty")
p=Path("wiki/runbooks/retailcase_active_work.md");v=p.read_text(encoding="utf-8").replace("Final TS/encoding pending.","TS/UTF8 PASS; native errors/invalid empty.")
out[str(p)]="Checkpoint551: original transport tariff catalog fixed to actual vehicle/hour/point Oracle fields; read-only query PASS, head3/source120 unchanged, no invented table/columns/error rows. Architecture657 PASS. Next actual norm recognition and tare return disposition. API550 startup done before catalog modification, watcher may need rootserv restart. No full sprint completion/push.\n\n"+v
p=Path("wiki/index.md");v=p.read_text(encoding="utf-8").replace("checkpoint529–530, snapshot existing tariff/current version/period/currency/size/unload; apply pending.","native529/534 applied, versioned source snapshot/period/currency/size/unload;550 publication/history UI.")
out[str(p)]="- [Checkpoint551: действующий справочник тарифов](database/retailcase_ni071_transport_tariff_sources_20261012.md): vehicle/hour/point, точные строки, исправлен старый GET; architecture657 PASS,550 TS/UTF8/native VALID.\n"+v
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-12 checkpoint551: original tariff catalog corrected to real RRL_TRANSPORT_PRICE, dead float-based schemas removed; bounded exact read PASS/no writes, SQL5.746/4.065ms with retained bounds/index-growth backlog.550 TS/UTF8/native errors0 pass, architecture657 pass. Full sprint acceptance/publication remain open.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for item in m["increments"]:
 if item["id"]=="NI07.1":item["implementedSlices"].append("551 original tariff catalog fixed to actual vehicle/hour/point exact strings/PRICE_NAME/type filters, no guessed table/columns/error rows; original source120/head3 read only")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[str(root/"NI07.1/551_existing_tariff_catalog.md")]="""# Qwen: original carrier tariff catalog551
Prepared only. Review app/routers/transport_tariffs.py against actual Oracle column mirror and native existing source. GET only, existing transport_dispatch_view. Verify vehicle/hour/point exact decimal strings, null retained, exact PRICE_NAME key and type prefix filters, limit500, missing/error does not masquerade as a tariff row. No goods valuation, mutating price function, guessed per-km or pallet rate.
Own original ctx532 PRICE120/head3 must be retained, no fixture recreation/publication. Targeted actual direct read551 already performed; no full repeated regression or automatic additional model qualification.
"""
print(json.dumps(out))
