set define off
set serveroutput on

prompt [profile] legacy-master

@../structure/00_create_rabaev_owner.sql
@../structure/10_legacy_core_structure.sql
@../settings/20_legacy_master_data.sql
@../settings/10_minimal_runtime_settings.sql

prompt [profile] legacy-master done
