# Installed verification correction ? PREPARED finish only

Root applyv4 installed all seven exact native sources; current errors0/globalINVALID0/tombstones0, but verification stopped before ledger at RESOURCE_INTENT_VALID_UNIQUE_INDEXES. Actual evidence actual-indexes.json shows two NORMAL unique VALID PK/UK indexes and three LOB indexes that are ALSO UNIQUE/VALID. The author's uniqueness-only exclusion was incorrect; the stopped attempt is preserved.

verify_installed_indexes.sql changes only that count: join table P/U constraints via INDEX_NAME+INDEX_OWNER to USER_INDEXES, require NORMAL/UNIQUE/VALID, exactly2. Earlier exact single-column PK, named domain+original unique two-column identity, constraints/FK targets/NO ACTION, enabled trigger, source7exact, current non-BIN errors including warnings/globalINVALID and package context-binding checks remain unchanged. No LOB status/uniqueness inference is used.

apply_after_installed.sql runs corrected complete verification and only then the original migration ledger MERGE/commit, identifying this finish entry. It does not repeat any DDL/business package body or drop/recompile objects. Root alone executes after independent review; author ran no SQL/native call. Original frozen and reviewed-v1/v2 files/manifest chains are untouched.
