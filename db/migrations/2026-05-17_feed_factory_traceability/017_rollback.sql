prompt [migration 2026-05-17-017] safe rollback

prompt This migration creates data-bearing pick topology objects and recompiles RRL_PICKING_API to use them.
prompt Automatic rollback is intentionally non-destructive and keeps tables, packages, columns, rights, and data.
prompt Use a VirtualBox/database snapshot for a full physical rollback.

select '017 rollback is intentionally no-op' MESSAGE
  from dual;
