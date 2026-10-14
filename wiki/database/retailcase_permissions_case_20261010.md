# Контракт регистра имён прав
10.10.2026.084 APPLIED RABAEV/orcl. Existing admin rights endpoint normalizes RIGHT1 to uppercase; API authentication lowercases them, but old RRL_HAS_WRIGHT compared exact case. Thus a normal non-admin grant could pass HTTP and fail Oracle. Found while completing store receiver binding; no second rights registry.

Existing function now compares trimmed permission names case-insensitively, requires one exact active RUSERS ID, preserves GLOBAL_ADMIN all-rights with the same case/trim semantics as API. Duplicate right rows behave as presence of a permission, matching API set semantics; duplicate actor identity refuses. SQL/Rights tables and group assignment remain unchanged.

scripts/ni053_receiver_rights_case.py passed actual existing rights UI API grant in uppercase, both lower/uppercase Oracle checks, GLOBAL_ADMIN1, non-admin receiver without address binding403, own binding preview200, foreign-address403, deactivated HTTP401/Oracle0. Own receiver retired; no stock writes.

Source [084](../../db/migrations/2026-10-10_permissions_case/apply.sql), original function checkpoint retained, live VALID and dependent objects recompiled. This is bounded actual role/contract evidence, not a broad security audit. No permission automatically granted to existing groups.
