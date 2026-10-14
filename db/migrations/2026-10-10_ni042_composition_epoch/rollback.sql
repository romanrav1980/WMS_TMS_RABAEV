-- Removing the monotonic composition epoch can resurrect invalid quality approvals.
-- Checkpoints 358..361 are diagnostic evidence, not a safe live rollback.
-- Recovery must preserve counters and QC v2 and install a forward corrected coordinator.
begin
 raise_application_error(-20886,'COMPOSITION_EPOCH_REQUIRES_FORWARD_RECOVERY');
end;
/
