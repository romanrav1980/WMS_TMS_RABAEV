set define off
set sqlblanklines on

prompt VIEW Z1

  CREATE OR REPLACE FORCE EDITIONABLE VIEW "RABAEV"."Z1" ("ADDR", "NAPR") DEFAULT COLLATION "USING_NLS_COMP"  AS 
  select distinct 
ADDR , 
NAPR
from
RRL_SBORKA_PALLETS;

