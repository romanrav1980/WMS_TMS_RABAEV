# NI06.2 — конкретный возврат поставщику через существующую СТ,108
Owner inventory, transaction owner original Root for physical LOAD_SHIPMENT; metadata preparation uses existing outgoing_pallet_edit metadata fence and PALL_SPLITTER.create_return_task/add_row_2sborka_pallets. SC role/store_return_approve chooses actual unique supplier INN with explicit decision, actor warehouse-bound; metadata and source mapping one commit and exact operation hash. No second ST/quantity engine.

Immutable mapping pins placed SUPPLIER return receipt/physical UID/warehouse/exact whole unreserved quantity to existing prepared supplier ST. Original source document/decision remains. Source descriptor is reused by existing single loading preview/confirm and original shipping core. Existing RETURNS fallback remains for old untyped supplier STs.

Typed source permits consuming its segregated blocked location only under actual Root LOAD_SHIPMENT + dispatch permission/current same warehouse/source match. One native consume/journal/outbox, actual load/TT/vehicle/dock/measurements. Direct logical SHIP cannot impersonate physical load. Dispatch is warehouse exit; it is not confirmed receipt by supplier/SAP ACK. Store receipt must reject supplier cargo.

Immutable dispatched source and SAP pending event retain original return/source/INN and operation. Supplier acceptance is next distinct fact. Preserve existing QC; ordinary scope initially, required marking denied until exact return regulatory/units path.
