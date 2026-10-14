# NI05.3 — принятое исполнение заказа
Ticket090: reuse existing RRL_CUSTOMER_ORDER_FULFILLMENT/project_ship and immutable original shipment RESOLVED_PLAN_JSON. No second preparation/assignment/stock writer or overwrite of original ORDER_QTY/SHIPPED facts.

Bounded read-only Oracle snapshot joins actual existing fulfillment/ST/source load/receipt and original shipping legs. Credit quantities to the original frozen customer_order_id, article, BASE_UOM and UID. Report accepted/missing/refused/damaged/unreceived separately; never sum different SKU/UOM into one amount. Preserve all historical load links, even inactive: confirmed acceptance remains history after future unloading.

Single original owner per leaf permits exact receipt totals. A whole accepted leaf can retain exact original per-owner shipped quantities. A partially accepted leaf with several original owners cannot be arbitrarily distributed: report needs_owner_allocation and leave accepted credit unresolved. Missing or inconsistent original source also prevents a fabricated credit.

Expose customer order delivery progress alongside existing warehouse execution API/UI. Received shipped volume is distinct from completion of the entire original requested order: unshipped/planned fulfillments and unresolved cases remain visible. Accepted portion is final receiver fact, remainder remains logistics obligation. No mutation of warehouse stock or old receipt; industrial/customer order line allocation and approved return/redelivery remain follow-ups.
