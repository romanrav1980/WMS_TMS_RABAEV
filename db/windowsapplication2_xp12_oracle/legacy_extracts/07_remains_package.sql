create or replace package REMAINS is

  -- Author  : RRABAEV
  -- Created : 15.09.2011 9:04:07
  -- Purpose : ???????
  

  -- Public function and procedure declarations
  function create_snapshot( type2 int  ) return int;
  function close_snapshot(  snap_shot_id1 int  ) return int;
  function add_row_2_snapshot(   snap_shot_id1 int ,   cell1 varchar ,   articul1 varchar2 ) return int;
  function remains_free( articul1 varchar2 ) return number ;
  function remains_in_otbor( articul1 varchar2 ) return number;
  function remains_in_otbor_all( articul1 varchar2 ) return number ;
  function remains_free_all( articul1 varchar2 ) return number ; 


function remains_partion_in_cell( pallet_uid1 varchar2 , cell3 varchar2 ) return number ; 
function remains_partion_in_otbor( pallet_uid1 varchar2 ) return number ; 
function remains_except_part_in_otb( pallet_uid1 varchar2 ) return number ;


function CLOSE_OTHOD_PALLET(  PALLET_ID1 varchar2 ,  iser_id21 varchar2  ) RETURN varchar2;
FUNCTION TRIAL_BY_WEIGHT(  PALLET_UID1  varchar2 ,  TRIAL_WEIGHT1 varchar2 , WOOD_WEIGHT1 varchar2 , user_id1 varchar2 )  RETURN int ;
FUNCTION SET_SCAN_PROOVE( PALLET_UID1 varchar2  , count_of_errors1 int ,
    prim1 varchar2 ,  SBORSHIK1  VARCHAR2, KLADOVSHIK1 VARCHAR2 ) return int;
FUNCTION OTHOD_PALLET_PODBOR_PARTII( PALLET_ID1 varchar2 ) RETURN int;
function move_pall_2_picking_cell( pall_uid1 varchar2 , user_id2 varchar2 ) return varchar2 ;
function close_othod_pall_row( PALLET_ROW_ID1 int, prih_pall_uid5 varchar2 , kolvo_provod number  , iser_id21 varchar2   ) return int ;
FUNCTION OTHOD_PALLET_PODBOR_PARTI4CELL( PALLET_ID1 varchar2 , cell1 varchar2 )  RETURN int ;

end REMAINS;
/
