import json
from pathlib import Path
out={}
entry="""\n550: transport norm publication/history UI now uses the existing native529/534 owner. Exact intent persisted before send, key API+exact actor+warehouse+source (no password), unchanged operation retry; only server-confirmed409 permits correction. Source/head version and metadata authority remain native. UI currency/date/zone/class/unload rates/reason/reference, latest published version and descending history30. Structured API errors preserve outcome_confirmed. No source PRICE or goods balance writer added.
Store unloading recovery retains malformed local raw intent in archive, authoritatively reads server preview before clearing damaged intent, then refreshes original receipt UI; recovery refusal keeps receipt blocked. Difficult rolling without loader cannot supply finish details. Optional unloading GET parameters are bounded100/255.
Typecheck550 pending at documentation preparation; no browser/independent acceptance claim. Next finance monetary recognition and tare custody trace; all18 are not complete.
"""
p=Path("wiki/database/retailcase_ni071_transport_norms_20261012.md")
out[str(p)]=p.read_text(encoding="utf-8")+entry
p=Path("wiki/database/retailcase_ni053_unloading_facts_20261012.md")
out[str(p)]=p.read_text(encoding="utf-8")+entry
p=Path("wiki/runbooks/retailcase_active_work.md")
out[str(p)]="Checkpoint550: norm publisher and paginated history in existing billing UI; malformed unloading intent recovery via archive/server preview; difficult rolling requires loader before receipt. Native quantities unchanged, no new migration. Final TS/encoding pending. All18 not complete; no GitHub publication yet.\n\n"+p.read_text(encoding="utf-8")
p=Path("wiki/index.md")
out[str(p)]="- [Checkpoint550: формы транспортных норм и восстановление выгрузки](database/retailcase_ni071_transport_norms_20261012.md): существующий native API, точный повтор операции, история30; malformed unload recovery сохраняет исходник и сверяется с сервером.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md")
out[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-12 checkpoint550: existing billing norm publisher/history and structured error semantics; unloading corrupted local intent recovery and loader validation, GET bounds. No new quantity owner/DDL. TS/encoding pending; no full acceptance or publication.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json")
m=json.loads(p.read_text(encoding="utf-8"));m["planRevision"]=20
for item in m["increments"]:
 if item["id"]=="NI07.1":item["implementedSlices"].append("550 existing native norm publisher and history30 UI with durable exact intent/current source version/confirmed-refusal correction; not monetary recognition")
 if item["id"]=="NI05.3":item["implementedSlices"].append("550 corrupted local start recovery preserves raw archive and verifies server preview; difficult rolling without loader blocks details; bounded optional unload GET")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.md")
v=p.read_text(encoding="utf-8").replace("**Revision 19, 12 октября 2026 года.**","**Revision 20, 12 октября 2026 года.**")
out[str(p)]=v+"\nCheckpoint550: добавлены публикация и история транспортных норм в действующем биллинге, сохранение точной операции и исправление после подтверждённого отказа; восстановление повреждённого локального начала выгрузки через сервер. Начисление транспортных расходов остаётся открытым.\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[str(root/"NI07.1/550_norm_ui.md")]="""# Qwen: NI07.1 UI550
Prepared only; do not run additional model qualification automatically.
Review TransportNormPublisher, TransportNormHistory, TransportTariffSources and api.ts. Use isolated metadata and current authorized actor. Do not recreate ctx532, reset retired publisher535 or publish a tariff for an original carrier.
Cases: unknown response after commit -> saved identical OP/body retry returns one native version; confirmed409 -> refresh current source/head before editable new intent;403/network/500 do not allow dropping intent; separate exact actor/API/warehouse/source keys; malformed storage blocked; no password persisted. A successful publish followed by failed read must remain visibly published, not unknown.
History limit30, descending version keyset, stale response after switching source ignored. Current source fields versus frozen snapshot displayed distinctly; no PRICE/P/H or monetary costs effect. Record observed result, do not mark full NI07.1 accepted.
"""
out[str(root/"NI05.3/550_unload_recovery.md")]="""# Qwen: unloading recovery550
Prepared only; do not recreate original source519/543 or run full regression.
Malformed saved local start JSON must block receipt and offer recovery. Retain raw archive before any removal; failed authorized server preview keeps original intent and block. Successful preview obtains real STARTED/COMPLETED/absent state before clearing corruption and refreshing UI. If source changes during request do not modify new source state.
Validate saved body scope/OP/scan/camera fields, repeated exact request, double click guards; rolling_difficult without loader supplies no finish details. No claim that camera checkbox verifies hardware or that loader attestation is provider evidence.
"""
print(json.dumps(out))
