import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/services/traceability_service.py");s=p.read_text(encoding="utf-8")
s=s.replace("                       LOCKED_AT,","                       LOCKED_AT,\n                       CLAIM_VERSION,\n                       LEASE_UNTIL,").replace("                   LOCKED_AT,","                   LOCKED_AT,\n                   CLAIM_VERSION,\n                   LEASE_UNTIL,")
# Avoid double fields caused by indentation substring overlap.
s=s.replace("                   CLAIM_VERSION,\n                   LEASE_UNTIL,\n                       CLAIM_VERSION,\n                       LEASE_UNTIL,","                       CLAIM_VERSION,\n                       LEASE_UNTIL,")
s=s.replace('if event.get("status") == "DONE":','if event.get("status") in {"DONE","EXPORTED","ACKNOWLEDGED"}:')
out[str(p)]=s
out["wiki/database/retailcase_outbox_lease_20261010.md"]="""# Lease и fencing существующего outbox,154

Existing RRL_EVENT_OUTBOX/RRL_ADAPTER_REQUEST_LOG retained; additive CLAIM_VERSION, aware LEASE_UNTIL/RESPONSE_AT_TZ, claim worker/FINISH_HASH. RRL_OUTBOX_DELIVERY_API owns short claim/begin/finish/manual retry transactions. Default disabled adapter still does not claim. Native APIs/guards liveVALID with no USER_ERRORS, current manifest schema startup and contract registered; full bundle generated only.

Explicit single FETCH SKIP LOCKED skips an oldest row owned by another worker, checks at most100 candidates. Expired aware lease consumes one unconfirmed attempt and preserves old request UNCONFIRMED; legacy LOCKED without aware lease requires reconciliation. Begin refuses second request for one claim, never blindly repeats send after an unconfirmed begin. Finish checks generation/worker/lease/current request identity, atomically retains response/hash and finalizes event. Late response becomes STALE_RESPONSE, cannot finish current generation. Same response replay returns stored historical outcome, not assertion about current event generation; different payload rejected. No HTTP under locks and no internal COMMIT.

Manual retry checks current active actor/right before/after event lock, rejects active or legacy locked/completed events, increments generation. Failure history TRY_COUNT preserved. Exhausted retry grants one further MAX slot and writes MANUAL_RETRY request evidence with actor/reason/old/new retry limit. Managed rows reject old/direct updates including transition0→positive. Existing legacy generic XML exports withclaim0 retained separately; not full migration of every exporter.

Actual own targets Q154_99e65ad277/events2300,2301 and Q154_fc2e624ad2/events2302,2303,2304: locked head skipped; two workers/one event exactly one claim; expired1second lease reclaimed generation+1; late old DONE recordedSTALE/currentLOCKED unchanged; whole finish rollback restores both request STARTED/hashNULL and eventLOCKED; exact replay/conflict/old markdone denial; completed/manual/current-lease denied, unknown actor denied; authorized exhausted retry preserves1 and raisesMAX1→2 with durable evidence, then own synthetic failureDEAD_LETTER2. No real provider/no stock. Adapted153 error case event2305 stillERROR503→RETRY1/exact38digits and audited cleanupDEAD_LETTER2.

ArchitecturePASS504files0cycles79allowed debt. V$SQL claim15.251ms/3, requestlookup0.828ms/4, eventlock0.365ms/11, finishhash0.755ms/4. Retain existing status/retry and target/status indexes plus event/request PKs; no speculative additional index. Integrations owner backlog: realistic pending/dead-history distribution and EXPLAIN/actual plan before production queue sizing, then dedicated eligible/lease index or bounded partition/history policy if measured need. Not million-operation capacity proof.

At-least-once external transport still requires stable event idempotency/provider dedup/status reconciliation. Response held in worker memory can be lost if Oracle unavailable or process dies before finish: local durable response recovery remains next slice155. No government/SAP ACK inferred from simulated response.
"""
p=Path("wiki/index.md");out[str(p)]="- [Захват и завершение outbox](database/retailcase_outbox_lease_20261010.md):154 aware lease/generation/stale-response fencing/atomic finish/manual audit; private concurrent case/no stock.\n"+p.read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:154 existing outbox nativelease+generation+responsehash, shortUOW/managed guards/liveVALID/currentmanifest. Headskip/two-workers/expiry/stale/atomicrollback/replay/manualhistory authorPASS/no stock;153error stillPASS. Architecture504/0/79PASS; SQLclaim15.251ms existingindexes retained/productionqueue-plan backlog ownerintegrations. Unpersisted response crash window next155, no realACK.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")in{"NI04.3","NI07.2"}:row.setdefault("implementedSlices",[]).append("154 existing outbox aware lease/fenced generation/atomic finish/audited retry")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI04.3/154_захват_и_завершение_outbox.md"]="""# Qwen —154
Read wiki/database/retailcase_outbox_lease_20261010.md and native source. Own isolated target only/no real provider.
Check two workers one event, oldest locked row does not hide next; expire1s lease then old success cannot mutate next owner; begin sameclaim twice refused. Atomic finish rollback then exactsame replay/different conflict. Direct oldmarkdone/direct generation0→positive update refused. Manual retry cannot steal active lease, rejectcompleted/unknowninactive actor; exhaustedretry preservesTRY, recordsactor/reason/oldMAX and grants one auditedMAX slot. No quantity effects. Legacy LOCKEDwithout aware lease needs reconciliation/no naive-date UTC guess. DefaultDISABLED preservespending. Saved historicalfinish replay is not currentgenerationclaim. Provider dedup and local durable response recovery separate, not governmentACK.
"""
print(json.dumps(out,ensure_ascii=True))
