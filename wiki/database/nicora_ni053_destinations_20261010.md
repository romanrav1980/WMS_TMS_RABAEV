# NI05.3 — неизменный адрес физического места
10.10.2026.082 APPLIED RABAEV/orcl. Transport physical load owns frozen destination, existing ST/ADDR remains source before loading.

RRL_TT_HU_LOAD_ST.DESTINATION_ADDR copies exact255-byte legacy ADDR. Compiler freezes each actual ST/address, finish_load rechecks after real ST locks then writes immutable member address. Empty destination refuses. Loaded-ST guard also forbids changed ADDR, without acquiring TT late. Future store receipt uses frozen destination, not mutable current ST/address. Previous immutable physical load members stay NULL; no automatic historical inference or backfill.

Existing loading measure origin now explicitly rejects NULL in raw root calls. Reconciliation API original operation identifier is bounded100, separate request subtype. Source checkpoint381, versioned082, installed package objects VALID. Targeted positive frozen-address and changed-address refusal will be exercised together with the next store-receipt functional slice; no acceptance claimed yet. Full NI05.3 not implemented.

Author082/083 fixture04633c677f now confirmed actual frozen STORE.QA destination and loaded/departed address mutation refusal, then full ordinary receipt3. See [[nicora_ni053_store_barcode_20261010]] for continued-case limits.
