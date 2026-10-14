-- Existing reconciled loads require this source link and command history.
begin raise_application_error(-20886,'LOAD_RECONCILIATION_REQUIRES_FORWARD_RECOVERY');end;
/
