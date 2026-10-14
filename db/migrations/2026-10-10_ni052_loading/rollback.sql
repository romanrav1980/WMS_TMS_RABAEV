-- Physical facts are immutable evidence; old close_task/can_print cannot safely approve departure.
begin raise_application_error(-20886,'PHYSICAL_LOADING_REQUIRES_FORWARD_RECOVERY');end;
/
