-- No database/VM copy or new data archive was requested or created.
-- DELETE is rollbackable before commit. After the authorized commit the old test facts are intentionally removed.
begin
 raise_application_error(-20808,'DEV_RESET_IS_IRREVERSIBLE_AFTER_COMMIT: old stock/movements are not reconstructed');
end;
/
