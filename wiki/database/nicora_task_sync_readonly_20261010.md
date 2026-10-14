# Повтор синхронизации читает проведение,147

WarehouseTaskDomainSyncService now ACTIVE-only native committed proof reader. Removed PREPARED escape and exclusively-used old domain mutation/replenishment/MES retry executor; obsolete task_stock_move.py and task_reservation.py plus call-free inventory public wrappers removed. Original sync list/detail/retry/dispatch interfaces retained, no history deletion. Native root atomically owns stock/reserve/domain/SYNCED.

Inactive release503; ACTIVE without matching APPLIED operation/task quantity/pallet/source-target and SYNCED fact409 TASK_POSTING_REQUIRED. Existing HU unpack/relocation/completion proof variants retained. Retry cannot create legacy event/reservation/MES/wave effect or fake repair. Compatibility trigger configuration unchanged/defaultoff. Business document status PREPARED elsewhere is not release bypass.

Seven bounded cases PASS: task completion inactive3, sync inactive3, active missing proof refuses without writes/transaction. Actual ni032_sync_readonly_existing_case.py original120 task829 retry twice same HTTP proof, complete event1 qty3, all stock/sync attempts/timestamps unchanged. No new fixture.

Proof SQL mean21.036ms/2, other12.758ms/1. Decision keep original task/operation keyed lookup/exists and current proof variants, no history scan expansion or new index. Not load benchmark. Independent Qwen acceptance remains open.
