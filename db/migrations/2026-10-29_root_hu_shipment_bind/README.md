# Root-HU shipment binding

This migration permits several CASE children of one root handling unit to reference one prepared ST. It removes only the named legacy unique constraint and keeps a non-unique lookup index. The API verifies one root, one ST, one recipient and exact CASE composition before it writes any binding.

Rollback refuses when an ST already has more than one CASE child. It never deletes bindings or changes shipment history to satisfy a downgrade.
