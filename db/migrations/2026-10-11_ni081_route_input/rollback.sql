-- Explicit recovery only; preserve/export route journal before removing metadata.
@@../2026-10-10_ni081_operation_plan/001_api.sql
drop trigger RRL_TT_ROUTE_INPUT_GUARD;
drop package RRL_TT_ROUTE_API;
drop package RRL_TT_ROUTE_SOURCE;
-- Retain RRL_TT_ROUTE_INPUT history until explicit data disposal.
