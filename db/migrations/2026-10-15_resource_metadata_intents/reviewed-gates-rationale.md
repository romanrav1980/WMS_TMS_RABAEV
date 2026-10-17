# Reviewed USER_ERRORS gate wrapper ? PREPARED

Original frozen manifest SHA256:4f12af11e4fd524f28f0cd6ecf846a10679121e415045a2cabeb984ecd7945b3. All26 original files remain byte-for-byte unchanged. Root applyv3 stopped in before.sql before any DDL at RESOURCE_INTENT_BEFORE_ERRORS. Root evidence before-errors-read.json contains only BIN$ recycle-bin trigger errors; current globalINVALID0/newobjects0 was separately reported by root. Author did not execute SQL/DDL/native calls.

Only USER_ERRORS counting is narrowed to NAME not like BIN$%. No ATTRIBUTE filter is added: every current non-BIN$ diagnostic row, including warnings, still blocks. Existing exact4before/7after source checks, namespace, ledger, globalINVALID, table/PK/UK/FK/index/trigger and context binding guards remain unchanged. No recycle-bin purge, object cleanup, error suppression by module prefix, or altered business body is authorized.

New apply_reviewed.sql uses before_current.sql and verify_current.sql, reusing every original frozen schema/spec/body/guard. Ledger paths identify the reviewed entry. rollback_reviewed.sql retains exact-applied-source and empty-history refusal and uses rollback_verify_current.sql. Original failed attempt and frozen files are preserved as evidence. Root alone reviews/applies the new entry sequentially; partial completion is never inferred as success.
