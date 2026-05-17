prompt [migration 2026-05-17-018] safe rollback

prompt This migration creates data-bearing wave picking objects and hard-reservation workflow.
prompt Automatic rollback is intentionally non-destructive and keeps tables, packages, rights, and data.
prompt Use a VirtualBox/database snapshot for a full physical rollback.

select '018 rollback is intentionally no-op' MESSAGE
  from dual;
