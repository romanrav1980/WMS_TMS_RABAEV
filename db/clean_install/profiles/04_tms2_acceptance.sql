set define off
set serveroutput on

prompt [profile] tms2-acceptance

@../structure/00_create_rabaev_owner.sql
@../structure/10_legacy_core_structure.sql
@../settings/20_legacy_master_data.sql
@../settings/10_minimal_runtime_settings.sql
@../structure/20_modern_wms_mes_structure.sql
@../structure/30_tms2_prod_structure.sql
@../fixtures/10_tms2_acceptance_seed.sql
@../settings/10_minimal_runtime_settings.sql

prompt [profile] tms2-acceptance done
