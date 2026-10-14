# NI05.3 — фактические количества и открытые обязательства
Ticket086 design10.10.2026, installed APPLIED; see [[retailcase_ni053_discrepancy_20261010]]. Sources process10_store_receipt, NS49/NS52 partial acceptance and remainder logistics.

Extend ordinary BARCODE receipt with explicit per-original-leaf BASE disposition: accepted + missing + refused + damaged = immutable shipped quantity. Reported excess is separate and never added to known accepted or warehouse stock. Require complete unique source leaf coverage and reason when any discrepancy/excess exists. Existing full-place request remains compatible; defaults must not alter old canonical replay.

One root transaction: immutable receipt/lines, discrepancy case, per-line missing investigation/refused/damaged return-decision/excess review obligations and existing outbox. Original shipped quantity/history/P/H unchanged. No automatic return, loss write-off, guessed SAP return authority or source mutation. Logistics can see open responsibilities; physical return and approved decision are later explicit commands.

Target author case uses own actual shipped/departed ordinary place: accepts2 of3, missing1, reason; P/H0, immutable lines/source/outbox, one open investigation obligation. Excess reporting separate, mismatched totals/foreign or duplicated leaf/missing reason denied, exact replay and duplicate receipt protected. Marked and WEIGHT_PHOTO still require their separate mandatory flows.
