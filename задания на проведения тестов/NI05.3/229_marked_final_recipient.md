# Qwen:229 — уникальные QR у окончательного получателя
Новая собственная полная standalone маркированная source->pick/QC/load/depart->225manifest->226receipt->227putaway->228onward/depart. Уже принятый STORE229.RECEIVE:13508027ed0/order2030 не повторять.
1. КарточкаSKU=current mandatory UNIT profiles; physical3/codes6(two synthetic systems) quantity3 not6. Profile version/code canonicalization/shared hash exact; не считать синтетическую комбинацию реальной применимостью ГосACK.
2. Store preview scoped current receiver/address, supported singleSTOCK/current issued fingerprint/sourceversions/profiles/expectedScanCount. Wrong/missing/duplicate/foreign tuple rejects; current aggregation unsupported explicit. Default old ordinary body hash/replay preserved.
3. Full accepted only. Marked partial/missing/refused/damaged/extra ->STORE_MARKED_DISPOSITION_UNIT_ASSIGNMENT_REQUIRED without fact/outbox/stock; дальнейший per-unit scope отдельный.
4. Native outerrollback after execute removes receipt and derived rows; two different IDs concurrent ->one winner; exact replay saved; sameID changed content conflict.
5. Current receiver address binding removed under existing configuration context ->saved replay403; inactive account ->403; restore own binding ->same result. Не raw-delete guarded configuration.
6. Original shipped quantity3/customer fulfillment unchanged; final accepted3/unreceived0/order delivery lineage originalfirstload->actualsecondload. Store stock journal events0/same3issued units/codes unchanged/no unit inserts/GovACK.
7. React original StoreAdmission uses profiles/QR Enter/bounded draft/source+receiver+profile versions, quota error before state, optional scans saved intent/retry/auth/source switch; unsupported sources disabled. TypeScript both apps must pass.
8. SlowSQL: source code index/10k units/20k scan matrix/current profiles<=50/source unique; explicit index/bound/plan decision.
