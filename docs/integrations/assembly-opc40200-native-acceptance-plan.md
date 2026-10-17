# Assembly gateway → live API acceptance plan

Scope: TEST transport/integration acceptance after the assembly and raw1.1 migrations are APPLIED/INVALID0. The OPC server is a local encrypted protocol fixture, not physical equipment. Production API routes and actual Oracle validation remain in the path. Native positive quantity/posting acceptance runs separately inside caller rollback.

## Isolation and activation

1. Coordinate a no-DDL test window with root and inventory owner. Save counts for stock operations, assembly use, raw evidence and captures, actual package hashes, ledger and INVALID baseline; record the slow-SQL marker.
2. Inventory owner provisions a uniquely tagged TEST CASE, ordinary explicit EA SKU, scanned source/carrier and dedicated non-admin sender bound to the actual warehouse/station. Carrier uses the official simulated label owner; record SIMULATED_TEST_LABEL_NOT_PHYSICAL. Station policy is explicit; no policy on a shared station is altered. Initial EMPTY_TARE is explicitly TEST evidence under the actual native schema, never claimed physical.
3. Temporary permissions/users/configuration and their cleanup are owned by the fixture author. Immutable capture/session/policy/audit history remains truthfully tagged TEST; do not bypass guards to erase it. Snapshot P/H/version and existing business facts before any gateway cycle.

## Actual path, without a stock commit

4. Start the real localhost asyncua server fixture with fresh certificates and explicitly mapped Scales V2 WeightType and seven required DataValues. Use actual SignAndEncrypt client, pinned certificate, real server timestamps and a shared physical-device lease DB. Configure the dedicated TEST sender only through environment; never log credentials.
5. Native operator opens a session and a step with explicit quantity/scans/consent. Actual GET `/api/inventory/assembly-scale/gateway/requests` must return its fixed BEFORE capture ID, original tare key and current policy/calibration.
6. Let genuine fresh OPC Read results form the BEFORE window at the admitted baseline. Send with the production HTTP adapter. Validate the real native archive ACK/hash/weight and state ARMED; verify no step-use/stock operation exists. Deliver raw1.1 and require MATCHED with the exact session/step/BEFORE/tare reference.
7. Default no-stock-commit AFTER test uses a stable positive mass change deliberately outside the configured SKU delta policy (above minimum change so the gateway can observe it). For BUTTON mode, operator first records actual TEST placement intent. The actual native result must be DISCREPANCY and session BLOCKED, with capture/raw MATCHED and no stock posting. This is a negative mass-admission test, not a successful physical assembly claim.
8. Replay the exact staged bodies and immutable raw evidence using the original IDs; compare archive hashes/keys and no extra rows. Verify raw wrong phase/tare reference, wrong sender and changed body fail against actual native endpoints. Keep all failure responses as evidence.

## Separate positive proof and risks

A valid in-range AUTO AFTER or BUTTON READY sent to production HTTP calls `deliver_assembly_step`, which invokes the existing StockPosting writer in a fresh committed transaction. It must not be used in a default rollback-only test. The positive native runner instead performs genuine prepare/execute with caller rollback and verifies movement/quantity/step-use/domain effects disappear together. A positive HTTP commit needs an explicitly selected isolated test fixture and an agreed stock/audit outcome.

Concurrent duplicate native captures can both miss the preflight archive lookup: the waiter may receive a phase/state conflict after the first request wins. State plus unique keys prevent duplicate archive/posting; a later exact retry returns the saved archive. Record this as a retry behavior limitation and test it before a distributed pilot.

No conclusion about instrument metrology, physical labels, operator ergonomics or throughput follows from a local protocol fixture. Hardware commissioning still needs actual model profile, stable/zero signal mapping, unit, calibration and transport interruption acceptance.

## Completion evidence

Save exact counts before/after, package readback/INVALID, HTTP/native ACKs without secrets, both outbox identities, raw1.1 binding, current business states, P/H/version equality, fixture cleanup/retained TEST history and fresh slow SQL. Every query above500ms repeated or1000ms single receives a bounded-query/index/plan/backlog decision. Root owns final index/log and release integration.
