# CASE-aware interwarehouse bridge - PREPARED

Existing grouped native receipt creates physical HU continuation for shipped CASE; original picking, ASM, ST/fulfillment and tare books remain history. Same stock/unit identities received once. One source ST can own several receipt leaves. Additive metadata map and bounded owner changes. Rollback refuses retained CASE/multi-leaf history; use forward recovery after physical facts. See wiki/database/retailcase_interware_case_bridge_20261016.md. No SAP publication or external ACK.
