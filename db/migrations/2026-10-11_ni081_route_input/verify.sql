select object_name,object_type,status from user_objects where object_name in('RRL_TT_ROUTE_SOURCE','RRL_TT_ROUTE_API','RRL_TT_OPERATION_PLAN_API','RRL_TT_ROUTE_INPUT_GUARD');
select name,type,line,text from user_errors where name in('RRL_TT_ROUTE_SOURCE','RRL_TT_ROUTE_API','RRL_TT_OPERATION_PLAN_API','RRL_TT_ROUTE_INPUT_GUARD');
