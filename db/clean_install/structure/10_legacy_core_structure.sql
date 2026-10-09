set define off
set serveroutput on

prompt [clean-install] legacy WindowsApplication2 xp12 core structure

alter session set current_schema = RABAEV;

prompt Creating sequences
@../../windowsapplication2_xp12_oracle/02_sequences.sql

prompt Creating tables, indexes, triggers and constraints
@../../windowsapplication2_xp12_oracle/01_tables.sql

prompt Creating PL/SQL functions used by WindowsApplication2 xp12
@../../windowsapplication2_xp12_oracle/03_functions.sql

prompt Creating PL/SQL procedures used by WindowsApplication2 xp12
@../../windowsapplication2_xp12_oracle/04_procedures.sql

prompt Creating supplemental legacy objects required by WindowsApplication2 xp12
@../../windowsapplication2_xp12_oracle/05_gap_patch.sql

prompt Creating working transport task implementations required by WindowsApplication2 xp12
@../../windowsapplication2_xp12_oracle/06_transport_task_missing_impl.sql

prompt Applying legacy Oracle 19c completion patches
@../../windowsapplication2_xp12_oracle/07_legacy_completion.sql

prompt Applying remains compatibility package
@../../windowsapplication2_xp12_oracle/08_remains_compat.sql

prompt Applying schema contract patch
@../../windowsapplication2_xp12_oracle/09_schema_contract.sql

prompt Applying ARTICULS compatibility package
@../../windowsapplication2_xp12_oracle/10_articuls_contract.sql

prompt Applying COMPL compatibility package
@../../windowsapplication2_xp12_oracle/11_compl_contract.sql

prompt Applying ORDERS compatibility package
@../../windowsapplication2_xp12_oracle/12_orders_contract.sql

prompt Applying CROSS_DOCKING compatibility package
@../../windowsapplication2_xp12_oracle/13_cross_docking_contract.sql

prompt Applying transport seed compatibility patch
@../../windowsapplication2_xp12_oracle/14_transport_seed_contract.sql

prompt [clean-install] legacy core structure done
