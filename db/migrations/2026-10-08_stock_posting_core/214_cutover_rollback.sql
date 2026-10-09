-- Do not restore an older executor after any posted command.
-- Before the first command: restore PREPARED and SOFT metadata from the cutover checkpoint
-- under the same exclusive release/config fences and table drain (operator recovery).
declare n number;
begin
 select count(*) into n from RRL_STOCK_OPERATION;
 if n>0 then raise_application_error(-20808,'POSTED_OPERATIONS_REQUIRE_INVERSE_COMMANDS_NOT_CUTOVER_ROLLBACK');end if;
 raise_application_error(-20808,'USE_CHECKPOINT_RECOVERY_WITH_EXCLUSIVE_FENCES; DO_NOT_RESET_RELEASE_BLINDLY');
end;
/
