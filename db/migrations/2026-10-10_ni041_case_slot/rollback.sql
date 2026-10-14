-- Older sources cannot interpret CASE claims. Preserve existing task/claim history.
begin raise_application_error(-20886,'CASE_SLOT_REQUIRES_FORWARD_RECOVERY');end;
/
