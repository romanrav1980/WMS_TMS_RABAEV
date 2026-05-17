-- 2026-05-17-005-admin-users-db-backed-auth verification

select 'RUSERS_ADMIN' check_name,
       count(*) rows_found
  from RUSERS
 where lower(ID) = 'admin'
   and PASS = 'admin123'
   and nvl(DELETED, 0) = 0
   and nvl(PRAVO_ADMIN_LOGIN, 0) = 1
   and USER_GROUP = 'GLOBAL_ADMIN';

select 'GLOBAL_ADMIN_RIGHTS' check_name,
       count(*) rights_found
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in (
     'WMS_ADMIN_LOGIN',
     'API_AUDIT_VIEW',
     'API_AUDIT_REPLAY',
     'REGULATORY_ADAPTER_VIEW',
     'REGULATORY_ADAPTER_RETRY'
   );

select object_type, status, count(*) cnt
  from user_objects
 where status <> 'VALID'
   and object_name not like 'BIN$%'
 group by object_type, status
 order by object_type, status;
