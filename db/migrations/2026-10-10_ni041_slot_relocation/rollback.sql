@@../2026-10-08_stock_posting_core/353_checkpoint_same_cell_hu_command.sql
@@../2026-10-08_stock_posting_core/354_checkpoint_same_cell_hu_slot.sql
@@../2026-10-08_stock_posting_core/355_checkpoint_same_cell_hu_root.sql
@@../2026-10-08_stock_posting_core/356_checkpoint_same_cell_hu_reserve.sql
@@../2026-10-10_ni041_slotted_unpack/004_unpack.sql
@@../2026-10-10_ni041_slotted_unpack/006_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-071-hu-slot-relocation';
commit;
/
