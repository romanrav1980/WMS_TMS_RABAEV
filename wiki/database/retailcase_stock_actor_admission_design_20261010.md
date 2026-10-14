# Действующий пользователь ядра остатков,152

Stock posting owns common admission; command-specific warehouse/rights checks remain their existing authoritative modules. All existing operation actors have corresponding RUSERS records, no unregistered pseudo-service actor found. Require current non-deleted RUSERS.ID for every command before immutable replay/source compilation and after original lock acquisition.

This adds PK reads, no actor row lock/global physical mutex. Authorization point is admission after waiting for locks; existing per-kind checks unchanged. Do not claim full new per-command permission registry. Existing native API/Python UOW still owns whole commit/rollback, no second transaction or quantity rule.

Native root body-only incremental deployment avoids unchanged spec/guard invalidation. Author deactivates an existing private operation actor only within rollback-only local transaction and submits exact saved native request: reject20882/no result, then restore and replay original exact/no journal. Unknown actor refuses before effect. No new stock or migration actor privilege invented.
