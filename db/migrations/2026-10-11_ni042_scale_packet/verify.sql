select object_name,object_type,status from user_objects where object_name in('RRL_SCALE_PACKET_READ','RRL_STORE_SCALE_API');
select name,line,text from user_errors where name in('RRL_SCALE_PACKET_READ','RRL_STORE_SCALE_API');
