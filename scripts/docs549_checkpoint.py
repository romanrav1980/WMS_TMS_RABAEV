import json
from pathlib import Path
out={}
p=Path("wiki/database/nicora_ni071_transport_norms_20261012.md");v=p.read_text(encoding="utf-8")
v=v.replace("Подготовлено529–530, применение ожидается.","Применено529/534 в RABAEV/orcl, native VALID; author532/535/538 выполнены.")
v+='''\nTyped API: POST /api/finance/logistics-costs/transport-norms and bounded descending keyset GET /warehouses/{ware}/transport-norms/{price}/history. Finance publishes the CURRENT legacy row under lock; request is an instruction to snapshot that row, not an amount edit. No future source-row PRICE change or arbitrary candidate selection is performed.
532 own legacy rowID1/company OWN.NORM532.7a... (exact context532), no existing driver's company changed. Snapshot100/point5/hour2, loader3/rolling1.5/manual2.25; native late rollback/head0 removed, concurrent sameOP one version, changed body rejected. Original100 stays after source120/version2.
535 current bound non-admin creates version3 of same isolated norm, then wrong WARE/deleted actor replay403; actorQN535 retired. Original admin operation remains100/version1 after later versions.
538 HTTP saved publication and limit1 keyset history pass; native all VALID. Source selector536 now exposes published metadata from a single join, existing billing UI reads lazily per trip/warehouse; latest published snapshot rates shown separately from current source row. No normative transport charge claimed.
SQL538 history23.154/18.211ms cold53/66 buffers, saved-op1.691ms/5, latest-date8.029ms/31. Decision finance: retain current PK/OPID unique/date-version index, history<=100/current warehouse; exact source single-row locks/publication rare. Original PRICE table currently1 isolated row; source ID index/unique migration only after duplicate audit and measured growth, no arbitrary rownum1.
Next actual unloading consumption/vehicle class and once-only monetary recognition, ERP agreement/independent acceptance. Publication is not receipt or stock effect.
'''
out[str(p)]=v
p=Path("wiki/database/nicora_ni053_unloading_facts_20261012.md");v=p.read_text(encoding="utf-8")
v=v.replace("Checkpoint539 prepared, application pending.","Применено539/544, native VALID; author543/545/547 выполнены.")
v+='''\n540–542 typed start/read and optional existing receipt details; preview reads original receipt and unload facts in one consistent snapshot. Existing receiver UI includes system start/current details/durable exact start intent, credentials are not persisted. In-flight references guard duplicate clicks; pending keys preserve exact actor identity, not lowercased aliases. AdminTS/architecture655 pass; actual browser/scanner not yet claimed.
543 retained load FULL.HU.SHIP:dc223cc37e/TT33622/WARE14526684 →UNLOAD543.START and STORE543. Customer3 accepted once/manual/no loader, missing finish and forged ROLL_CAGE reject, original P0/protected20/20, goods events0. No source recreated. Start545 participates in outer rollback; dedicated metadata transaction must begin clean per original stock lock owner.
546–547 daily starts/completions attributed to START day, backlog unfinished starts blocks close; real source543 start1/completed1/open0. Receiver reference is attestation only, no camera/hardware/legal verification claim.
SQL547 initially77.496ms/34.5 buffers completed-start-day count, dynamic sampling on fresh tiny tables.548 gathered only new start/fact table stats; same cursor average51.729 over3 vs77.496 over2 =>last execution about0.195ms, other counts about0.19–0.23ms. Decision finance: retain PK/source indexes and bounded daily window now; before >1000 starts, add time/WARE access path and inspect actual plan (ownerfinance/inventory), no throughput claim from one start. Open-work query ownerfinance: materialise active starts only if historical scan growth measured.
Next current-actor/role UI reload confirmation, difficult rolling loader source, financial recognition and large-day/window evidence. Full sprint is open.
'''
out[str(p)]=v
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"));m["planRevision"]=19
m["firstChange"]="Continue remaining deltas: published existing transport norms and real unloading facts delivered529–548; next actual transport norm recognition and NI06.3 real tare cycles; no claimed full external/independent acceptance."
for item in m["increments"]:
 if item["id"]=="NI07.1":
  item["implementedSlices"].append("529–538 exact existing tariff immutable currency/period/type/size/unload norms; native locks current actor/grant/source/head, version publication/concurrent replay/snapshots100->120 and lazy billing source UI; money recognition remains")
 if item["id"]=="NI05.3":
  item["implementedSlices"].append("539–545 system unloading start/actual method-difficulty-loader atomically finished by original STORE_RECEIPT; retainedBOX3 actual customer3/manual/no-loader, rollback/replay/forgedroller denied; receiver attestation not hardware proof")
 if item["id"]=="NI07.2":
  item["implementedSlices"].append("546–548 unloading daily start/finish by operational start day and current open-unload blocker, actualstart1/done1/open0; targeted new-table stats remove dynamic sampling overhead")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.md");v=p.read_text(encoding="utf-8")
