prompt One-time administrator dependency grants; no stock/data changes
declare
begin
 if user not in('SYS','SYSTEM') then raise_application_error(-20851,'Run this prerequisite as Oracle administrator'); end if;
 execute immediate 'grant execute on SYS.DBMS_LOCK to RABAEV';
 execute immediate 'grant execute on SYS.DBMS_CRYPTO to RABAEV';
 execute immediate 'grant execute on SYS.DBMS_FLASHBACK to RABAEV';
end;
/
