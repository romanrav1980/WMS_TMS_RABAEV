declare n number;v varchar2(20);begin
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_OBJECTS where STATUS!='VALID' and
  OBJECT_NAME in('RRL_STOCK_RECEIPT_REVERSE','RRL_STOCK_INV_ENTRY','RRL_STOCK_METADATA_TX','RRL_STOCK_TRANSFER_CORE','RRL_STOCK_POSTING_API',
  'RRL_ACCEPT_ORDER2','RRL_ACCEPT_ORDER2_2','RRL_ACCEPT_ORDER2_3','RRL_ACCEPT_ORDER3','RRL_OTKAT_ORDER2');
 if n>0 then raise_application_error(-20808,'CURRENT_COMMAND_PACKAGES_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-047-receipt-reverse' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Receipt reversal: history preserved, stock/reserve/unit checks and SAP outbox',sysdate,user,'133_receipt_reversal_apply.sql','133_receipt_reversal_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-048-receipt-reverse-sender' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'SAP reversal sender and document identity',sysdate,user,'134_receipt_reverse_sender_apply.sql','134_receipt_reverse_sender_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-049-receipt-reverse-history' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Receipt reversal rejects consumed original lots',sysdate,user,'135_receipt_reverse_history_apply.sql','135_receipt_reverse_history_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-050-native-inventory' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Native inventory functions use explicit inventory commands',sysdate,user,'138_inventory_native_apply.sql','138_inventory_native_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-051-inventory-lot-entry' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Explicit lot count and native BOX count adapter',sysdate,user,'140_inventory_lot_entry_apply.sql','140_inventory_lot_entry_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-052-receipt-metadata-fence' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Receipt replan/cancel serialized with physical commands',sysdate,user,'143_metadata_fence_apply.sql','143_metadata_fence_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-053-physical-unit-repack' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Physical unit UID rebinding; external composition proposal remains pending',sysdate,user,'145_physical_unit_repacking_apply.sql','145_physical_unit_repacking_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-054-repack-outbox' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Generic StockPosted publishes pending repacking composition',sysdate,user,'146_repacking_outbox_apply.sql','146_repacking_outbox_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-055-receipt-retirement' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Automatic receipt/delete paths replaced by SAP scan workflow',sysdate,user,'147_receipt_retirement_apply.sql','147_receipt_retirement_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-056-receipt-origin-inventory-expiry' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Reversal requires admitted origins; inventory expiry conflict rejected',sysdate,user,'148_receipt_origin_inventory_expiry_apply.sql','148_receipt_origin_inventory_expiry_rollback.sql','APPLIED');
commit;
