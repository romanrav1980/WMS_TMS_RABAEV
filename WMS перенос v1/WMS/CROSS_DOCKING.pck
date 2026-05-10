create or replace package CROSS_DOCKING is

  -- Author  : RRABAEV
  -- Created : 16.09.2011 15:47:36
  -- Purpose : Кросс-докинг

/*
     Принцип преноса данных при кросс-докинге. 
      1) определяем список паллет для переноса.
      2) проверяем адреса данных паллет на наличие в дочерней базе (поиск по внешнему ид).
       если адресов с данным внешним 
       идентификатором нет, создаем такой адрес.
      3) проверяем артикулы в паллетах. если нет, копируем артикулы
      4) проверяем модификации в паллетах по сочетанию 
      
        
          
       5) переносим строки паллета , переносим паллет в состоянии 2. (закрыт) , 
       склад КРОСС-АЛКО ..... - из таблицы соответствий складов

*/


  -- Public function and procedure declarations
  function SYNC_ARTICUL( ACTICUL1  VARCHAR2 , NORMA_UKLADKI1  NUMBER , NAME1  VARCHAR2 ,
  SHT_IN_KOR1 NUMBER , SHT_WEIGHT1 NUMBER , KARTON_WEIGHT1  NUMBER , SHK_SHT1 VARCHAR2 ,
  SHK_KOR1  VARCHAR2 ) return int;
  
 -- function SYNC_MOD();
  
 -- function SYNC_ADDR();
 -- function SYNC_PALLET();
 -- function SYNC_PALLET_ROW();
 -- function SYNC_VEH();
 -- function SYNC_VODITEL();

/*
ACTICUL           VARCHAR2(15 CHAR),
  NORMA_UKLADKI     NUMBER                      NOT NULL,
  CELL              VARCHAR2(50 CHAR),
  NAME              VARCHAR2(255 CHAR),
  UNIT_TYPE         VARCHAR2(20 CHAR),
  BARCODE_SHT       VARCHAR2(128 CHAR)          DEFAULT 777                   NOT NULL,
  BARCODE_KOR       VARCHAR2(128 CHAR),
  BARCODE_BL        VARCHAR2(128 CHAR),
  WEIGHT_OF_KOR     NUMBER,
  COUNT_IN_ROW      INTEGER,
  ROWS_IN_PAL       INTEGER,
  COUNT_SHT_IN_KOR  NUMBER,
  COUNT_SHT_IN_BL   NUMBER                      DEFAULT 1,
  PALLET_MULTIPLE   NUMBER                      DEFAULT 1,
  CARTON_WEIGHT     NUMBER                      DEFAULT 0,
  ETAJ_LIMIT        INTEGER                     DEFAULT 100,
  BESTBEFOREDAYS    INTEGER                     DEFAULT 360,
  SSP               NUMBER                      DEFAULT 0,
  ABC_GROUP         VARCHAR2(1 BYTE),
  XYZ_GROUP         VARCHAR2(1 BYTE),
  ORDER_OF_COMP     INTEGER                     DEFAULT 0,
  RCECOMPLECT       INTEGER                     DEFAULT 0,
  FLOATING_WEIGHT   INTEGER                     DEFAULT 0,
  TYPE_W            INTEGER                     DEFAULT 0,
  WEIGHT_OF_SHT     NUMBER                      DEFAULT 0,
  ROUND_TO          INTEGER                     DEFAULT 2,
  DEF_PERC          NUMBER                      DEFAULT 0,
  LAST_MOD_ID       INTEGER

*/



/* RABAEV.RRL_ARTICUL_MODS
(
  ID             INTEGER,
  ARTICUL        VARCHAR2(15 BYTE),
  NAME           VARCHAR2(50 BYTE),
  SHT_IN_KOR     NUMBER,
  SHT_WEIGHT     NUMBER,
  KARTON_WEIGHT  NUMBER,
  DELETED        INTEGER,
  SHK_SHT        VARCHAR2(50 BYTE),
  SHK_KOR        VARCHAR2(50 BYTE)
)*/

end CROSS_DOCKING;
/
create or replace package body CROSS_DOCKING is

 function SYNC_ARTICUL( ACTICUL  VARCHAR2 , NORMA_UKLADKI     NUMBER ) return int is
 begin
   
 null;
 end;

begin
  -- Initialization
  null;
end CROSS_DOCKING;
/
