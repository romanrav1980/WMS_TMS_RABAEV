# Compatibility Fixes 2026-05-11

Fix pass for the restored `RABAEV` schema after the desktop/Tserver compatibility check.

Apply only after a VM snapshot.

## Scripts

- `001_client_tserver_compat.sql`: adds missing table-like objects, compatibility package APIs, and conservative columns used by the WinForms client.

## Verification

After applying:

- run `tmp/oracle_apply/recompile_rabaev.sql`;
- verify `select count(*) from user_objects where status <> 'VALID'` returns `0`;
- rebuild `WindowsApplication2` and `Tserver`;
- run the `Tserver` `GET_RUSER` smoke test.
