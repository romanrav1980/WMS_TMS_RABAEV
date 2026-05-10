set define off
set serveroutput on

prompt Creating Oracle schema for WindowsApplication2 xp12
prompt Run this script as SYSTEM, SYS, or another account that can create users and grant privileges.

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
        execute immediate 'alter user RABAEV identified by RABAEVWMS';
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

alter session set current_schema = RABAEV;

prompt Creating sequences
@@02_sequences.sql

prompt Creating tables, indexes, triggers and constraints
@@01_tables.sql

prompt Creating PL/SQL functions used by WindowsApplication2 xp12
@@03_functions.sql

prompt Creating PL/SQL procedures used by WindowsApplication2 xp12
@@04_procedures.sql

prompt Creating supplemental legacy objects required by WindowsApplication2 xp12
@@05_gap_patch.sql

prompt Creating working transport task implementations required by WindowsApplication2 xp12
@@06_transport_task_missing_impl.sql

prompt Applying legacy Oracle 19c completion patches
@@07_legacy_completion.sql

prompt Applying remains compatibility package
@@08_remains_compat.sql

prompt Applying schema contract patch
@@09_schema_contract.sql

prompt Applying ARTICULS compatibility package
@@10_articuls_contract.sql

prompt Applying COMPL compatibility package
@@11_compl_contract.sql

prompt Applying ORDERS compatibility package
@@12_orders_contract.sql

prompt Applying CROSS_DOCKING compatibility package
@@13_cross_docking_contract.sql

prompt Schema creation finished
@14_transport_seed_contract.sql

