-- Restoring an unlocked writer would invalidate departure membership guarantees.
begin raise_application_error(-20886,'TRIP_ASSIGNMENT_REQUIRES_FORWARD_RECOVERY');end;
/
