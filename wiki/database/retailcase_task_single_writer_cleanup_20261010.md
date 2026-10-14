# Единственное завершение задания и SAP metadata scope,146

Removed unused WarehouseTaskService._complete_task_locked PREPARED completion branch and exclusively-used Python scan/quantity/resource fallback. No other source caller found. Live complete_task still enters inventory public/native root; live assign/start/cancel sync preserved. Sole physical writer remains RRL_STOCK_POSTING_API. Three cutover-boundary cases PASS, old handlers never invoked in inactive release states.

Receiving SAP cancel takes its own original metadata UOW before ordinary wrapper, so144 wrapper scope alone did not cover this route. Corrected source and earlier completeness implication: native144 access adapter now checks current actor in Receiving.cancel and replan before document lookup/replay and again after task lock. Original document/claim/outbox cancellation is unchanged; no nested UOW introduced. Native20882 converted PermissionError and old replan API/SAP-cancel legacy facade403. Permission and receiving document state remain existing rules.

ReplanPutaway scanned pallet max150 and exact saved internal ID comparison first; optional SSCC normalization only for nonmatching alternative representation. Internal42-character example accepted in DTO unchanged. Not a claim of real replan execution for a new receipt.

Author ni081_receipt_scope_existing_case.py executes adapter actual admin/task829 permitted, actual135 foreign actor refused PermissionError; no writes. No active SAP placement fixture present and no suitable nonadmin metadata rights actor found; did not create new physical receipt just for checking. Actual full SAP cancel/replan acceptance remains Qwen task. Existing cutover tests3 PASS.

Architecture after removal489files/0cycles; remaining code debt not accepted/threshold not raised. Native144 keyed scope timing applies, no new Oracle SQL budget rule or migration. NS59 physical ranges/calendar/joint schedule validation remain open.
