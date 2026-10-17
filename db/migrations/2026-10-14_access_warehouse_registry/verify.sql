select count(*) REGISTERED_WAREHOUSES from RRL_ACCESS_OBJECT where KIND='WAREHOUSE';
select count(*) UNEXPECTED_ASSIGNMENTS from RRL_ACCESS_ASSIGNMENT;
select count(*) INVALID_COUNT from user_objects where status='INVALID';
