select KIND,count(*) SCOPE_OBJECTS from RRL_ACCESS_OBJECT where KIND in('STORE','REGION')group by KIND;
select count(*) INVALID_COUNT from user_objects where status='INVALID';
select count(*) MOJIBAKE_TITLES from RRL_ACCESS_OBJECT where KIND in('STORE','REGION')and(instr(TITLE,unistr('\FFFD'))>0 or instr(TITLE,'???')>0);