v=v.replace("**Revision 18, 12 октября 2026 года.**","**Revision 19, 12 октября 2026 года.**")
v=v.replace("| NI07.1 | Same-last-period norm revisions/native date-version choice; BOX1 charge3/v2 frozen; exact scoped invoice/trip grouping | Ordinary BOX assembly clock, multiple assembly days inside one load, remaining norms/real financial ERP |",
            "| NI07.1 | Actual CASE/BOX clocks, dated source partition and one claim; immutable rate revisions; published existing transport tariff norms/current scoped billing sources | Transport monetary recognition, physical mixed-day rehearsal, remaining vehicle/unload grounds and real financial ERP |")
old="Следующее функциональное действие: NI07.1 — достоверный источник сборки ordinary BOX, затем несколько расчётных дат CASE в одном load с единственным начислением источника; до реализации такой mixed load расчёт явно отказывается."
v=v.replace(old,"Следующее функциональное действие: NI07.1 — фактическое признание транспортных норм по машинам/точкам/выгрузке на неизменяемых источниках. Ordinary BOX clock и разделение по датам реализованы512–520; физический mixed-day rehearsal остаётся открытым.")
v+='\nRevision19 /529–548: existing tariff publication with immutable period/currency/type/size/unload rates; actual system unload start →original STORE543 customer3/manual/no-loader, start-day reconciliation1/1/open0. Metadata publication does not claim monetary recognition. Next NI07.1 transport charges and NI06.3 actual tare cycles. All18 acceptance remains incomplete; GitHub authorized only after completion, SAP excluded.\n'
out[str(p)]=v
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name in ["RRL_TRANSPORT_NORM_API","RRL_STORE_UNLOAD_API","RRL_STORE_UNLOAD_CORE"]:
 if name not in m["packages"]:m["packages"].append(name)
