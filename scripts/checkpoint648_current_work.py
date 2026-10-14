from pathlib import Path
import json
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"));m["planRevision"]=27;m["date"]="2026-10-12"
m["currentSprint"]="NI06.2";m["currentStream"]="NI06"
notes={
"NI03.2":"631–635 existing multi-binding partial target replacement leaves exactly one reduced whole physical continuation; actual owner6+6→target8H8/source8H4, other owner preserved, P unchanged and replay; own cleanup633",
"NI06.2":"619–648 shared registered aggregation resolver/API/existing UI for BOX and preserved unchanged whole PALLET returns; actual mixed UNIT/BOX624 and PALLET/BOX643 P3H0/3oldkeys6codes, no rebirth/exact replay/different identity refused",
"NI08.1":"636–638 existing driver-day/read/Gantt/common coordinator now preserve continuous driving across trips and midnight with existing explicit REST rule; domain637/TS PASS, outside duty/legal admission unverified"}
for item in m["increments"]:
 if item["id"]in notes:item.setdefault("implementedSlices",[]).append(notes[item["id"]])
 if item["id"]=="NI03.2":item["pendingSlices"][0]="Other physical split modes and partial coverage leaving multiple physical continuations; current bounded case supports multiple old bindings only when exactly one reduced whole source remains"
 if item["id"]=="NI06.2":item["aggregateReturn648"]={"implemented":["BOX-only plus UNIT profiles","PALLET-only unchanged full original identity","existing custody/warehouse UI","shared native resolver/one stock transaction"],"remaining":["PALLET composition changes/partial repacking/new aggregation lifecycle","applicable real regulatory ACK","independent/full acceptance"],"evidence":"wiki/database/retailcase_ni062_preserved_pallet_20261012.md"}
 if item["id"]=="NI08.1":item["crossTripContinuity638"]={"implemented":True,"legalAdmission":False,"externalDutyVerified":False,"evidence":"wiki/components/retailcase_ni081_cross_trip_continuity_20261012.md"}
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.md");v=p.read_text(encoding="utf-8").replace("**Revision 26,","**Revision 27,")
v=v.replace("**Текущий — [NI07.1](execution/active/ni07_1.md);","**Текущий — [NI06.2](execution/active/ni06_2.md);")
v+="""
## Revision27: текущие изменения631–648
NI03.2: частичная замена нескольких собственных HARD в существующем native wave, один оставшийся целый physical source; P неизменён/чужой owner сохранён.
NI06.2: registered BOX возврат и неизменённая полная исходная PALLET с прежним UID проходят existing approval/SAP/handover/pickup/receive/PUT; actual643 P3H0/3keys6codes. Новый UID со старым PALLET кодом отвергнут. UI поддерживает заданный в товаре UNIT/BOX/PALLET/UNIT_OR_AGGREGATION.
NI08.1: непрерывное наблюдаемое вождение между рейсами/через полночь входит в прежние driver-day/Gantt/coordinator; explicit REST из существующего правила. Предыдущая смена/внешняя работа/правовые нормы не подтверждены.
Все18 спринтов ещё не завершены. Оригинальный auto-split NI02.1 требует исходника или решения владельца о восстановлении на existing preparation; вопрос задан. Full GitHub publication выполняется после завершения, SAP/SAP_INTEGRATION исключаются.
"""
p.write_text(v,encoding="utf-8")
p=Path("wiki/database/retailcase_ni062_preserved_pallet_20261012.md")
with p.open("a",encoding="utf-8")as f:f.write("""
## Actual639–648
Native639 applied5statements/0errors; all current objects VALID. Fresh own641 SAP3/sixcodes/originalST/load/depart,642 customeraccepted3.643 full registered CRPT PALLET + EGAIS BOX-only return preserves exact original UID: approval/SAP/plan/handover/independent driver pickup/warehouse fullBOX3/PUT to pickface/P3H0. Different pallet identifier and direct UNIT fallback refused; full-box quantity conflict refused; receive/PUT exact replays returned saved results.646 read-only retains one handover,3original units/6codes, retired driver actor and no rebirth. Do not recreate641/642/643 factories; context643 retained original available pallet, binding restored.

645 existing React/raw return UI accepts actual configured PALLET/BOX level; original identifier/full-composition instruction and durable scoped drafts retained. Native original identity helper is authoritative, not UI counts. TypeScript/JS/architecture PASS. Previous blanket PALLET block629 is superseded only for this explicit full unchanged original-pallet scenario.

647 verifies original receipt UNIT UID PK, CASE LOT_UID PK and HU parent/active index. CASE exclusion0.077ms/1buffer, active-HU check0.651ms/4.4buffers; aggregate646 lookup0.261ms/3.71buffers/count0.616ms/6.57. Decision: retain exact UID lookups/registered composition bounds; no speculative additional index. Not throughput certification. New gov aggregation/repacking/physical hardware/external ACK/full acceptance remain unclaimed.
""")
p=Path("wiki/database/retailcase_ni062_return_aggregation_20261012.md")
with p.open("a",encoding="utf-8")as f:f.write("\nCheckpoint648 supersedes blanket PALLET rejection629 for exact unchanged whole original UID only. Native639/helper/current receipt and actual643 PALLET+BOX complete P3H0; other identity/repacking stays blocked. [[retailcase_ni062_preserved_pallet_20261012]].\n")
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_2.md")
with p.open("a",encoding="utf-8")as f:f.write("\n639–648 preserved original full PALLET return implemented/actual643, current nativeVALID and existingUI. No fresh identity reuse/partial repack/legal ACK implied. [[database/retailcase_ni062_preserved_pallet_20261012]].\n")
p=Path("wiki/runbooks/retailcase_active_work.md");v=p.read_text(encoding="utf-8")
p.write_text("""## Current checkpoint648 — 12Oct2026
- Continue all18; full commit/GitHub AFTER completion; exclude SAP/SAP_INTEGRATION. No agents/model inference/broad qualification. Plan27/currentNI06.2.
- Native631 multi-binding partial target applied VALID; actual632 own12=6+6 -> target8H8/source8H4, otherowner8 preserved/P unchanged. Cleanup template failed after positive effect; corrected builder and633 cleaned existing own facts by core. context632 REBIND_PASS_OWN_CLEANED; do not rerun initial632.
- Native639 preserved whole unchanged original PALLET branch applied5/0/VALID. Fresh641 source/642customer3/643originalPALLET+BOX full return→PUT/sourceoldUID/P3H0/same3keys6codes; wrongidentity/unitfallback/BOXqty refused, exactreceive/PUT replay.646 retained PASS, driver retired/binding restored. Never recreate641/642/643; original return pallet remains available.
- Existing ReturnMarkPanel/raw return-mark-draft support configured UNIT/BOX/PALLET/UNIT_OR, durable actor/API/original-profile scope;645 TS/JS/architecture PASS. Blanket PALLET block629 now superseded only for exact preserved original scenario.
- Existing driver-day now cross-trip continuity636–638/common coordinator/Gantt; domain637 PASS120/REST15/midnight/endclip, TS/architecture PASS. No real legal/external duty admission. Current API644 started45960/26244, startup complete.
- Latest changed native errors/invalid empty. SQL647 CASE0.077ms1buffer/HU0.651ms4.4/aggregate6460.261ms3.71; exact UID keys retained. Multi-source query63458.816ms355 inventory predicate/plan backlog; no broad load.
- Bundle629 predates631/639; append canonical files next, never apply whole ACTIVE. Final docs encoding after648 pending.
- NI02.1 owner question to authorize original auto preparation restoration still pending; no dependent replacement yet. Continue independent residuals. All18 not complete; no fake external/hardware/independent proof.
- Preserve contexts565/586/601 money original107.25/current0;624 mixed BOX return remains ownP3H0; no factories.
- Details [[database/retailcase_ni062_preserved_pallet_20261012]], [[database/retailcase_ni032_multi_binding_partial_20261012]], [[components/retailcase_ni081_cross_trip_continuity_20261012]].

"""+v,encoding="utf-8")
p=Path("wiki/index.md")
with p.open("a",encoding="utf-8")as f:f.write("\n- [Checkpoint648: исходная паллета возврата](database/retailcase_ni062_preserved_pallet_20261012.md): native639 VALID/actual643 oldUID P3H0/3keys6codes, currentUI/plan27; original identity guard supersedes629 only for unchanged whole pallet.\n")
p=Path("wiki/log.md")
with p.open("a",encoding="utf-8")as f:f.write("\n2026-10-12 checkpoint648: native639/actual641–643 unchanged whole PALLET return completed, read646/SQL647/TS/JS/architecture PASS. Plan27 includes631 multi-binding and636 cross-trip continuity. External/hardware/independent/all18 completion not claimed, publication condition pending.\n")
d=Path("db/migrations/2026-10-08_stock_posting_core");p=d/"current_runtime_manifest.json";m=json.loads(p.read_text(encoding="utf-8"))
for name in ("../2026-10-12_ni032_multi_binding_partial/001_wave.sql","../2026-10-12_ni062_preserved_pallet/001_identity.sql","../2026-10-12_ni062_preserved_pallet/002_unit.sql","../2026-10-12_ni062_preserved_pallet/003_receipt.sql"):
 if name not in m["additional_scripts"]:m["additional_scripts"].append(name)
p.write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
print("648 wiki/plan27/native manifest maintained; no whole bundle application or GitHub publication")
