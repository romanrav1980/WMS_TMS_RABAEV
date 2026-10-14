@@../2026-10-08_stock_posting_core/312_checkpoint_hu_task_posting.sql
@@../2026-10-08_stock_posting_core/309_checkpoint_hu_task_commands.sql
@@../2026-10-08_stock_posting_core/310_checkpoint_hu_task_read.sql
@@../2026-10-08_stock_posting_core/311_checkpoint_hu_task_plan.sql
drop package RRL_STOCK_HU_TASK;
/
-- Additive task contract/history retained; restore callers together before recovery.
@@../2026-10-08_stock_posting_core/014b_recompile.sql