for name in ["../2026-10-12_ni071_transport_norms/apply.sql","../2026-10-12_ni053_unloading_facts/apply.sql"]:
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
out[str(p)]=json.dumps(m,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[str(root/"NI07.1/549_transport_norms.md")]="""# Qwen NI07.1 /529–538
Read wiki/database/nicora_ni071_transport_norms_20261012.md; source row, head/history, current RUSERS/RIGHTS/source lock order and native body.
No source factory532 or actor535 rerun. Isolated rowID1 is private OWN.NORM532 company, current norm3, history100/120/120. Saved original admin request returns100/v1, wrong payload/WARE/deleted actor denied; no stock or carrier-price writes.
Independently review source exactness/duplicate ID refusal, publication while legacy edit waits, sameOP and distinctOP contention, rollback/savepoint preserving original history, keyset UI/history scopes. Published source is CURRENT row under lock, not client-entered money. Do not equate publication to financial recognition.
Report real API/SQL/state and longest SQL decision. Physical vehicle classification, actual costs and real ERP are pending tickets.
"""
out[str(root/"NI05.3/549_unloading_facts.md")]="""# Qwen NI05.3 /539–548
Read wiki/database/nicora_ni053_unloading_facts_20261012.md and original receiver UI/native receipt owner. Author543 actual delivered customer3/manual/no-loader; source519 must not be recreated; ctx543 saved exact bodies are replayable.
Review clean plan-before-savepoint, same original load locks, new system capture/one start per load, current receiver/role scope, wrong root scan/signature/rolling mode/difficulty-without-loader denial. Verify finish shares receipt/custody/line/outbox transaction, no stock consumption twice.
Fresh isolated scenario: difficult rolling cage with loader, late receipt rollback must restore no finish/no receipt/no outbox while already committed start remains; exact retry. UI reload/disconnect keeps exact op/body, no passwords in pending storage, changed actor/endpoint not mixed. Invalid local storage should be recoverable from server state.
Day crossing midnight belongs start day, open starts block closure; actual source543 source1/done1/open0. Hardware/camera/reference is receiver attestation until real proof; do not invent external ACK.
"""
for name,entry in [
("wiki/index.md","- [Checkpoint549 unloading/norms](database/nicora_ni053_unloading_facts_20261012.md): native539/544/API542, actual customer3/start-finish/manual, source-clock day1/1/open0; versioned tariffs529/534 and published history/UI. Planrev19.\n"),
("wiki/log.md","\n12Oct529–549: existing transport tariff immutable publication/current-rights source locks, sameOP publication100/120/history, nativeVALID/API538; actual unloading system clock/finish joins original STORE543 customer3/manual/no-loader, missing/forged finish refused, dedicated clean-plan rollback, day1/1/open0. Actor535 retired, ctx519 now buyer-delivered3. AdminTS/architecture655 pass; new-table stats548 last counts about0.2ms, growth access-path ownerfinance. Qwen tasks549 prepared, independent/hardware/external not claimed. Next transport money recognition and actual tare cycles.\n"),
("wiki/requirements/nikora_delivery_v55/execution/active/ni07_1.md","\n529–538: existing price-row version publication/current auth and immutable original100 vs120 snapshots, caller rollback/sameOP once, keyset/lazy billing source UI; actual monetary recognition still open.\n"),
("wiki/requirements/nikora_delivery_v55/execution/active/ni05_3.md","\n539–545: exact original customer receipt now supports system start/method/difficulty/loader atomic finish; actual STORE543 buyer3/manual/no-loader, wrongroller/missingdetails denied, no extra stock. UI/API source scoped and exact pending; browser/hardware still pending.\n"),
("wiki/requirements/nikora_delivery_v55/execution/active/ni07_2.md","\n546–548: daily start-day unloading completion and open-start blocker; source543 start1/done1/open0, targeted statistics decision. No fake full day close or external ACK.\n")]:
 p=Path(name);v=p.read_text(encoding="utf-8");out[str(p)]=entry+v if name=="wiki/index.md"else v+entry
p=Path("wiki/runbooks/nicora_active_work.md");entry="""Checkpoint549: planrev19/native544+534/API542+autoreload; architecture655/adminTS541/546 PASS, encoding needs after latest docs. ctx519 TT33622/WARE14526684/tagdc223cc37e is now delivered customer3 by STORE543, physicalsourceP0/cost2.25 preserved. ctx543 contains system UNLOAD543.START and exact receipt/details, completedmanual/no-loader; no factory519 or initial receipt/start assumptions rerun. ctx532 own legacyPRICEID1/OWN.NORM532 private company, normhead3 snapshots100/120/120; normalpublisher535 retired. NativeVALID last540, needs final incremental verification.
Next monetary transport norm recognition and actual NI06.3 tare cycles. New unloading SOURCE clock/fact consumption, vehicle-size/actual loader proof needed; no naive/deduced metadata dates. Source mismatch stoim_tt is goods valuation, GET_TT_PRICE mutates fields; never readonly invoke. Source RRL_TRANSPORT_PRICE existed empty, now isolatedownrow1; no originaldriver company's data modified.
Qwen3:8b available via Ollama, tasks549 prepared only; independent review not run. Current user authorizes full commit/GitHub AFTER all sprints complete; SAP excluded. Former06MSK stop deadline revoked by continuation. No subagents.
"""
out[str(p)]=entry+p.read_text(encoding="utf-8")
print(json.dumps(out))
