# Единый идентификатор профиля маркировки

655–658: live RRL_SKU_RECEIPT_PROFILE/RRL_WMS_RECEIPT_AGG.PROFILE_CODE and stored Oracle resolvers support80 bytes. Card and manifest accepted80, but aggregation/store/inventory-count/task-draft API schemas rejected names longer than60. This could make a valid configured profile unusable at a later scanner step.

Shared MarkingProfileCode in master_data/contracts.py now governs card, trace manifest, aggregation scanner, store receipt/return custody, inventory count and task scan. API accepts up to80 UTF-8 bytes; longer ASCII or multibyte values fail before Oracle. No duplicate identity validator or schema/quantity change. Native current profile/version/full composition rules still apply.

Targeted contract check: ASCII80 and Cyrillic40 accepted; ASCII81/Cyrillic41 rejected. Architecture677/0cycles/76debt and current native VALID. This is boundary evidence; no new government/profile semantics or external ACK claimed. Existing SQL/read bounds unchanged.

ReturnMarkPanel and raw return draft support removing the last scan for the selected profile and selected UNIT/BOX/PALLET mode without clearing other scans. Source/actor/API-scoped persistence and saved pending-command immutability remain. JS and frontend typecheck passed; no broad regression needed for this reversible draft action.
