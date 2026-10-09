-- Single OracleApply invocation after scripts/stock_posting_install.py prerequisite preflight.
-- Never includes administrative grants or activates release.
@025_command_schema.sql
@016_locking.sql
@017_context.sql
@018_balances.sql
@019_operations.sql
@020_reservations.sql
@021_location.sql
@022_command_plan.sql
@023_manual_move.sql
@024_posting.sql
@027_policy_catalog.sql
@026_complete_install.sql
