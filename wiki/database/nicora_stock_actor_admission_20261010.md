# Действующий пользователь ядра остатков,152

Common root admission now requires current nondeleted RUSERS ID before immutable replay/source compilation and after original resource locks. PK reads only; no extra actor row lock or global physical mutex. Command-specific warehouse/rights rules remain current modules; this is not a full new permission registry. Native/Python command owners retain whole commit/rollback.

All recorded operation actors have existing RUSERS records; no unregistered service principal invented. Actual current nonadmin active old operation actor unavailable, so author uses original admin SAP receipt with rollback-only DELETED=1 on own connection. Exact saved request rejected20882 STOCK_CURRENT_ACTOR_REQUIRED; missing actor rejected; rollback restores admin and exact original receipt replay returns same result/event count unchanged. No persistent user/stock change. Actor-change-during-lock-wait independently verify.

Migration2026-10-10_stock_actor_admission body-only1 statement/live spec+bodyVALID, unchanged spec avoided trigger invalidation. Full source/spec+body replaces current manifest component; bundle generated only. Explicit compatibility setting unchanged; callers require registered active user/service principal rather than implicit admin.

SQL current actor related keyed count first11.181ms and repeated observed cursor0.113ms/10508, not full workload benchmark. Decision retain PK lookup/no actor lock; do not infer million-operation capacity. Source/direct API permission and replay warehouse audits remain separate. No full sprint acceptance.
