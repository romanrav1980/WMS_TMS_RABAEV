-- 2026-05-17-005-admin-users-db-backed-auth rollback
-- Keeps existing legacy tables. Reverts only the admin password changed by 005.

update RUSERS
   set PASS = 'admin'
 where lower(ID) = 'admin'
   and PASS = 'admin123'
   and USER_GROUP = 'GLOBAL_ADMIN';

commit;
