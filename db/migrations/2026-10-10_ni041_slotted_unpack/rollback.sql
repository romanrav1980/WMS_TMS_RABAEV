@@../2026-10-08_stock_posting_core/348_checkpoint_slotted_unpack_command.sql
@@../2026-10-08_stock_posting_core/349_checkpoint_slotted_unpack_slot.sql
@@../2026-10-08_stock_posting_core/350_checkpoint_slotted_unpack_root.sql
@@../2026-10-08_stock_posting_core/351_checkpoint_slotted_unpack_reserve.sql
@@../2026-10-10_ni041_hu_slots/006_guard.sql
@@../2026-10-10_ni041_hu_shipping/006_link_guard.sql
@@../2026-10-10_ni041_hu_shipping/008_container_guard.sql
@@006_claim_guard_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-069-slotted-hu-unpack';
commit;
/
