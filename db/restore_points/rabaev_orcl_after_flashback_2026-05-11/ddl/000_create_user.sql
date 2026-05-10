declare
  v_count number;
begin
  select count(*)
    into v_count
    from dba_users
   where username = 'RABAEV';

  if v_count = 0 then
    execute immediate 'create user RABAEV identified by RABAEVWMS default tablespace USERS temporary tablespace TEMP quota unlimited on USERS';
  else
    execute immediate 'alter user RABAEV identified by RABAEVWMS account unlock';
    execute immediate 'alter user RABAEV quota unlimited on USERS';
  end if;
end;
/

grant connect, resource to RABAEV;
grant create view, create sequence, create procedure, create trigger, create synonym to RABAEV;
