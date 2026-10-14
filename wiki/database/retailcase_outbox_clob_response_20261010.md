# Большой исходящий ответ сохраняется как CLOB,159

RRL_OUTBOX_DELIVERY_API.finish_attempt now extracts response_json with native JSON_OBJECT_T.get_clob, not get_string VARCHAR2<=32767. Same event/request/hash/lease/generation/atomic finalize and local response recovery remain. No payload decoding/rounding/reserialization inside original response string. Versioned migration2026-10-10_outbox_clob_response body-only1 statement, specinterface unchanged/live USER_ERRORS empty/currentcontract manifest replaced/fullbundle generatedonly. Old154 source evidence retained.

Actual own2308/Q159_cd12a920b9 simulated response40077chars/80077UTF8bytes, Cyrillic40000chars and exact38digit decimal text: stored original RESPONSE_JSON byte-equivalent text, requestDONE200/hash64/eventDONE, mocknotlegalACK/stockjournalunchanged. Explicit body journal bound8MiB unchanged. This is no realprovider/production batch limit proof.

Traceability event list/detail render aware LEASE_UNTIL explicitUTCtext, preserving offsetratherthan drivernaive timestamp presentation. Legacy DATE nextretry/created remainlegacy, not declaredUTC. Adapterrequest CLOB and nativefinalization contracts preserved. SQL finish11.456ms/20, requestPKlock0.449ms/20/hash0.362ms/16; same indexedshortUOW retained/no newindex. Architecture513/0/79PASS. Provider outcome classification and legalACK separation unchanged.
