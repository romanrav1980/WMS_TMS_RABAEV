# Qwen: NI05.3/088 — физическая коробка в погрузке
Read wiki/database/nicora_ni053_load_boxes_20261010.md. Use own ordinary HU with actual BOX identities, current tree, stock and existing assigned ST/trip/dock. No guessed SKU carton norm.

Configure destination WEIGHT_PHOTO. Root loading without physical_boxes refuses. Provide complete occupied innermost BOX list, actual scan/version/final gross KG/manual measurement reference. Successful API load freezes exact box rows alongside shipment/ST; replay same original API body creates none again; separate departure consumes no P/H. Reader returns half lightest actual gross box, including small incomplete box.

Refusals: foreign/duplicate/missing/empty/overlapping box, changed content version/wrong scan, gross below tare/KG stock, whole gross below sum boxes+outer tare; CASE/unboxed layout must not infer fake physical cartons. Validate nested outer BOX handling with no double count. Direct update/delete frozen mass must fail. Barcode destination can omit proof, old proof-free load cannot be backfilled by later policy switch.

Real browser raw loading UI: individual masses/scans/reference, no float arithmetic, exact pending-body retry after unknown answer. API producer preserves omitted optional fields for old replay. Direct SQL and API fixture byte formats differ; test original producer replay, do not rewrite prior request history.

Keep evidence of operator manual declaration separate from physical scale/calibration acceptance. Own P/H cleanup solely Root, preserve immutable load/box/history. Largest changed SQL and explicit decision in report.
