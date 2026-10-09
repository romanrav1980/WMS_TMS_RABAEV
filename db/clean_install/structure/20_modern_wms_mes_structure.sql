set define off
set serveroutput on

prompt [clean-install] modern WMS/MES/traceability/warehouse-map structure

alter session set current_schema = RABAEV;

@../../migrations/2026-05-17_feed_factory_traceability/001_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/002_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/003_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/004_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/005_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/006_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/007_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/008_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/009_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/010_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/011_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/012_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/013_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/014_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/015_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/016_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/017_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/018_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/019_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/020_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/021_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/022_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/023_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/024_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/025_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/026_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/027_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/028_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/029_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/030_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/031_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/032_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/033_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/034_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/035_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/036_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/037_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/038_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/039_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/040_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/041_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/042_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/043_apply.sql
@../../migrations/2026-05-17_feed_factory_traceability/044_apply.sql

prompt [clean-install] modern WMS/MES/traceability/warehouse-map structure done
