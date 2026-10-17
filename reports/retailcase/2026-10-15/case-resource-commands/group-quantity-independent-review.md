# Independent GROUP-only quantity proof review

Artifact: scripts/case_group_quantity_proof.py. Read-only review; reviewer did not execute the script, SQL, ACL or native commands. CASE1138/session55 UI HOLD is unchanged.

Initial source has the correct bounded goal: all eight canonical metadata intents plus exact CASE_PICK_CONFIRM1EA wire saved fsync/atomic before any ACL call; a fresh explicit clean Oracle connection runs only native prepare/execute and unconditionally rolls back/resets; before/after comparison includes task/line/both original UID lineage/reservations/events/resource receipts, plus absence of operation/clock/outbox/newlot/carrier/STEP_USE.

Blocking findings sent before RUN:

1. restore() began with fixture(strict=False) outside compensation handling; changed/retired role/user/task or read failure could prevent every restore/private GROUP retirement attempt. Require unconditional attempts for strictly owned private GROUP cleanup, without reactivating role/user.
2. Compensation run_acl required writing progress before calling already-frozen restore intents. A reporting/disk failure after an ACL mutation could suppress compensation. Best-effort progress writes must not block execution of validated intents already durably saved before mutation.
3. REVOKED_AT alone does not prove this script revoked an original grant. A legitimate external revoke racing expected-version failure could be undone. Require exact immutable ACCESS receipt for this script's original revoke, matching actor/hash/target/version, before restoring through a new ID; foreign/no-receipt revocation is preserved and reported.
4. A self-hash does not bind a loaded restore-only journal to the authorized fixture. Validate the complete command whitelist/IDs/kinds/payload/role/GROUP/actor/targets and original bindings before any restored ACL mutation.
5. Assert GROUP-only authority/flat0 with the same physical cursor after prepare and after execute, rather than attributing the positive solely from earlier separate preflight connections.

Author acknowledged all five fixes in progress. Final frozen delta review pending; no approval to RUN from this reviewer yet.

Final frozen delta read-only APPROVED: scripts/case_group_quantity_proof.py SHA256 8192a21b2c80730a09f847dfe79feee929cb6063ede91622bd48639f29d2badd,281 lines. All five findings resolved in source. Strict reconstructed eight-command whitelist and exact fixed Stock request prevent retargeting; original restoration requires matching immutable admin/hash receipt and version+1/source; compensation logging is best effort; private GROUP cleanup is attempted even when fixture guard/read fails; same-cursor isolation checks surround native execute. Static AST scan found no commit/post/post_command calls. No script, Oracle, ACL or native command was executed by this reviewer.

Role/user/task drift intentionally leaves original scopes for manual reconciliation with RESTORE_REQUIRED while still attempting private GROUP retirement; never auto-reactivates a role/user. Author pure tests and coordinator's actual native result are separate evidence and were not claimed by this source approval.

V1 coordinator runtime result (reported by root, not run by reviewer): FAILED_PROOF_ACL_RESTORED because SQL DBMS_TRANSACTION.LOCAL_TRANSACTION_ID(false) raised ORA00904 before Stock prepare. All eight ACL steps restored; no quantity proof. Original V1 source/hash retained.

V2 independent read-only diff APPROVED: scripts/case_group_quantity_proof_v2.py SHA256 ba939dbd26abb3e2cc53ce8e13e17c554add05c22779ca25cf8e7e18259ce6a7. Changes limited to fresh GQP2 namespace/journal/command/operation/restore IDs, original whitelist now V1-restored GQP.RESTORE.SELF/WARE v1 (SELF suffix correctly updated), and clean-TX check via PL/SQL cursor.callfunc('DBMS_TRANSACTION.LOCAL_TRANSACTION_ID',str,[False]). All restoration ownership/frozen whitelist/rollback safeguards unchanged; static AST no commit/post/post_command. Driver/runtime success requires separate coordinator evidence. No SQL, ACL, or script execution by reviewer.
