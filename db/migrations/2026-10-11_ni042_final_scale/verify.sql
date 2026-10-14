select name,type,line,text from user_errors where name not like 'BIN$%';
select CAPTURE_PURPOSE,count(*) from RRL_WH_SCALE_CAPTURE group by CAPTURE_PURPOSE;
