-- Old loading sources cannot interpret standalone CASE physical owners; preserve actual facts.
begin raise_application_error(-20886,'STANDALONE_LOADING_REQUIRES_FORWARD_RECOVERY');end;
/
