# GROUP1939: ordinary CASE_PICK_CONFIRM caller rollback

PREPARED AUTHOR SCRIPT ONLY. Root owns execution and the exclusive N1939 UI/ACL window. No code path commits a goods command or closes CASE. Old CRES/GQP scripts and retired journals are unchanged.

Target: CASE1139/line1141, WAVE570/PLAN2201, N1939.OP, resource63/session59, warehouse13583852, confirmed identifier090000000000010017. Starting lineage is parent23/H1 plus retained old child1/H0 at the original origin; no new CASE child exists. Native manual time must be OFF/IDLE after root completes the time acceptance. Fresh pinned encrypted TEST EMPTY must exist in root's report and current native archive, exact SHA and DB age at most120sec. A read or replay never refreshes its original measurement time.

## Execution order

1. Validate current fixture, flat0, role3/permissions, exact active original N1939.SELF/WARE assignmentsv1, unchanged warehouse object and absent private namespace/history. Read and retain both UID source/cell/P/H/version/origin, CASE/line, reservations including versions, CASE/resource events/receipts and carrier history.
2. Freeze/fsync all eight normalized ACCESS command DTOs, exact canonical CASE_PICK_CONFIRM1EA wire, source hashes and old→new grant mapping before the first mutation.
3. Commit canonical private GROUP_SAVE (only warehouse13583852), current GROUP assignment, then revoke the two original assignments. No WARE/DC hierarchy, role or session edit. GROUP validity is bounded to15min or root deadline23:00MSK, whichever is earlier.
4. In a NEW clean caller connection prove effective GROUP-only and flat0; native prepare then execute the single frozen ordinary CASE_PICK_CONFIRM. Recheck GROUP-only in the same cursor after prepare and after execute. Check actual PICKED1EA result/stock operation, parent22/H0, new CASE child1/H1 with original origin, exactly one aware UTC native clock and one canonical outbox event.
5. Always rollback the entire goods transaction and reset the native connection. Verify original source/task/line/reservation/event/carrier snapshots exactly, absence of the new UID and operation/clock/outbox/STEP_USE artifacts. No nested metadata CLOSE or second dirty prepare is attempted.
6. In finally, restore the original effective WARE/SELF scope, membership and original validity through NEW N1939.GQP.RESTORE.WARE/SELF assignments. Existing ACCESS ASSIGN is INSERT-only; old IDs remain revoked atv2. Each restore requires the unchanged original scope/currentv2 and an immutable native receipt proving this exact proof command performed the revoke (actor admin plus original payload hash). Then retire only this proof's GROUP grant/group, requiring their own immutable create/assign receipts. Retain every audit record.

## Recovery and root cleanup

Script: tmp/group1939_quantity.py. Root-only execute requires GROUP1939_ROOT_REVIEWED=1 and N1939_UI_ACL_WINDOW_RELEASED=1 plus --execute-reviewed. Default --plan imports no Oracle and writes no journal. A partial existing journal forbids a fresh whole proof; use the same frozen --restore-only after review. Any conflicting/unknown source or incomplete compensation reports RECOVERY_REQUIRED, without new IDs, reactivation or quantity retry. Compensation progress logging is best effort so a full disk cannot suppress already-frozen canonical cleanup.

The final group-quantity-journal.json retains full normalized bodies/source hashes, ACK bodies/local ACK hashes and acl_replacement_map. Root retirement MUST read new active restore IDs/current versions from that report. Original fixture grant versions are stale after this increment; do not silently re-enable the old IDs. If fixture/user/role changed during failure, private cleanup is still attempted only with this proof's receipt provenance, and unresolved restoration remains explicit.

This proves GROUP-only quantity admission with caller rollback. It does not prove positive CLOSE, hardware, physical picking, committed late replay or a production pilot. Positive CLOSE requires separately reviewed oneEA canonical commit, a fresh clean close transaction and RETURN→WAVE_CANCEL→PLAN_CANCEL/tare cleanup preserving parent/old/new UID lineage. That later stage is absent from this script.
