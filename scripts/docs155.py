import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/outbox_response_journal.py");s=p.read_text(encoding="utf-8")
s=s.replace("        probe.unlink()",'''        linked = probe.with_suffix(".probe-link")
        try:
            os.link(probe, linked)
        finally:
            if linked.exists():
                linked.unlink()
            probe.unlink()''')
out[str(p)]=s
out["wiki/database/retailcase_outbox_response_recovery_20261010.md"]="""# Локальное восстановление исходящего ответа,155

RRL_OUTBOX_DELIVERY_API remains Oracle delivery owner. Local response journal stores exact typed finish body/claim version/request identity/target/simulation/ack fact before database finalization. Default directory api/wms_api_server/runtime/outbox_responses, overridable WMS_OUTBOX_RESPONSE_DIR; use persistent local NTFS/POSIX filesystem. Pre-send writable/fsync/hard-link probe and soft500pending backpressure; each record at most8MiB. Original external response is JSON string inside envelope, not reinterpreted or regenerated.

Immutable response publication uses fsync then atomic hard-link create-if-absent; same record different body rejected. Recovery ownership reuses existing OS directory_owner, sharded256locks, released on process death. Response removed only after native finish confirmed; database error retains record. A commit succeeded but client did not receive confirmation repeats identical nativehash on restart. Recovery runs before new provider send, including when adapter disabled, and never invokes send. Expired generation finalizes only STALE_RESPONSE proof, cannot finish newer event. Concurrent record removal while scanning skipped.

Author existing realOracle own event2307/Q155_c892d743eb: injected finish ConnectionError after one simulated provider response; localpending1 and eventLOCKED/requestSTARTED/hashNULL retained. Reconstructed worker with disabled adapter wrote nativeDONE/responsehash and removed file, providercalls remained1/mocklegalACKfalse/stockjournalunchanged.153 actualerror facade stillPASS event2306, auditedcleanupDEADLETTER. Architecture505/0/79PASS.

No external provider/real governmentACK/hardware/power-loss acceptance. Crash between receipt of provider response and local publication, diskloss/full after probe, oversized response, unsupported filesystem/persistent directory unavailable remain unconfirmed delivery requiring provider idempotency/status reconciliation and lease policy; no exactly-once promise. .writing leftovers unpublished are not proof of response delivery. Softbackpressure not strictglobalquota. Pending response files contain exchange evidence: restrict OS ACL to service and authorized operations account, retain persistent volume, exclude GitHub. Recovery key/hash prevents accidental identity conflict, not hostile localdisk administrator tampering.

SQL same keyed154 finish/event/request paths; observed154 avg0.365/0.755ms aftercase, no newquery/index/nativeDDL. Bounded directory scan500, at mostone result perworkerstep, shardlocks only finalize/never provider call. Integrations owner monitor pending/failures and reconcile malformed evidence; don't discard a corruptrecord to silently resend.
"""
p=Path("wiki/index.md");out[str(p)]="- [Восстановление ответа после перезапуска](database/retailcase_outbox_response_recovery_20261010.md):155 durable local outcome before native finish/recovery without provider resend/disabled adapter can finalize.\n"+p.read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:155 local durableoutcome/sharded OSlock/atomic fsync hardlink/samebody replay/backpressure beforeclaim. Private2307 afterfinishfailure reconstructeddisabledworker nativeDONE/providercalls1/mockACKfalse/no stock, architecture505/0/79PASS. SamekeyedSQL retained; prepublicationcrash/physicaldiskloss requireexternal dedup/statusreconciliation, notexactlyonce. Current functionalqueueNI08.1 reflectedinplan; history retained.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.md");s=p.read_text(encoding="utf-8-sig")
s=s.replace("общий architecture gate остаётся красным по прежнему debt. **Текущий — [NI05.3](execution/active/ni05_3.md), in_progress;", "на дату начала редакции общий architecture gate был красным по прежнему debt. После149 gatePASS с уменьшенной baseline/0cycles. **Текущий — [NI08.1](execution/active/ni08_1.md), in_progress;")
s+="\n10.10.2026:154–155 existingoutbox awarelease/fencing/atomic response+event/auditedretry and durablelocalresponse recovery delivered. No externalGov/SAP acceptance inferred. Current NI08.1 resource/range approval/drain/common timing validator, then remaining functional residuals per active cards. All17 open remain open until complete business result, not only author slice.\n"
out[str(p)]=s
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")in{"NI04.3","NI07.2"}:row.setdefault("implementedSlices",[]).append("155 local durable provider response/native recovery without resend")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI04.3/155_восстановление_ответа_после_сбоя.md"]="""# Qwen —155
Own isolated target/journal directory only. Simulated adapter returns once, inject nativefinish failure: record must remain and requestSTARTED/eventLOCKED; reconstruct worker evenadapterdisabled must finish samebody withoutsend, delete onlyafterconfirmedDB. Commit-response-loss replay samehash; expiredclaim recovery STALE cannot mutate newowner. Two recoveryworkers OSshards samefile onlyonefinish/delete; removal while scan safe. Samekeydifferentbody conflict, symlink/oversize/corruptrecord explicit failure, beforeclaim diskprobe/backpressure. No secrets/rawresponse print, no real externalqueue. Test WindowsNTFS hardlink and fsync locally, do not infer powerloss acceptance; prepublication crash requiresproviderdedup/statusquery. Author2307 PASS/native stockjournalunchanged. See database/retailcase_outbox_response_recovery_20261010.md.
"""
print(json.dumps(out,ensure_ascii=True))
