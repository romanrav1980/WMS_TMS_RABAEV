prompt [migration 2026-05-19-034] resource management foundation - rollback

delete from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and upper(RIGHT1) in (
     'RESOURCE_MANAGEMENT_VIEW',
     'RESOURCE_MANAGEMENT_EDIT',
     'RESOURCE_SHIFT_VIEW',
     'RESOURCE_SHIFT_EDIT',
     'RESOURCE_SESSION_VIEW',
     'RESOURCE_SESSION_MANAGE',
     'RESOURCE_GANTT_VIEW',
     'RESOURCE_GANTT_REPLAN',
     'RESOURCE_DISPATCH_MANAGE',
     'WAREHOUSE_TASK_FORCE_ASSIGN'
   );

delete from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-19-034-resource-management-foundation';

commit;

prompt [migration 2026-05-19-034] rollback done
