# NI05.3 — неизменяемый фотоархив
10.10.2026.085 APPLIED RABAEV/orcl. Pure delivery evidence metadata, outside physical quantity/receipt transaction. Existing actual APPLIED departed load, frozen store and RUSERS receiver authorization reused.

Original JPEG/PNG bytes are deduplicated in RRL_STORE_MEDIA_ASSET by SHA256; immutable RRL_STORE_RECEIPT_PHOTO links load/store/view/actor/server time to asset. Package computes actual BLOB hash and compares bytes on duplicate hash, serializes per-load photo cap12, never commits inside Oracle routine. Secure separate photo context guards append-only assets/associations; registration inside a stock operation refuses. Retrieval authorizes current receiver and verifies recovered bytes/hash; immutable evidence can be supplementary to an earlier barcode receipt and does not rewrite its original admission.

Decoder Pillow12.3.0 pinned/installed from cached wheel. Image.open is lazy, so verify plus bounded load are used; only one JPEG/PNG still frame,4MiB/12M pixels, minimum useful dimensions. Original bytes are unchanged. [Decoder primary reference](https://pillow.readthedocs.io/en/stable/reference/Image.html).

API /api/delivery/store-photos upload/list/photo_id/content. Raw incoming image stream is capped in audit middleware before decoder and endpoint; Starlette bounded body cache forwards exact bytes. Audit stores byte count/hash descriptors rather than binary-as-text, marks photo traffic nonreplayable; oversized retained-prefix hash is explicitly marked truncated. Download keeps original MIME/ETag/nosniff and private no-store.

Existing DriverMobilePage receipt panel now uploads camera/file sides and downloads original archive through current authenticated receiver. Password remains in memory, source/account changes suppress stale results. Weight/photo admission is still separate; archive alone does not approve receipt or fabricate government ACK. Human UI messages map technical rules to actionable text, API rule/error envelope remains compatible.

scripts/ni053_photo_archive_case.py passed actual PNG/JPEG/three views, identical source/file retry, exact original HTTP bytes/hash/ETag recovery, foreign address, invalid image, MIME mismatch,4MiB limit, direct association delete refusal. Actual API audit hash/metadata/replayable0 verified, own source P/H0. Color raster fixtures demonstrate technical archival only, not physical industrial photographs or full NS52 acceptance. Frontend local tsc passed.

Slow SQL4yf0vb8guns9g bounded photo list8.150ms/4; catalog/schema74–246ms excluded runtime. Keep load/store/time index, cap12 and SHA/source unique PKs; no extra speculative index. Explicit storage cost: BLOBs consume Oracle space, production image volume/recovery/object-store transition belongs NI08/operations owner. Quantity posting transactions contain photo IDs in future weight slice, never image blobs.

Versioned085 and forward-only archive preservation. Remaining NI05.3: actual stable-scale source, confirmed physical-box mass/tolerance, mandatory weight+photos, discrepancy/partial/return obligation, marked recipient/ACK and independent browser acceptance.
