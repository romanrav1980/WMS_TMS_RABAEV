select object_name,object_type,status from user_objects where object_name in('RRL_STORE_CALENDAR_API','RRL_SAP_CAL_EX_GUARD','RRL_SAP_CAL_WRITE_GUARD');
select name,type,line,text from user_errors where name in('RRL_STORE_CALENDAR_API','RRL_SAP_CAL_EX_GUARD','RRL_SAP_CAL_WRITE_GUARD');
