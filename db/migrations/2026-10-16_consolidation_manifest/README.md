# Expected consolidation manifest - PREPARED, not applied

Fulfillment owns logical expected ST membership. Three new metadata/receipt
tables, two native packages, three owner triggers and one HU_SHIP body hook.
Existing physical HU links, quantities, CASE/ST/quality and loading owners stay.
Plan references1..200 existing prepared fulfilments, at most200 ST rows each /
2000 rows total. Source can remain PLANNED; no physical receipt is fabricated.
Target warehouse_task_execute and current source-view authority are checked
before replay and under rights REV -> CONFIG6 -> metadata resource fences.
SELF without an authoritative owner is not a planning grant. Exact commands
retain immutable receipt/frozen expectations; current version and source ST
reference/signature prevent silently changing the expected order.

Current physical root readiness checks actual location, exact ST membership,
bound CASE/STOCK identity and changed ST rows. Missing/extra/unknown leaves
block HU_SHIP before child QC; compiled expectation token is rechecked under
the existing CONFIG4/stock/CASE locks. No active plan keeps the legacy path.
This gate never grants quality release or declares measured mass. SHIPPING_GROSS
candidate must include this token before its future installation.

Checkpoint pins8 existing sources,4 new package sources and3 triggers; before
namespace/schema guards and exact after hashes. Source before image and paired
rollback included. Rollback refuses ANY retained plan/receipt/member metadata;
history is not deleted. Revert the new Python consumer before an empty rollback.
Current author review only, native apply/API functional acceptance pending.
