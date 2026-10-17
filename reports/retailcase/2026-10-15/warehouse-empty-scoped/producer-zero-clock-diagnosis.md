# TEST OPC zero before server claim: diagnosis and bounded correction

Actual root acceptance failed before capture or GROUP ACL mutation. Native `confirm_zero` returned HTTP409 `WH_ZERO_OBSERVATION_OUTSIDE_CLAIM`; this was a correct rejection, not a successful zero or hardware commissioning.

Evidence: [original API diagnostic](first-zero-failure.json). Original request `N1939.EMPTY.1139`, claim `WH.OPC.413e1bfb2a6648ae9f0e0067f628e0df`. Oracle claim created `2026-10-15T17:57:02.488197Z`; saved genuine OPC current-weight server timestamp `17:57:02.463465Z`, observation `17:57:02.467926Z`. The first read after HTTP ACK still contained instrument values preceding Oracle claim creation by20?25ms. All seven Good readings and physical-zero flags are preserved in the local immutable event, SHA256 `67F0B56471ADD2F2151296741F709985CE991F4AC4057E8CAAE2DE90AEFE34B1`.

The producer now waits for an actual zero whose observed_at and every DataValue server_timestamp are within the original server claim window BEFORE durable staging or HTTP confirmation. It rereads, never edits timestamps or weakens native checks. A sustained clock discrepancy fails at the bounded lease deadline without staging a zero. Existing saved events still retry their exact original bytes; they are not replaced by new observations. Source timestamps retain existing native semantics (static metadata source timestamps are not silently relabelled).

Validation:38 focused zero/gateway tests passed, including each of eight stale timestamps, persistent skew/no staging, and lost-ACK exact replay. Architecture1089 files/cycles0/debt72 PASS. Independent store_navigation read-only review PASS. These are software tests, not physical scale acceptance.

Prepared replacement driver `tmp/warehouse_opc_native1939b_empty.py` requires authoritative original request EXPIRED, expiry before server_now, original ZERO/capture absence, exact preserved original body/event hashes and original409 identity before any new POST. It uses separate requestB/runtime/report. Root alone may run it after review. No successful B capture, GROUP quantity proof, or new goods effect is claimed here.
