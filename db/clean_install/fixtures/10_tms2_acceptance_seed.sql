set define off
set serveroutput on

prompt [clean-install] TMS-2 acceptance fixtures
prompt Never run this script for production data.

alter session set current_schema = RABAEV;

prompt Applying Dobrotseny deterministic warehouse/order seed
@../../migrations/2026-05-23_dobrotseny_seed/046_apply.sql
@../../migrations/2026-05-23_dobrotseny_seed/047_apply.sql

prompt Applying Sprint 9 planner-template fixture
@../../migrations/2026-05-29_tms2_planner_template_fixture/055_apply.sql

prompt Applying MAP/VRP test geocode fixture
@../../migrations/2026-06-01_tms2_test_geocode/063_apply.sql

prompt [clean-install] TMS-2 acceptance fixtures done
