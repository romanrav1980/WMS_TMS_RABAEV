-- Diagnostic only: no DML or DDL. Expected process exit 1, no unhandled exception.
begin
 raise_application_error(-20899,'ORACLEAPPLY_CONTROLLED_ERROR');
end;
/
