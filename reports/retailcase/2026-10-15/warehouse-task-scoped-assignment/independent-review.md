# Independent review: TASK scoped assignment

Scope: prepared migration `2026-10-15_warehouse_task_scoped_assignment`; read-only source review, no Oracle writes or runtime acceptance. Reviewer is not migration author.

Two findings sent to parent/author before application:

1. Lazy baseline version0 had no parent FK for untouched historical tasks. DELETE/reinsert same task ID/body could restore version0 and identical signature. Parent approved all-row immutable identity BEFORE DELETE / UPDATE OF TASK_ID guard, without backfill or task ALTER. Final guard/source/rollback delta review remains pending.
2. Dispatcher assignment with an existing same-target assignee and changed physical tuple initially returned APPLIED/no change. Latest body now rejects any changed resolved tuple with WTASK_EXPLICIT_RESOURCE_TRANSFER_REQUIRED, retaining same-binding no-op behavior. Re-read verified.

No additional blockers found in reviewed current body/access/resource policy: capability is bound to actual TX/task/action/actor/target and rechecks current scoped authority; original receipt rechecks original actor/current target authority. Clean begin_plan precedes revision SHARE/policy/resource locks. Sidecar derive/writing is limited by ACCESSIBLE BY to the two intended triggers, guarded monotonic and reset on exception; changes remain in caller transaction. FK/history protections preserve existing sidecar/receipt identities. No Stock writer was added. Legacy COMPLETE authorization branches remain.

Required native proof after final kit: direct sidecar mutation/derive refusal, unseeded and seeded parent DELETE/PK replacement refusal, same-value identity update allowed, old-writer assignment A-to-B-to-A increments version twice, failed/rolled-back task update restores sidecar, exact receipt and wrong-body/revoked/foreign actor cases, clean-vs-dirty entry and true concurrent assignment/version race. Preserve source quantities/events; source review alone is not runtime evidence.

Final frozen delta re-read: RRL_WTASK_IDENTITY_GUARD rejects every parent DELETE and actual/null TASK_ID replacement while permitting same-ID update. It covers untouched historical baseline0 tasks. apply includes trigger; before namespace includes name; AFTER exact source SHA recomputed locally A7E94EBAC80B49A74FF23A6C50DF8C2CC32E31BDD3EE87CE3CC8B2669E8B579A equals checkpoint/guard. Rollback first verifies full AFTER sources and both clock/receipt tables empty before dropping identity guard. Source-review APPROVED; no remaining static blockers. Native runtime acceptance remains required and was not run by this reviewer.
