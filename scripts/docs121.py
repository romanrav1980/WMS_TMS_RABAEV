from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=["../2026-10-10_ni061_custody/004_root.sql"if x=="../2026-10-10_ni061_placement/006_root.sql"else x for x in m["components"]]
for group,names in {"components":["002_command.sql"],"startup_scripts":["001_schema.sql","005_active_index.sql"],"additional_scripts":["003_load_guard.sql","006_proof_guard.sql"]}.items():
 for name in names:
  item="../2026-10-10_ni061_custody/"+name
  if item not in m[group]:m[group].append(item)
if "RRL_STOCK_INTERWARE_CUSTODY" not in m["packages"]:m["packages"].append("RRL_STOCK_INTERWARE_CUSTODY")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/index.updated.tmp"]="- [Ответственность первого межскладского плеча](database/retailcase_ni061_custody_20261010.md):121 APPLIED, actual119 receipt/native release/history DEPARTED retained/activeUID released/P3H0 unchanged/replay; onward ST next.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:121 APPLIED13/0 explicit Root INTERWARE_CUSTODY_RELEASE on original119; append-only proof and load custody columns, actual unload timestamp, departure history/ST retained, activeUID released/P3H0/event0. PASS117f1e5e26 current target actor/foreign403/replay/conflict/second/direct history edit denied. Checkpoints438Root439actualLoadGuard; index installation creates replacement uniqueness before removing original, idempotent predicate check. Initial indexDDL invalidated trigger with no source errors, explicitcompile added beforeVALIDgate. SQL27.595/39.533/18.449ms keep receipt/source uniqueness/PK and scoped100 queue, transport owner growing lineage. Old sourceST assignment preserved; next existing outbound ST constructor with original fulfillment ownership, not reassignment/deletion."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md","Ticket121: [перевозочная ответственность](../../../../database/retailcase_ni061_custody_20261010.md); original119 accepted receipt/currenttarget receiver/explicitRoot proof → activeUID released whileDEPARTED/sourceST/history/P3H0 retained. Actual onwardST/packing/marked/nested remains open.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
out["wiki/database/retailcase_ni061_custody_20261010.md"]="""# NI06.1 — ответственность первого плеча,121
Migration2026-10-10-121-interwarehouse-first-leg-custody-release APPLIED13/0 RABAEV/orcl. Checkpoints438Root/439 actual load guard (437 unchanged read package). New private RRL_STOCK_INTERWARE_CUSTODY/new proof/load guard/Root/indexVALID.
Existing RRL_TT_HU_LOAD_FACT adds CUSTODY_RELEASED_AT/CUSTODY_RELEASE_OPERATION_ID with immutable RRL_INTERWARE_CUSTODY_PROOF referencing original applied119 receipt and original departed load. Explicit root command/interwarehouse_receive/current targetWARE. Actual unload timestamp, full original departure/UID/TT/vehicle/dock/composition/version/departureOP preserved, original sourceST membership never reused/deleted. One metadata TX/root result/native common outbox/proof/custody columns; no P/H/event/customer delivery confirmation.
Active UID unique now only LOADED/DEPARTED without custody release. Replacement index created before old uniqueness removed; existing upgraded predicate returns without rebuild. Whole indexDDL initial apply invalidated load trigger without source errors; explicitcompile before gate fixed. New load cannot fabricate released custody; TRIP_DEPART cannot forge columns; release only proof/source exact, direct/after release history editing denied. Marked/CASE/nested release not supported by ordinary119 receipt, no bypass.
Author scripts/ni061_custody_case.py PASS117f1e5e26 original INTERWARE.RECEIVE:349bc1ff57/sourceSINGLE.FULL.LOAD:9b15cf997d: current target nonadmin/foreign403/replay/conflict/second/directedit denied. OriginalDEPARTED/TT33498/ST641280/timestamps unchanged, custody actual119unload, activeUID0/P3H0/event0, proof1. Actor retired. No final store delivery inferred.
Raw interwarehouse UI release action works on actually received plan; server rejects missing receipt/current foreign scope. Current day-board custody pending distinct from placement pending and ERP pending.
SQL27.595/39.533/18.449ms retain source/receipt unique PK and scoped100 queue; transport owner growing lineage review. Next new onwardST via existing constructor/assignment/loading linked original fulfillment, old sourceST stays history. Full NI06.1/nested/marked/packing/temperature remains open.
"""
out["задания на проведения тестов/NI06.1/121_ответственность_плеча.md"]="""# Qwen — NI06.1,121
Original119 applied receipt+unload+original departed load; current active target actor/interwarehouse_receive. Root proof/releases active UID at exact actual unload timestamp, retains originalDEPARTED/TT/ST/departureOP/time/composition; no goods/customer delivery effect.
Missing/unapplied/foreign proof/otherWARE/second release/directedit/release columns forged on newload/depart deny. Replay saved result/conflict altered receipt deny. Unique activeUID retained for loads withoutrelease; replacement index installed beforeoldremoved; currentAPPLIED source/triggerVALID.
Original117f1e5e26 already released; continuation only. Target stock3H0/native movement untouched; onward newST original ownership separate. CASE/marked/nested unsupported requires exact custody representation, no ordinary fallback. SlowSQL decision and independent evidence separate from author case.
"""
p=Path("api/wms_api_server/app/modules/finance/infrastructure/reconciliation_sources.py");s=p.read_text(encoding="utf-8")
if '"interwarehouse_custody_pending"' not in s:s=s.replace("BACKLOG=[",'BACKLOG=[\n ("interwarehouse_custody_pending","select count(*)from RRL_INTERWARE_RECEIPT r where r.WARE_ID=:ware and not exists(select 1 from RRL_INTERWARE_CUSTODY_PROOF p where p.RECEIPT_OPERATION_ID=r.OPERATION_ID)"),')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8")
if 'id="iwRelease"' not in s:s=s.replace('<button id="iwRetry"',"""<section class="panel" data-permission="interwarehouse_receive"><h2>Завершение первого плеча</h2><label>Состоявшаяся приёмка<select id="iwCustodyReceipt"></select></label><button id="iwRelease">Подтвердить окончание ответственности первого рейса</button><p>Система использует факты выгрузки и складской приёмки. История первого выезда сохраняется, остаток не изменяется. Доставка клиенту оформляется отдельно.</p></section><button id="iwRetry" """,1)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('el("iwPlacementReceipt").replaceChildren(...rows.filter','el("iwCustodyReceipt").replaceChildren(...rows.filter(r=>r.receipt_operation_id&&!r.custody_release_operation_id).map(r=>new Option(r.pallet_identifier+" · "+r.receipt_operation_id,r.receipt_operation_id)));el("iwPlacementReceipt").replaceChildren(...rows.filter',1)
s=s.replace('say(intent.path==="/placement"','say(intent.path==="/release-custody"?"Ответственность первого плеча завершена. История выезда сохранена.":intent.path==="/placement"',1)
s=s.replace('el("iwTaskLink").replaceChildren();document.querySelectorAll','el("iwTaskLink").replaceChildren();el("iwCustodyReceipt").replaceChildren();document.querySelectorAll',1)
if 'el("iwRelease").addEventListener' not in s:s=s.replace(' el("iwLoad").addEventListener',''' el("iwRelease").addEventListener("click",async()=>{if(busy||pending)return;try{const body={operation_id:"INTERWARE.CUSTODY:"+crypto.randomUUID(),receipt_operation_id:el("iwCustodyReceipt").value};if(!body.receipt_operation_id)throw Error("Обновите планы и выберите состоявшуюся приёмку.");const intent={path:"/release-custody",body};localStorage.setItem(key(),JSON.stringify(intent));pending=intent;await send(key());}catch(e){say(e.message);}});
 el("iwLoad").addEventListener''',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
