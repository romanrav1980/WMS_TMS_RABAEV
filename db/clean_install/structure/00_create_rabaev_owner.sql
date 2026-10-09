set define off
set serveroutput on

prompt [clean-install] create/update RABAEV owner
prompt Run through an Oracle account that can create users and grant privileges.

declare
  v_count number := 0;
begin
  select count(*)
    into v_count
    from dba_users
   where username = 'RABAEV';

  if v_count = 0 then
    execute immediate 'create user RABAEV identified by RABAEVWMS default tablespace USERS temporary tablespace TEMP quota unlimited on USERS';
  else
    execute immediate 'alter user RABAEV identified by RABAEVWMS account unlock';
    execute immediate 'alter user RABAEV default tablespace USERS temporary tablespace TEMP';
    execute immediate 'alter user RABAEV quota unlimited on USERS';
  end if;
end;
/

grant connect to RABAEV;
grant resource to RABAEV;
grant create view to RABAEV;
grant create sequence to RABAEV;
grant create procedure to RABAEV;
grant create trigger to RABAEV;
grant create synonym to RABAEV;

prompt [clean-install] owner ready
