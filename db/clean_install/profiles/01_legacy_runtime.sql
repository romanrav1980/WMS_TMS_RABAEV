set define off
set serveroutput on

prompt [profile] legacy-runtime

@../structure/00_create_rabaev_owner.sql
@../structure/10_legacy_core_structure.sql
@../settings/10_minimal_runtime_settings.sql

prompt [profile] legacy-runtime done
