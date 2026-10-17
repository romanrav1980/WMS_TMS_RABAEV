# Reviewed gate v2: explicit UTF8 without BOM

Root requested an additive chain after a BOM comparison/blocking issue before DDL. New wrappers are built from original frozen bytes after stripping only the file-initial U+FEFF marker, before prepending the new comment. All v2 files are written as UTF8 bytes without BOM; assertions prove no U+FEFF occurs anywhere in them. Frozen original26 files and reviewed-v1 six files/manifest remain byte-identical. Business DDL bodies are reused verbatim.

The gate semantic delta remains only USER_ERRORS NAME not like BIN$%. Current non-BIN diagnostic rows, including warnings, still block. Before4/after7 exact source, globalINVALID, object/schema/PK/UK/FK/index/trigger/context checks, rollback empty-history refusal and ledger logic are retained. Reviewed entry paths identify v2. No recycle-bin cleanup, SQL, DDL or native call was executed by author.

Observed read-only filesystem detail: original verify.sql has a single initial U+FEFF. Current reviewed-v1 wrapper bytes inspected by author contain no U+FEFF; root's comparison failure may concern expected-text normalization. V2 provides an explicit independently checkable no-BOM chain without altering or rewriting that history. Root decides application after exact diff/byte review.
