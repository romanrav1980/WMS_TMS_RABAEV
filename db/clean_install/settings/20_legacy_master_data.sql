set define off
set serveroutput on

prompt [clean-install] full legacy master reference data

alter session set current_schema = RABAEV;

@../../windowsapplication2_xp12_oracle/20_seed_master_data.sql

prompt [clean-install] full legacy master reference data done
