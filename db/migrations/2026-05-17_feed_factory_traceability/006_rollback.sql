-- 2026-05-17-006-rights-admin-page-permissions rollback
-- Removes only the two rights introduced by migration 006.

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in ('RIGHTS_ADMIN_VIEW', 'RIGHTS_ADMIN_EDIT');

commit;
