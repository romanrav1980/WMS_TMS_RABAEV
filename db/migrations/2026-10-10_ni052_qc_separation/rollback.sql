-- Re-enabling QC auto shipment would bypass physical loading and strand trips.
begin raise_application_error(-20886,'QC_PHYSICAL_LOADING_REQUIRES_FORWARD_RECOVERY');end;
/
