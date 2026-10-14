create or replace trigger RRL_STORE_MEDIA_ASSET_GUARD before insert or update or delete on RRL_STORE_MEDIA_ASSET for each row
begin
 if not inserting then raise_application_error(-20863,'PHOTO_ORIGINAL_ASSET_IMMUTABLE');end if;
 if sys_context('RRL_STORE_MEDIA_CTX','TX_ID') is null or sys_context('RRL_STORE_MEDIA_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_STORE_MEDIA_CTX','ASSET_HASH') is null or sys_context('RRL_STORE_MEDIA_CTX','ASSET_HASH')!=:new.SHA256 then raise_application_error(-20863,'PHOTO_ARCHIVE_PACKAGE_REQUIRED');end if;
end;
/
create or replace trigger RRL_STORE_PHOTO_SOURCE_GUARD before insert or update or delete on RRL_STORE_RECEIPT_PHOTO for each row
begin
 if not inserting then raise_application_error(-20863,'PHOTO_ORIGINAL_ASSOCIATION_IMMUTABLE');end if;
 if sys_context('RRL_STORE_MEDIA_CTX','TX_ID') is null or sys_context('RRL_STORE_MEDIA_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_STORE_MEDIA_CTX','PHOTO_ID') is null or sys_context('RRL_STORE_MEDIA_CTX','PHOTO_ID')!=:new.PHOTO_ID
  or sys_context('RRL_STORE_MEDIA_CTX','ASSET_HASH')!=:new.ASSET_SHA256 then raise_application_error(-20863,'PHOTO_ARCHIVE_PACKAGE_REQUIRED');end if;
end;
/
