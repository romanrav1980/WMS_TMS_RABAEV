from pathlib import Path
import json
out={}
actor="wiki/database/nicora_stock_actor_admission_20261010.md"
out[actor]="""# Действующий пользователь ядра остатков,152

Common root admission now requires current nondeleted RUSERS ID before immutable replay/source compilation and after original resource locks. PK reads only; no extra actor row lock or global physical mutex. Command-specific warehouse/rights rules remain current modules; this is not a full new permission registry. Native/Python command owners retain whole commit/rollback.

All recorded operation actors have existing RUSERS records; no unregistered service principal invented. Actual current nonadmin active old operation actor unavailable, so author uses original admin SAP receipt with rollback-only DELETED=1 on own connection. Exact saved request rejected20882 STOCK_CURRENT_ACTOR_REQUIRED; missing actor rejected; rollback restores admin and exact original receipt replay returns same result/event count unchanged. No persistent user/stock change. Actor-change-during-lock-wait independently verify.

Migration2026-10-10_stock_actor_admission body-only1 statement/live spec+bodyVALID, unchanged spec avoided trigger invalidation. Full source/spec+body replaces current manifest component; bundle generated only. Explicit compatibility setting unchanged; callers require registered active user/service principal rather than implicit admin.

SQL current actor related keyed count first11.181ms and repeated observed cursor0.113ms/10508, not full workload benchmark. Decision retain PK lookup/no actor lock; do not infer million-operation capacity. Source/direct API permission and replay warehouse audits remain separate. No full sprint acceptance.
"""
exchange="wiki/database/nicora_outbox_response_20261010.md"
out[exchange]="""# Ответ ERROR не завершает исходящее событие,153

Integrations domain delivery decision is the sole classification: adapter DONE plus HTTP2xx or nonHTTP transport no HTTP code means transmission completed. ERROR/unknown state/failed HTTP requestERROR and native mark_outbox_error, not unconditional DONE. Original response body/IDs/external status/HTTP/error code retained. Legal acceptance separate: explicit boolean true from non-simulation adapter only; never inferred from2xx or truthy string. Default DISABLED no claim unchanged, MOCK remains mock/not signed.

RegulatoryResponse dataclass moved to pure domain with contract alias retained, avoiding domain outward dependency. Existing OutboxService uses public rule; current native event/request ledger/retry/MAX remain. Event read to_clob(PAYLOAD_JSON) preserves original bytes/numeric text and avoids native JSON dict CLOB bind failure. No provider credentials/network connector/new acknowledgment claimed.

Six response casesPASS including ERROR503/DONE500/STARTED200 refused, DONE202 transmission only/no legal implication, nonHTTP DONE permitted, boolean HTTP invalid. Actual private target Q153_bc63be3019/event2299, simulated failing adapter: requestERROR/HTTP503/SIMULATED_RETRYABLE_ERROR/error metadata and response preserved, eventRETRY1. Exact raw38digit numeric payload retained, stock event count unchanged. Own private failure later markedDEAD_LETTER for cleanup. Initial table name/signature in author script corrected from live evidence before successful creation; no affected real queue.

ArchitecturePASS503files0cycles79debt; no OracleDDL. SQL add/update/error15.550/6.684/15.310ms, retain current keyed journal/update and native retry. Crash claim lease/current worker fencing and async status polling remain next concerns; this is not proof of production regulatory delivery.
"""
out["wiki/index.updated.tmp"]="- [Ошибка адаптера остаётся в повторе](database/nicora_outbox_response_20261010.md):153 responseERROR/HTTP503→requestERROR/eventRETRY1/raw38digits preserved/no realACK.\n- [Действующий пользователь общего ядра](database/nicora_stock_actor_admission_20261010.md):152 active RUSERS before replay/after locks/body-onlyVALID/exact old receipt restored/no stock.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"""
2026-10-10:152 common native current actor before replay/after original locks, PK reads/no actor mutex/per-kind rights retained. Allactorsregistered; rollback-only admin deactivation oldSAPexact replay denied20882/unknown denied/restored exact/journalunchanged. Body-only1stmtVALID/currentmanifestgenerated. Keyedactor11.181ms first/observed repeated0.113ms retain/no load claim.
2026-10-10:153 pure domain regulatory delivery classification/error status notDONE, raw CLOB payload retained, legalACK separate strictboolean/nonsimulated.6 responsecasesPASS; private mockfailure event2299/Q153_bc63be3019 requestERROR+body/IDs/503/eventRETRY1/exact38digit/no stock/owncleanupDEADLETTER. Live table/signature corrections beforecreate; no realqueues/network. Architecture503files0cycles79debtPASS; SQL15.550/6.684/15.310ms keyedledger retained. Crashlease/fencing and async status polling next.
"""
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni08_1.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nCross-cutting152 active root actor admission and153 truthful outbox error delivery retained; see database/nicora_stock_actor_admission_20261010.md and nicora_outbox_response_20261010.md. No full permission/GOV acceptance claim.\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":row.setdefault("implementedSlices",[]).append("152 common current root actor admission before replay/after lock")
 if row.get("id")in{"NI04.3","NI07.2"}:row.setdefault("implementedSlices",[]).append("153 responseERROR remains retry/original raw CLOB and diagnostics/no fake legalACK")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/152_актуальный_пользователь_ядра.md"]="""# Qwen —152
Root active RUSERS before replay/source compilation and after locks, no actor row mutex/current per-kind rights unchanged. Actual sourceactor deactivation during wait independently verify. Author admin deactivation rollback-only (never commit) rejected originalSAPreceipt exact20882, unknown actor rejected, restored saved replay/journalunchanged. Body-only1stmtVALID; full manifest source retained. No service principal invented, compatibilityOFF unchanged.
"""
out["задания на проведения тестов/NI04.3/153_ошибка_внешнего_адаптера.md"]="""# Qwen —153
ERROR/unknown/DONE+failedHTTP cannot mark eventDONE. Preserve response IDs/HTTP/body/external state and requestERROR; native retries/MAX. DONE2xx transport completion not legalACK; real_ack explicitTrue and nonsimulation only, false/truthystring/mock never legalACK. Defaultdisabled no claim.
Original CLOB to_clob read/raw exact signed payload including38digit numeric source preserved; no nativeJSONdict bind/reserialization. Private simulated2299 targetQ153_bc63be3019 alreadyDEADLETTER cleanup, no realqueue claim/network. Six response cases and actual requestERROR503/RETRY1 authorPASS. Crashlease/fencing/statuspolling not accepted by this patch.
"""
print(json.dumps(out,ensure_ascii=True))
