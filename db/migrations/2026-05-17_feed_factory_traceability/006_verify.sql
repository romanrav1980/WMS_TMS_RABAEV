-- 2026-05-17-006-rights-admin-page-permissions verification

select 'RIGHTS_ADMIN_PERMISSIONS' check_name,
       count(*) rights_found
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in ('RIGHTS_ADMIN_VIEW', 'RIGHTS_ADMIN_EDIT');

select RRL_HAS_WRIGHT('admin', 'RIGHTS_ADMIN_VIEW') RIGHTS_ADMIN_VIEW,
       RRL_HAS_WRIGHT('admin', 'RIGHTS_ADMIN_EDIT') RIGHTS_ADMIN_EDIT
  from dual;

select object_type, status, count(*) cnt
  from user_objects
 where status <> 'VALID'
   and object_name not like 'BIN$%'
 group by object_type, status
 order by object_type, status;
