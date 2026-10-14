-- Older placement sources cannot interpret measured stock claims or move an empty carrier.
-- Preserve existing placement/history; use a forward repair from source revisions071/074.
begin raise_application_error(-20886,'STOCK_LEAF_PLACEMENT_REQUIRES_FORWARD_RECOVERY');end;
/
