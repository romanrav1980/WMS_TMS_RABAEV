select name,type,line,text from user_errors where name not like 'BIN$%';
select SIGNATURE_VERSION,count(*)from RRL_WH_FINAL_SCALE_USE group by SIGNATURE_VERSION;
