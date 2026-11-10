# C-0191 — T06/T07 mixed CASE pallet transport and store receipt

Read AGENTS.md, wiki/index.md and current sprint plan. C0190 is released; Codex now owns scripts/c0190_mixed_tree_runner.py and its tests. Do not edit them.

Implement a separate adapter scripts/c0191_mixed_tree_transport.py and focused tests/tradecase/test_c0191_mixed_tree_transport.py. It must accept the existing C0190 Live object/state (warehouse, cases, parent tag.PAL, journal, send/post/read methods) and complete the existing native control/loading/departure/store-receipt flow for one root pallet with KG and EA CASE children, one recipient. Reuse supported API contracts from tests/tradecase/live_nested_shipping.py and current store receipt workflows. Do not import a module that performs live work at import time. Do not split children among recipients.

Deliver actual implementation, not only a plan or unconditional TRANSPORT_NOT_WIRED. Save exact commands before sending; recover lost replies by same operation_id/body. Declare necessary missing fixture inputs in a validated input contract and list them in RESULT. Values provided by the software fixture must be explicitly identified as synthetic; never describe them as physical measurements or production external acknowledgments. Real external ACK prerequisites must remain explicit.

Ownership: only new adapter, its focused tests, reports/tradecase/2026-10-28/claude/C0191/, coordination/retailcase-claude/RESULT_C0191.md. Codex integrates and executes live writes. No Oracle writes, migrations, shared API restart, GitHub push or broad regression runs. Run only meaningful tests of your adapter. Send ACK with paths, then RESULT and RELEASE. Ask only for a blocking missing contract; resolve routine details from current source.

Registered before delivery in claude-budget.json, request 1 of current two-request allocation. Deadline for overall work: beginning of 2026-11-06 Europe/Moscow.