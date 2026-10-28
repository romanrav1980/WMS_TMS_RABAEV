# Multi-order QC status serialization fix

`RRL_STOCK_QC_GATE.status_json` materializes `slices` before adding it to the response. Oracle rejects passing a transient `json_array_t` returned by `get_array` directly to `put` with ORA-40573.

Rollback restores the pre-fix package body from the preceding multi-order migration.
