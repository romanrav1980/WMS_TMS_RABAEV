set define off
set serveroutput on

prompt [clean-install] optional slow SQL native Oracle grants
prompt Run as SYS/SYSTEM if /api/admin/slow-sql/oracle-top must read v$ views.

@../../migrations/2026-05-17_feed_factory_traceability/022_grant_native_views_system.sql
