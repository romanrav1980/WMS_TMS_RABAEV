# Multi-order QC JSON value fix

The multi-order QC status code materializes JSON arrays and objects before adding them to another JSON object. Oracle rejects temporary JSON values passed directly to `put`.
