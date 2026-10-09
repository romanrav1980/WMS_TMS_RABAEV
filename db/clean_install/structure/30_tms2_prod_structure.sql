set define off
set serveroutput on

prompt [clean-install] TMS-2 production structure

alter session set current_schema = RABAEV;

prompt Applying final compatible MAP/VRP planner structure
@../../migrations/2026-05-26_transport_sprint7/051_apply.sql
@../../migrations/2026-05-26_transport_sprint8/052_apply.sql

prompt Applying ARM/Gantt structure
@../../migrations/2026-05-27_transport_sprint11/053_apply.sql

prompt Applying transport billing structure
@../../migrations/2026-05-27_transport_sprint15/054_apply.sql

prompt Applying fleet CRUD structure and legacy-column fix
@../../migrations/2026-05-29_fleet_crud/055_apply.sql
@../../migrations/2026-05-29_fleet_crud/055_fix.sql
@../../migrations/2026-05-29_fleet_crud/056_apply.sql

prompt Applying notification/GPS/geofencing structure
@../../migrations/2026-05-29_notifications/058_apply.sql
@../../migrations/2026-05-29_gps/060_apply.sql
@../../migrations/2026-05-29_geofencing/062_apply.sql

prompt [clean-install] TMS-2 production structure done
