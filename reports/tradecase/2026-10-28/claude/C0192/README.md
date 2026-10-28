# C-0192 — cleanup after shipping the mixed pallet (companion to C0190+C0191)

## Files
- `scripts/c0192_mixed_tree_cleanup.py`: `run(live)` on the C0190+C0191 Live state; no live work on import; C0190/C0191 not changed.
- `tests/tradecase/test_c0192_mixed_tree_cleanup.py`: 24 offline tests.

## When it starts (`delivery_findings`, otherwise a stop with nothing sent)
- C0191 `STORE_RECEIPT` completed, and C0191 has no `stopped`;
- the fixture belongs to the run: tag `MT28…`, warehouse and wave present;
- `driver_user`/`receiver_user` are only this run's synthetic users (`MT28D|MT28R` + 9 hex);
- `vehicle_id`/`driver_id`/`transport_task_id` match the C0191 journal answers (`t.vehicle`/`t.driver`/`t.task`);
- `expected_remainder_after_load` is present.

## Steps (all writes through the C0190 journal: stored before sending, the same body/operation_id on resume, unknown outcome blocks the rest; completed steps are not repeated)
1. **Tare return** between two different participants: offer VEHICLE→WAREHOUSE under the run's driver, accept under the warehouse (admin); NS23 pattern.
2. **Root tare to zero:** the warehouse balance of the pallet type, only when it is exactly `1` (otherwise `ROOT_TARE_BALANCE_UNEXPECTED`). If C0190 cleanup already zeroes the same pallet type, the companion does not zero it a second time.
3. **`driver-bindings` active=false** with the version from the C0191 journal answer.
4. **Finishing the wave:** `GET /api/picking/waves/{wave}/execution` must be `ready` (already `completed` → nothing is sent) → `POST …/finish-execution {operation_id}` + exact repeat.
5. **Own stock:** only UIDs of the registered lots and the run's carrier lots, only the two articles, the remainder exactly `expected_remainder_after_load`, 0 active reservations. Otherwise `STOCK_SCOPE_REFUSED`: nothing is counted, and the users are not retired. Then a native `INVENTORY_COUNT` of the run's lots to 0 (through `live.post`, journal `native.c0192.count.zero`) and a check P=0/H=0 (`WAREHOUSE_NOT_EMPTY_AFTER_CLEANUP` otherwise).
6. **Retiring:**
   - the `store_receipt_confirm` right of the receiver group is removed through the supported `DELETE /api/admin/rights/groups/{group}/rights/{right}`;
   - the driver and receiver: `RUSERS.DELETED=1`; the driver's rights (group = driver ID) are removed from `RIGHTS`, as in NS23;
   - there is no route to delete the group itself, so the receiver's empty group stays (recorded in the state).
- The departed historical tree is not detached or returned (no such steps in the plan or the code).

## Checks (commands)
- `python -m pytest -q -p no:cacheprovider tests/tradecase/test_c0192_mixed_tree_cleanup.py` → 24 passed (after rework):
  - start conditions and 9 kinds of stops before cleanup;
  - plan order, with no detach;
  - no double tare zeroing;
  - stock scope: another UID, another article, a remainder mismatch, reservations;
  - the full order of commands with two different participants, the exact tare/binding/wave bodies and the replay;
  - foreign stock → no count and no user retirement;
  - wave not ready → stop;
  - incomplete delivery → nothing sent;
  - stock after the count → stop;
  - resume without repeating steps.
- `python scripts/retailcase_quality_gate.py` → PASS; `scripts/check-encoding.ps1` → PASS; `python scripts/check_architecture.py` → PASS.

## Limitations
- **Not run against a live Oracle/API.** Unconfirmed on the target runtime:
  - the field names of `/tare/.../balances` and `/execution` (taken from NS23);
  - the version of the `driver-bindings` answer (when it is missing, 1 is used, as in NS23);
  - `finish-execution` without a disposition for a fully shipped wave.
  - Every deviation stops with a code.
- **Integration (Codex):**
  - the companion zeroes the run's lots itself after delivery. C0190 `cleanup()` must not be run after it (or must take an empty remainder);
  - for C0190's CASE pallet types, the tare is zeroed by C0190 cleanup when it matches the root type;
  - the two mistaken pre-integration ST bindings (ST 643008/643009) are Codex's work; the companion does not create or repair STs.
- **Task encoding:** the first version of `TASK_C0192` arrived with Cyrillic replaced by `?`; the work was done against the English version of the file (28.10 08:21).

## Rework K-0225 (same C0192)
- **What changed:** `retire()` no longer performs direct `RUSERS`/`RIGHTS` DML or the rights API. Before retirement there is a stop **`RETIRE_REQUIRES_DURABLE_OWNER_FINALIZER`**: there is no durable journaled finalizer with read-only reconciliation, and C0190 does not provide one.
- **The `retire` step is not marked done.** What is left is recorded in the state as `c0192.retire_pending`: the users, the receiver group and the `store_receipt_confirm` right.
- **Kept safe steps:** tare return, tare zero, binding off, wave finish, own stock zero. A resume does not repeat them and stops at the same place again.
- **Cleanup is incomplete:** the synthetic driver/receiver and their rights remain until an owner finalizer exists.
- **Tests: 24 passed.** New ones: after the safe steps the stop comes before any SQL (`connect` is not called, no rights API calls); a resume sends no completed command again (API, native post, replay).
- gate, encoding and architecture PASS.
