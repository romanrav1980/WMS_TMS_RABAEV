--
-- Create Schema Script 
--   Database Version   : 10.2.0.1.0 
--   TOAD Version       : 9.1.0.62 
--   DB Connect String  : REFSTOCK 
--   Schema             : RABAEV 
--   Script Created by  : RABAEV 
--   Script Created at  : 22.01.2010 5:30:29 
--   Physical Location  :  
--   Notes              :  
--

-- Object Counts: 
--   Users: 1           Sys Privs: 3        Roles: 1            Tablespace Quotas: 1 
--   Tablespaces: 1     DataFiles: 1         
-- 
--   Functions: 17      Lines of Code: 1053 
--   Indexes: 29        Columns: 37         
--   Procedures: 4      Lines of Code: 269 
--   Sequences: 7 
--   Tables: 23         Columns: 148        Constraints: 15     
--   Triggers: 4 
--   Views: 3           


CREATE TABLESPACE USERS DATAFILE 
  '/u01/app/oracle/oradata/REFSTOCK/users01.dbf' SIZE 5807360K AUTOEXTEND ON NEXT 1280K MAXSIZE UNLIMITED
LOGGING
ONLINE
PERMANENT
EXTENT MANAGEMENT LOCAL AUTOALLOCATE
BLOCKSIZE 8K
SEGMENT SPACE MANAGEMENT AUTO
FLASHBACK ON;


CREATE USER RABAEV
  IDENTIFIED BY VALUES 'C7B4E42B7CAF4C9C'
  DEFAULT TABLESPACE USERS
  TEMPORARY TABLESPACE TEMP
  PROFILE DEFAULT
  ACCOUNT UNLOCK;
  -- 1 Role for RABAEV 
  GRANT CONNECT TO RABAEV WITH ADMIN OPTION;
  ALTER USER RABAEV DEFAULT ROLE ALL;
  -- 3 System Privileges for RABAEV 
  GRANT SELECT ANY SEQUENCE TO RABAEV WITH ADMIN OPTION;
  GRANT SELECT ANY TABLE TO RABAEV WITH ADMIN OPTION;
  GRANT SELECT ANY DICTIONARY TO RABAEV WITH ADMIN OPTION;
  -- 1 Tablespace Quota for RABAEV 
  ALTER USER RABAEV QUOTA UNLIMITED ON USERS;


CREATE SEQUENCE RRL_PRIHOD_NAKLAD_SQ
  START WITH 11
  MAXVALUE 9999999999999999
  MINVALUE 1
  CYCLE
  NOCACHE
  NOORDER;


CREATE SEQUENCE RRL_PRIHOD_NAKLAD_ROWS_SQ
  START WITH 238
  MAXVALUE 999999999999999999999999999
  MINVALUE 1
  CYCLE
  NOCACHE
  NOORDER;


CREATE SEQUENCE ORDER_MOV_HIST_ID
  START WITH 78
  MAXVALUE 999999999999999999
  MINVALUE 1
  CYCLE
  NOCACHE
  NOORDER;


CREATE SEQUENCE SFERA_EAN_ID
  START WITH 92231
  MAXVALUE 999999999999999999999999999
  MINVALUE 1
  CYCLE
  NOCACHE
  NOORDER;


CREATE SEQUENCE RRL_ORDER_ROW_SEQ
  START WITH 25
  MAXVALUE 99999999999999999999999
  MINVALUE 1
  CYCLE
  NOCACHE
  NOORDER;


CREATE SEQUENCE RRL_EVENT_ID_SQ
  START WITH 8247
  INCREMENT BY 2
  MAXVALUE 999999999999999999999
  MINVALUE 5
  CYCLE
  NOCACHE
  NOORDER;


CREATE SEQUENCE RRL_PRIH_ORD_ID
  START WITH 14
  MAXVALUE 99999999999999999999999
  MINVALUE 1
  CYCLE
  NOCACHE
  NOORDER;


CREATE TABLE RRL_INVETARIZ
(
  ID       INTEGER,
  DATE_OF  DATE                                 NOT NULL,
  TYPE1    INTEGER                              DEFAULT 1                     NOT NULL
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_INVENTARIZ_LINES
(
  ID_OF_INVENT  INTEGER                         NOT NULL,
  ID_LINE       INTEGER,
  CELL          VARCHAR2(50 CHAR)               NOT NULL,
  PALLET_ID     VARCHAR2(50 CHAR)               NOT NULL,
  COUNT1        NUMBER
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE PLACE_AUDIT
(
  PALLETID   VARCHAR2(25 CHAR)                  NOT NULL,
  CONDITION  VARCHAR2(25 CHAR)
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE PLACE_AUDIT_ERROR_LINES
(
  PALLETID    VARCHAR2(25 CHAR)                 NOT NULL,
  CONDITION   VARCHAR2(15 CHAR),
  UNIT_COUNT  INTEGER                           DEFAULT 0                     NOT NULL,
  UID1        VARCHAR2(12 CHAR),
  EAN         VARCHAR2(25 CHAR),
  RUSER       NVARCHAR2(50),
  DATE1       DATE
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE ORDER_AUDIT_ERROR_LINES
(
  ORDER_NUMBER  VARCHAR2(25 CHAR)               NOT NULL,
  CONDITION     VARCHAR2(15 CHAR),
  UNIT_COUNT    INTEGER                         DEFAULT 0                     NOT NULL,
  UID1          VARCHAR2(12 CHAR),
  EAN           VARCHAR2(25 CHAR)
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE ORDER_AUDIT
(
  ORDER_NUMBER  VARCHAR2(25 CHAR)               NOT NULL,
  CONDITION     VARCHAR2(25 CHAR)
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE SFERA_EAN
(
  TMC_UID      VARCHAR2(50 CHAR)                NOT NULL,
  EAN_SHT      VARCHAR2(20 CHAR),
  EAN_BL       VARCHAR2(20 CHAR),
  EAN_KOR      VARCHAR2(20 CHAR),
  MANUALENTER  CHAR(1 CHAR)                     DEFAULT 'Y',
  SHT_IN_BL    INTEGER                          NOT NULL,
  BL_IN_KOR    INTEGER                          NOT NULL,
  УИД          INTEGER,
  NAME         VARCHAR2(255 CHAR)
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RUSERS
(
  ID                           NVARCHAR2(50)    NOT NULL,
  NAME                         NVARCHAR2(255),
  PRAVO_INVENTORY_EDIT         INTEGER          DEFAULT 0,
  PRAVO_CHECK_ORDER            INTEGER          DEFAULT 0,
  PRAVO_LIGHT_INVENTORY_CHECK  INTEGER          DEFAULT 0,
  DELETED                      INTEGER          DEFAULT 0,
  PRAVO_RAZVOZ_ZAYAVOK         INTEGER          DEFAULT 0,
  WMSUSER_ID                   INTEGER,
  PRAVO_EAN_PRODUCT_CHANGE     INTEGER          DEFAULT 0,
  PRAVO_KARSHIK                INTEGER          DEFAULT 0,
  WARE_ID                      INTEGER          DEFAULT 1
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE INVENTORY_LINE_PALLET_AUDIT
(
  УИД           VARCHAR2(25 CHAR)               NOT NULL,
  КОЛ           INTEGER                         DEFAULT 0,
  PALLETID      VARCHAR2(25 CHAR)               NOT NULL,
  ДАТАСОЗДАНИЯ  DATE,
  USER_ID       VARCHAR2(50 CHAR),
  METHOD        VARCHAR2(20 CHAR)
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE TZS
(
  КОД            INTEGER,
  УИД            INTEGER                        NOT NULL,
  ДАТАТЗ         DATE,
  ИДЕНТИФИКАТОР  NVARCHAR2(255),
  СЕКТОР         NVARCHAR2(255),
  НОМЕР          NVARCHAR2(50)                  NOT NULL,
  ЮР_ЛИЦО        NVARCHAR2(27),
  КЛИЕНТ         NVARCHAR2(60),
  СУММА          FLOAT(126),
  ВЕС            FLOAT(126),
  ОБЪЕМ          FLOAT(126),
  КВОСТРОЧЕК     INTEGER                        DEFAULT (0),
  АДРЕС          NVARCHAR2(255),
  ПРИМЕЧАНИЕ     NVARCHAR2(255),
  ВАЖНОСТЬ       NVARCHAR2(255)
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE LOT_AUDIT
(
  SSCC       VARCHAR2(25 CHAR)                  NOT NULL,
  CONDITION  VARCHAR2(25 CHAR)
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE LOT_AUDIT_ERROR_LINES
(
  SSCC        VARCHAR2(25 CHAR)                 NOT NULL,
  CONDITION   VARCHAR2(15 CHAR),
  UNIT_COUNT  INTEGER                           DEFAULT 0                     NOT NULL,
  UID1        VARCHAR2(12 CHAR),
  EAN         VARCHAR2(25 CHAR)
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE TEST1
(
  ID3  INTEGER
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE ORDER_MOV_HIST
(
  ID          INTEGER                           NOT NULL,
  ORDER_UID   INTEGER                           NOT NULL,
  ZONE        NVARCHAR2(15),
  RUSER       NVARCHAR2(15)                     NOT NULL,
  TIME_STAMP  DATE,
  LAST_FLAG   INTEGER                           DEFAULT 1,
  USSCC       VARCHAR2(50 CHAR)
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_EVENTS
(
  ID_EVENT        NUMBER,
  CELL_FROM       VARCHAR2(20 BYTE),
  CELL_TO         VARCHAR2(20 BYTE),
  DATE_EVENT      DATE                          NOT NULL,
  DATE_OF_ORDER   DATE,
  COUNT_EVENT     NUMBER,
  TYPE_EVENT      NUMBER(38)                    NOT NULL,
  UID_POLETA      VARCHAR2(50 BYTE),
  USER_ID         VARCHAR2(50 BYTE)             NOT NULL,
  PRIHOD_NAKL_ID  INTEGER                       DEFAULT 0,
  OTHOD_NAKL_ID   INTEGER                       DEFAULT 0
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_REMAINS
(
  CELL           VARCHAR2(20 BYTE),
  UID_POLETA     VARCHAR2(50 BYTE),
  REMAIN         NUMBER,
  OTHOD_NAKL_ID  INTEGER                        DEFAULT 0
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_PALLETS
(
  UID_PALLET        VARCHAR2(50 CHAR),
  ARTICUL           VARCHAR2(15 CHAR),
  CREATION_DATE     DATE,
  EXPIRY_DATE       DATE,
  UNIT_COUNT        NUMBER,
  PRICE             NUMBER,
  PRIHOD_NAKLAD_ID  INTEGER                     NOT NULL
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_ARTICULS
(
  ACTICUL        VARCHAR2(15 CHAR),
  NORMA_UKLADKI  NUMBER                         NOT NULL,
  CELL           VARCHAR2(50 CHAR),
  NAME           VARCHAR2(255 CHAR),
  UNIT_TYPE      VARCHAR2(20 CHAR),
  BARCODE_SHT    VARCHAR2(128 CHAR)             DEFAULT 777                   NOT NULL,
  BARCODE_KOR    VARCHAR2(128 CHAR),
  BARCODE_BL     VARCHAR2(128 CHAR),
  WEIGHT_OF_KOR  NUMBER,
  COUNT_IN_ROW   INTEGER,
  ROWS_IN_PAL    INTEGER
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_CELLS
(
  CELL                    VARCHAR2(15 CHAR),
  OTBOR                   INTEGER               DEFAULT 0,
  BLOCKED_FOR_REMAINS     INTEGER               DEFAULT 0,
  BLOCKED_FOR_POPOLNENIE  INTEGER               DEFAULT 0,
  UID_POLETA_FOR_BLOCK    VARCHAR2(50 CHAR),
  TIME_FOR_BLOCK          DATE,
  X                       INTEGER               DEFAULT 10000                 NOT NULL,
  Y                       INTEGER               DEFAULT 10000                 NOT NULL,
  Z                       INTEGER               DEFAULT 10000                 NOT NULL,
  BLOCKED_FOR_ACCEPT      INTEGER               DEFAULT 0,
  WARE_ID                 INTEGER               DEFAULT 1
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_PRIHOD_NAKLAD
(
  NAKLAD_NUMBER     VARCHAR2(20 CHAR),
  DATE_OF_NAKLAD    DATE,
  DATE_OF_ACCEPT    DATE,
  POSTAVSHIK_NAME   VARCHAR2(50 CHAR),
  SM_NAKLAD_NUMBER  VARCHAR2(50 CHAR),
  CONDITION         INTEGER                     DEFAULT 0,
  ID                INTEGER
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_PRIHOD_NAKLAD_ROWS
(
  ORDID        INTEGER,
  ARTICUL      VARCHAR2(15 CHAR),
  EXPIRY_DATE  DATE,
  ID           INTEGER,
  COUNT1       NUMBER                           DEFAULT 0,
  PRICE        NUMBER                           DEFAULT 0
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_OTHOD_NAKLAD
(
  ID                   INTEGER,
  NAKLADNAME           VARCHAR2(50 CHAR)        NOT NULL,
  MAG_NO               VARCHAR2(50 CHAR)        NOT NULL,
  NAKLADDATE           DATE                     NOT NULL,
  CREATIONDATE         DATE                     NOT NULL,
  PLANNEDDELIVERYDATE  DATE,
  CONDITION            INTEGER                  DEFAULT 0
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE TABLE RRL_OTHOD_NAKLAD_ROWS
(
  ID         INTEGER,
  ID_NAKLAD  INTEGER                            NOT NULL,
  ARTICUL    VARCHAR2(15 CHAR)                  NOT NULL,
  COUNT1     NUMBER                             NOT NULL
)
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;


CREATE UNIQUE INDEX RRL_INVENTARIZ_LINES_PK ON RRL_INVENTARIZ_LINES
(ID_LINE)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_INVETARIZ_PK ON RRL_INVETARIZ
(ID)
LOGGING
NOPARALLEL;


CREATE INDEX LOT_AUDIT_ERROR_LINES_PK ON LOT_AUDIT_ERROR_LINES
(SSCC)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX LOT_AUDIT_PK ON LOT_AUDIT
(SSCC)
LOGGING
NOPARALLEL;


CREATE INDEX PK2 ON SFERA_EAN
(EAN_SHT, EAN_BL, EAN_KOR)
NOLOGGING
NOPARALLEL;


CREATE INDEX PK ON SFERA_EAN
(TMC_UID)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_PRIHOD_NAKLAD_ROWS_ID2 ON RRL_PRIHOD_NAKLAD_ROWS
(ORDID, ARTICUL)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_PRIHOD_NAKLAD_ROWS_PK ON RRL_PRIHOD_NAKLAD_ROWS
(ID)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_PRIHOD_NAKLAD_ID ON RRL_PRIHOD_NAKLAD
(ID)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_PRIHOD_NAKLAD_I2 ON RRL_PRIHOD_NAKLAD
(SM_NAKLAD_NUMBER)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_PRIHOD_NAKLAD ON RRL_PRIHOD_NAKLAD
(NAKLAD_NUMBER, DATE_OF_NAKLAD, POSTAVSHIK_NAME)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_CELLS_PK ON RRL_CELLS
(CELL)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_ARTICULS_PK ON RRL_ARTICULS
(ACTICUL)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_PALLETS_PK ON RRL_PALLETS
(UID_PALLET)
LOGGING
NOPARALLEL;


CREATE INDEX RRL_REMAINS_IND ON RRL_REMAINS
(CELL, UID_POLETA)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_EVENTS_PK ON RRL_EVENTS
(ID_EVENT)
LOGGING
NOPARALLEL;


CREATE INDEX RRL_CELLS_WARE_ID ON RRL_CELLS
(WARE_ID)
LOGGING
NOPARALLEL;


CREATE INDEX RRL_ARTICULS_BARCODE_SHT ON RRL_ARTICULS
(BARCODE_SHT)
LOGGING
NOPARALLEL;


CREATE INDEX RRL_PALLETS_NAKLAD ON RRL_PALLETS
(PRIHOD_NAKLAD_ID)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX ORDER_AUDIT_LINES_PK ON ORDER_AUDIT_ERROR_LINES
(ORDER_NUMBER, UID1)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX ORDER_AUDIT_PK ON ORDER_AUDIT
(ORDER_NUMBER)
LOGGING
NOPARALLEL;


CREATE INDEX ФИЛЬТР1 ON TZS
(ДАТАТЗ, ИДЕНТИФИКАТОР)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX TZS_PK ON TZS
(КОД)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RUSERS_PK ON RUSERS
(ID)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX ORDER_MOV_HIST_PK ON ORDER_MOV_HIST
(ID)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_OTHOD_NAKLAD_ROWS_PK ON RRL_OTHOD_NAKLAD_ROWS
(ID)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_OTHOD_NAKLAD_I4 ON RRL_OTHOD_NAKLAD
(NAKLADNAME)
LOGGING
NOPARALLEL;


CREATE INDEX RRL_OTHOD_NAKLAD_I1 ON RRL_OTHOD_NAKLAD
(CREATIONDATE)
LOGGING
NOPARALLEL;


CREATE UNIQUE INDEX RRL_OTHOD_NAKLAD_PK ON RRL_OTHOD_NAKLAD
(ID)
LOGGING
NOPARALLEL;


CREATE OR REPLACE PROCEDURE        ADD_SFERA_EAN (
    row_uid OUT NUMBER,
    TMC_UID IN VARCHAR2,
      EAN_SHT      VARCHAR2 ,
  EAN_BL       VARCHAR2 ,
  EAN_KOR      VARCHAR2 ,
  MANUALENTER  CHAR,
  SHT_IN_BL    INTEGER,
  BL_IN_KOR    INTEGER,
  NAME         VARCHAR2   
)
AS
BEGIN
    INSERT INTO RABAEV.SFERA_EAN (
      УИД,
      TMC_UID    , 
      EAN_SHT    ,
      EAN_BL      , 
      EAN_KOR     ,
      MANUALENTER  ,
      SHT_IN_BL   ,
      BL_IN_KOR    ,
      NAME    
  ) VALUES (
          RABAEV.SFERA_EAN_ID.NEXTVAL,
          TMC_UID     ,
          EAN_SHT    ,
          EAN_BL      , 
          EAN_KOR     ,
          MANUALENTER  ,
          SHT_IN_BL   ,
          BL_IN_KOR    ,
          NAME    
    );
    
    
    SELECT SFERA_EAN_ID.CURRVAL INTO row_uid FROM DUAL;
    
END  ADD_SFERA_EAN;
/

SHOW ERRORS;


CREATE OR REPLACE PROCEDURE        RRL_ACCEPT_ORDER2 (
 order_id int 
 )
as
tmpVar NUMBER;
tmpdec NUMBER;
tmp_number_of_pallets int;
tmp_uid_pallet varChar2(50);

cursor dddd is

   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
   
BEGIN



   tmpVar := 0;
   tmp_number_of_pallets:=1;
   
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;
 

DBMS_OUTPUT.put_line( ' Hello 1 ');  
 for  articul_row in dddd loop
 
 DBMS_OUTPUT.put_line( articul_row.ARTICUL );
 
 tmp_number_of_pallets:=1;
 tmpVar:=articul_row.COUNT1;
 
 
    while tmpVar>0 loop
        begin
     
    DBMS_OUTPUT.put_line( ' создается паллет ');  
    
             if( tmpVar<=articul_row.NORMA_UKLADKI ) then
                tmpdec:=tmpVar;
             else
                tmpdec:=articul_row.NORMA_UKLADKI;
             end if;
         
            tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul_row.ARTICUL) ,'_' ) , order_id ) , '_' ) , tmp_number_of_pallets )  ;
         
            insert into RABAEV.RRL_PALLETS ( UID_PALLET,
              ARTICUL ,
              CREATION_DATE ,
              EXPIRY_DATE ,
              UNIT_COUNT ,
              PRICE ,
              PRIHOD_NAKLAD_ID   ) values (
              tmp_uid_pallet ,
              articul_row.ARTICUL ,
              articul_row.EXPIRY_DATE , 
              articul_row.EXPIRY_DATE , 
              tmpdec , 
              articul_row.PRICE , 
              order_id 
              );
            tmpVar:=tmpVar-tmpdec;
            tmp_number_of_pallets:=tmp_number_of_pallets+1;
            
            DBMS_OUTPUT.put_line( tmp_number_of_pallets);  
            
        end;
    end loop;

  end loop;


DBMS_OUTPUT.put_line( ' end ');  

end;
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/

SHOW ERRORS;


CREATE OR REPLACE PROCEDURE        RRL_ACCEPT_ORDER3 (
 order_id int ,
 user_id1 varchar2
 )
as
tmpVar NUMBER;
event_id int ;

cursor dddd is

   SELECT UID_PALLET, ARTICUL , CREATION_DATE , EXPIRY_DATE , UNIT_COUNT , PRICE ,
    PRIHOD_NAKLAD_ID   FROM RRL_PALLETS  where PRIHOD_NAKLAD_ID=order_id;
   
   
BEGIN

update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=2  where ID = order_id ;
 

-- dbms_output.put_line('n='||event_id);
    
    
     for  pallet_row in dddd loop
     
        select RRL_EVENT_ID_SQ.NEXTVAL into event_id from dual;
        event_id:=event_id+1;


         insert into RABAEV.RRL_EVENTS
            (  ID_EVENT ,  
            CELL_FROM , 
            CELL_TO    ,    
            DATE_EVENT  ,  
            DATE_OF_ORDER,   
            COUNT_EVENT   , 
            TYPE_EVENT  ,  
            UID_POLETA    ,
            USER_ID  ,  
            PRIHOD_NAKL_ID ) values (
          event_id ,
          'IN_ACCEPT',
          'IN_DOCK',
          pallet_row.CREATION_DATE , 
          pallet_row.CREATION_DATE , 
          pallet_row.UNIT_COUNT , 
          1 ,
          pallet_row.UID_PALLET ,
          user_id1 ,
          pallet_row.PRIHOD_NAKLAD_ID 
            );


      end loop;

end;
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
/

SHOW ERRORS;


CREATE OR REPLACE PROCEDURE        RRL_GIVE_DESTINATION_CELL (

 pallet_uid varchar2 ,
 cell_destination out varchar2(50)


 )
as
tmpVar NUMBER;
PX int; 
PY int;
PZ int;
error_name  varchar2(250) ;
 
cursor ddd is 
select cell from RRL_CELLS where UID_POLETA_FOR_BLOCK = pallet_uid and TIME_FOR_BLOCK <=    SYSTIMESTAMP  ;

cursor pallet_row is 
select * from RRL_PALLETS where UID_PALLET = pallet_uid    ;


cursor cell_for_pick is
select c1.*  from RABAEV.RRL_CELLS c1, RABAEV.RRL_ARTICULS , RABAEV.RRL_PALLETS   where
    RRL_ARTICULS.CELL = C1.CELL and RRL_PALLETS.ARTICUL= RRL_ARTICULS.ACTICUL
    and RRL_PALLETS.UID_PALLET = pallet_uid 
    and (  ( UID_POLETA_FOR_BLOCK= pallet_uid) or ( TIME_FOR_BLOCK <= SYSTIMESTAMP )  );


BEGIN

DBMS_OUTPUT.put_line( ' Hello ');
 


error_name:='';
cell_destination:='NONE';
-- Если существует паллето-место, куда указан резерв на данный паллет 
-- (и время ожидания не истекло), выбирается первое паллето-место. 
for fff in  ddd loop
    cell_destination:=fff.cell;
    return;
end loop;

--Иначе, выбирается ячеека отбора для данного артикула  , если она с нулевыми (или меньшими)
-- остатками, и на которую нет действующего резерва другого паллета.


for cell_for_pick1 in cell_for_pick loop

PX:=cell_for_pick1.X;
PY:=cell_for_pick1.Y;
PZ:=cell_for_pick1.Z;

  select sum(REMAIN) into tmpVar from RRL_REMAINS where cell = cell_for_pick1.cell group by cell ;
    -- определяем остатки в ячейке отбора 

    if( ( (tmpVar) is null) or (tmpVar=0)  ) then
    
        cell_destination:=cell_for_pick1.cell;
        -- ФИКСИРУЕМ РЕЗЕРВ В ТАБЛИЦЕ ЯЧЕЕК 
        update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '12' minute
        where RRL_CELLS.CELL = cell_for_pick1.cell ;
        return;
    
    end if;
   
end loop;



--Если свободной ячейки отбора нет, среди всех ячеек хранения отбираем свободную 
--не зарезервированную ячейку с наименьшим весом. Вес определяется как расстояние 
--от ячейки отбора данного паллета. 
--Если такой ячейки нет, помещаем паллет в зону переполнения.
--ВЕС: пусть X - ячейки по горизонтали Y - вертикаль  Z  - параллельные ряды.   
-- расстояние между 2-мя ячейками = abs( X1 - X2 ) + 2* abs(Y1-Y2) + 20 * abs(Z1-Z2)

    begin

        select CELL into cell_destination from 
        RRL_CELLS where ( ( TIME_FOR_BLOCK is null ) or (TIME_FOR_BLOCK <=    SYSTIMESTAMP )) 
        and RRL_GET_CELL_REMAIN(CELL)=0  and ROWNUM <=1
        order by abs(PX-X)+2*abs(PY-Y)+40*abs(PZ-Z);
    EXCEPTION
         WHEN NO_DATA_FOUND THEN
            cell_destination:='OVERFLOW';
         WHEN OTHERS THEN
            cell_destination:='OVERFLOW';
    end;



end;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION RRL_sfera_ean_EAN_KOR
(
    articul varchar2
)

RETURN varchar2 IS
tmpVar varchar2(50);
BEGIN
   tmpVar := '';
   select EAN_KOR into tmpVar from RABAEV.SFERA_EAN where  TMC_UID=  articul and ROWNUM<=1 and RABAEV.SFERA_EAN.manualenter='N' ;
   RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return '';
         WHEN OTHERS THEN
           return '';
END RRL_sfera_ean_EAN_KOR;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION RRL_sfera_ean_EAN_SHT
(
    articul varchar2
)

RETURN varchar2 IS
tmpVar varchar2(50);
BEGIN
   tmpVar := '';
   select EAN_SHT into tmpVar from RABAEV.SFERA_EAN where  TMC_UID=  articul and ROWNUM<=1 and RABAEV.SFERA_EAN.manualenter='N' ;
   RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return '';
         WHEN OTHERS THEN
           return '';
END RRL_sfera_ean_EAN_SHT;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION RRL_sfera_ean_EAN_BL
(
    articul varchar2
)

RETURN varchar2 IS
tmpVar varchar2(50);
BEGIN
   tmpVar := '';
   select EAN_BL into tmpVar from RABAEV.SFERA_EAN where  TMC_UID=  articul and ROWNUM<=1 and RABAEV.SFERA_EAN.manualenter='N' ;
   RETURN tmpVar;   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return '';
         WHEN OTHERS THEN
           return '';
END RRL_sfera_ean_EAN_BL;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        ADD_RRL_OTHOD_NAKLAD(
  NAKLADNAME1           VARCHAR2      ,
  MAG_NO1               VARCHAR2      ,
  NAKLADDATE1           DATE          ,
  CREATIONDATE1         DATE          ,
  PLANNEDDELIVERYDATE1  DATE

)
 RETURN INT 
 
 IS
tmpVar int;

BEGIN
   tmpVar := 0;
   
       SELECT RABAEV.RRL_PRIHOD_NAKLAD_SQ.NEXTVAL INTO tmpVar FROM DUAL;
   
   
    INSERT INTO RABAEV.RRL_OTHOD_NAKLAD (
      ID,
      NAKLADNAME   ,
      MAG_NO       ,
      NAKLADDATE   ,
      CREATIONDATE ,
      PLANNEDDELIVERYDATE
      
  ) VALUES (
          tmpVar , 
          NAKLADNAME1   ,
          MAG_NO1       ,
          NAKLADDATE1   ,
          CREATIONDATE1 ,
          PLANNEDDELIVERYDATE1
    );
    


   
   
   RETURN tmpVar;
   
   
   
   
   
 
       
END ADD_RRL_OTHOD_NAKLAD;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        ADD_RRL_OTHOD_NAKLAD_ROWS(
ID_ROW1 int ,
    ID_NAKLAD1           int      ,
    ARTICUL1 varchar,
    COUNT2  number
)
 RETURN INT 
 IS
tmpVar int;
cond1 int;
BEGIN
   tmpVar := 0;
   
   select CONDITION into cond1  from RABAEV.RRL_OTHOD_NAKLAD where ID=ID_NAKLAD1 ;

if(cond1>=2 ) then
    return 0;
end if;  
   

if( ID_ROW1=0 ) then
  SELECT RABAEV.RRL_PRIHOD_NAKLAD_ROWS_SQ.NEXTVAL INTO tmpVar FROM DUAL;
  INSERT INTO RABAEV.RRL_OTHOD_NAKLAD_ROWS (
      ID,
      ID_NAKLAD   ,
      ARTICUL ,
      COUNT1      
  ) VALUES (
          tmpVar , 
          ID_NAKLAD1   ,
          ARTICUL1 ,
          COUNT2    
  );

else

    update RABAEV.RRL_OTHOD_NAKLAD_ROWS set ARTICUL=ARTICUL1 , COUNT1=COUNT2 where ID= ID_ROW1;

end if;

   RETURN tmpVar;
    
END ADD_RRL_OTHOD_NAKLAD_ROWS;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        RRL_INTERNAL_MOVE2(
pallet_id varchar2 , 
cell_to varchar2 ,
count1 number ,
user_id1 varchar2
)

RETURN varchar2

IS
count2 number;
tmpVar NUMBER;
art1 varchar2(50) ;
is_otbor int;
remain_in_cell_to number;
checks_passed int;
cell_from1 varchar2(50);
debug_mode int;
new_event_uid int;
BEGIN
    
count2:=count1;
   debug_mode:=0;
   tmpVar := 0;
   is_otbor:=0;
   remain_in_cell_to:=0;
   checks_passed:=0;
   cell_from1:='NONE';

    begin  --  СНАЧАЛА ИЩЕМ - ЕСТЬ - ЛИ ТАКОЙ ПАЛЛЕТ КУДА
    
        select cell into cell_from1 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell<>cell_to group by cell ;

        if(count2=0) then
            select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
        end if;

    exception
        WHEN NO_DATA_FOUND THEN
           return 'no pallet';
         WHEN OTHERS THEN
            begin
                    -- ПОПРОБУЕМ ИСКЛЮЧИТЬ ОТБОР ИЗ ПОИСКА
                    select  RABAEV.RRL_REMAINS.cell into cell_from1 from  RABAEV.RRL_REMAINS , RABAEV.RRL_CELLS  where
                         ( RABAEV.RRL_REMAINS.UID_POLETA=pallet_id) and ( RRL_REMAINS.CELL = RRL_CELLS.CELL ) and ( RRL_CELLS.OTBOR=0 ) and ( RRL_CELLS.cell<>cell_to )  ;
                         
                    if(count2=0) then
                        select remain into count2 from  RABAEV.RRL_REMAINS  where UID_POLETA=pallet_id and cell=cell_from1 ;
                    end if;
            exception
            
                WHEN NO_DATA_FOUND THEN
                    return 'other pallet1';
                WHEN OTHERS THEN
                    return 'other pallet2';
            end;
         
            
    end;
    

if( cell_to=cell_from1 ) then 
    return 'cell_to=cell_from1';
end if;   
    

    if(count2=0) then
        return 'count2=0';
    end if;

begin
    -- ЕСЛИ ПАЛЛЕТ ЕСТЬ, ПРОВЕРЯЕМ ЧТО ЯЧЕЙКА НАЗНАЧЕНИЯ = ЯЧЕЙКА ОТБОРА, ЛИБО 
    --  СВОБОДНА ( ОСТАТКОВ В НЕЙ НЕТ, РЕЗЕРВА НЕТ ) 
    select OTBOR into is_otbor from RABAEV.RRL_CELLS where CELL=cell_to ;
exception
         WHEN NO_DATA_FOUND THEN
           return 'no_pallet_cell_to';
         WHEN OTHERS THEN
           return 'other pallet1';
end;


if ( (is_otbor=0) and (cell_to<>'TRASH') and (cell_to<>'IN_DOCK') )  then

    begin
        select sum(REMAIN) into remain_in_cell_to from  RABAEV.RRL_REMAINS  where CELL=cell_to ;
    exception
             WHEN NO_DATA_FOUND THEN
               remain_in_cell_to:=0;
             WHEN OTHERS THEN
               remain_in_cell_to:=0;
    end;

    if remain_in_cell_to is null then
    remain_in_cell_to:=0;
    end if;

    if(remain_in_cell_to<=0)  then
        checks_passed:=1;
    else
    return 'cell_not_empty';    
    end if;

else
    checks_passed:=1;
end if;

        
    --  ЕСЛИ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ, ТО: 
    -- делаем запись таблицы RRL_EVENTS cell_to , cell_from ,date_event , count_event
    -- type_event = 2 , UID_POLETA , USER_ID

    if( checks_passed=0 ) then
     return 'fault';
    end if;
    

  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;

insert into RABAEV.RRL_EVENTS ( ID_EVENT , CELL_TO , CELL_FROM , DATE_EVENT ,  COUNT_EVENT ,
 TYPE_EVENT , UID_POLETA , USER_ID ) values
( new_event_uid , cell_to  , cell_from1 , SYSTIMESTAMP , count2 , 2 , pallet_id , user_id1  );


   RETURN 'ok';
      
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       return 'err1';
     WHEN OTHERS THEN
       return 'err2';
END RRL_INTERNAL_MOVE2;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        RRL_UPDATE_ARTICUL_EX(
-- ПРОЦЕДУРА ДЛЯ АВТОМАТИЧЕСКОЙ ЗАКАЧКИ ДАННЫХ ИЗ EXCEL
--Артикул    
articul4 varchar2 ,
--Наименование артикула     
name4 varchar2, 
--секция    (На самом деле идентификатор склада)    
section4 varchar2 ,
--ряд           = Z 
Z int ,
--стеллаж       = X*3
X3 int , 
--ярус          = Y
Y int ,
--место         = +X
X int ,
-- мест в ряду    
count_in_layer int ,
-- рядов в паллете    
layer_in_pall int ,
-- штук в паллете    
count_in_pal int , 
-- Ячейка отбора   
cell4 varchar ,
--Вес коробки
weight_of_kor number ,

-- Штрих-код штуки  
unit_barkode varchar,
--  Штрих-код коробки
kor_barkode varchar

)
 RETURN NUMBER IS
tmpVar varchar2(250);

BEGIN



    begin
        select cell into tmpVar from RABAEV.RRL_CELLS C where C.CELL=cell4;
    exception
            WHEN NO_DATA_FOUND THEN
                insert into RABAEV.RRL_CELLS (
                        CELL  ,
                      OTBOR    ,
                      BLOCKED_FOR_REMAINS    ,
                      BLOCKED_FOR_POPOLNENIE ,
                      X                      ,
                      Y                      ,
                      Z                      ,
                      BLOCKED_FOR_ACCEPT     ,
                      WARE_ID          
                )  
                values 
                (   
                    cell4 ,
                    1 ,
                    0 ,
                    0 ,
                    X3*3+X ,
                    Y ,
                    Z ,
                    0,
                    1
                );
            WHEN OTHERS THEN
                   null;
    end;


--return '';


--DBMS_OUTPUT.put_line( ' Hello 1 ');

    begin

        select AAA.ACTICUL into tmpVar from RABAEV.RRL_ARTICULS AAA where AAA.ACTICUL =   articul4 ;

        update RABAEV.RRL_ARTICULS set 
             NORMA_UKLADKI = count_in_pal ,
             CELL  = cell4 ,
             NAME  = name4,
             UNIT_TYPE  =  'шт'    ,
           BARCODE_SHT= unit_barkode,
              BARCODE_KOR  = kor_barkode ,
              BARCODE_BL  =  '' ,
              WEIGHT_OF_KOR = weight_of_kor,
              COUNT_IN_ROW = count_in_layer,
              ROWS_IN_PAL = layer_in_pall 
        where  ACTICUL =   articul4 ;
       
    exception
        WHEN NO_DATA_FOUND THEN
           
            insert into RABAEV.RRL_ARTICULS  (
                  ACTICUL   ,
                  NORMA_UKLADKI ,
                  CELL   ,
                  NAME   ,
                  UNIT_TYPE     ,
                  BARCODE_SHT ,
                  BARCODE_KOR    ,
                  BARCODE_BL     ,
                  WEIGHT_OF_KOR  ,
                  COUNT_IN_ROW  ,
                  ROWS_IN_PAL   
            ) values (
                articul4 ,
                count_in_pal ,
                cell4 ,
                name4 ,
                'шт' , 
                unit_barkode ,
                kor_barkode ,
                '' ,
                weight_of_kor ,
                count_in_layer  ,
                layer_in_pall 
            );
        
         WHEN OTHERS THEN
           null;
    end;
   


   
   
   RETURN '';
   
  
END RRL_UPDATE_ARTICUL_EX;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        RRL_CLOSE_OTHOD_NAKLAD
 -- ЗАКРЫВАЕТ ОТГРУЗОЧНУЮ НАКЛАДНУЮ 
(
    naklad_num int ,
    iser_id21 varchar2 
)
 RETURN varchar2 IS
tmpVar int;
current_cell  varchar2(50);
kolvo_otbora NUMBER  ;
new_event_id int;
EXPEDITION_CELL varchar2(50);


cursor rowss is 
select * from RABAEV.RRL_OTHOD_NAKLAD_ROWS where ID_NAKLAD = naklad_num ;

--Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
cursor rests_in_cell is
 select  RABAEV.RRL_REMAINS.REMAIN , RABAEV.RRL_REMAINS.UID_POLETA ,  RRL_PALLETS.EXPIRY_DATE 
  from RABAEV.RRL_REMAINS left join RABAEV.RRL_PALLETS on 
    RRL_REMAINS.UID_POLETA = RRL_PALLETS.UID_PALLET  
    where RRL_REMAINS.CELL = current_cell and RRL_REMAINS.REMAIN>0  order by RRL_PALLETS.EXPIRY_DATE  ; 


BEGIN

EXPEDITION_CELL:= concat( 'EX_' , naklad_num );
DBMS_OUTPUT.put_line(  'Начало' );

select condition into tmpVar from RABAEV.RRL_OTHOD_NAKLAD where ID = naklad_num;

if(tmpVar>=2) then   
    DBMS_OUTPUT.put_line(  'накладная закрыта' );
    return 'closed already';
end if;

/*
При закрытии отгрузочной накладной:
Для каждой строки: 
Определяем остатки в ячейке отбора в разрезе паллет, упорядоченных по срокам годности.
    Количество отбора - количество для отгрузки в накладную.

        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла    
    
если Количество_отбора > 0 
    Делаем проводку из ячейки 'excess' на отгрузочную накладную
Количество_отбора  = 0
конец если
*/


for naklad_row in rowss loop

tmpVar:=0;
kolvo_otbora:=naklad_row.COUNT1;


    DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА НАКЛАДНОЙ' );

    select CELL into  current_cell from  RABAEV.RRL_ARTICULS 
    where RRL_ARTICULS.ACTICUL=naklad_row.ARTICUL ;
    
    DBMS_OUTPUT.put_line(  '  ЯЧЕЙКА ОТБОРА=' );
    DBMS_OUTPUT.put_line(  current_cell );
    

    for  ddd8 in rests_in_cell loop
-- REMAIN
    
        DBMS_OUTPUT.put_line(  '  НОВАЯ СТРОКА ОСТАТКОВ ' );
        DBMS_OUTPUT.put_line(   ddd8.REMAIN );
        DBMS_OUTPUT.put_line(   ddd8.EXPIRY_DATE );
        DBMS_OUTPUT.put_line(   ddd8.UID_POLETA );
         DBMS_OUTPUT.put_line(  '  количество отбора= ' );     
         DBMS_OUTPUT.put_line(  kolvo_otbora );  
          
        
        if(kolvo_otbora>0) then
/*
        по всем паллетам в ячейке отбора и пока Количество_отбора  > 0
        
            если количество_отбора <= количество в текущей ячейке тогда
                делаем проводку из данной паллеты на накладную в количестве Количество_отбора  
                Количество_отбора  =0
            иначе
                делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
            конец если

        конец цикла  
*/          
            if(kolvo_otbora <= ddd8.REMAIN )  then
                -- UID_POLETA
                
                
                 SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                
                
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( new_event_id ,
                      current_cell,
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      2,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      naklad_num
                      ) ;
                    kolvo_otbora:=0;
                else
                  SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                -- делаем проводку из данной паллеты на накладную в количестве = Количество_товара данной паллеты в данонй ячейке отбора  
                -- Количество_отбора  = Количество_отбора  - Количество_товара данной паллеты в данонй ячейке отбора  
                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( new_event_id,
                      current_cell, 
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      ddd8.REMAIN ,
                      2,
                      ddd8.UID_POLETA ,
                      iser_id21 ,
                      naklad_num
                      ) ;
                      
                    kolvo_otbora:=kolvo_otbora-ddd8.REMAIN;
                
                
            end if;      

   
        end if;
    end loop;


         DBMS_OUTPUT.put_line(  '  почти конец ' );   
         DBMS_OUTPUT.put_line(  '  количество отбора= ' );     
         DBMS_OUTPUT.put_line(  kolvo_otbora );  

--если Количество_отбора > 0 
--    Делаем проводку из ячейки 'excess' на отгрузочную накладную
--Количество_отбора  = 0
--конец если
if(kolvo_otbora >0 )  then
                     SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;
                      insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( new_event_id ,
                      'EXCESS',
                      EXPEDITION_CELL,
                      SYSTIMESTAMP , 
                      kolvo_otbora ,
                      2,
                     concat( 'EXCESS_' , naklad_row.ARTICUL ) ,
                      iser_id21 ,
                      naklad_num
                      ) ;
kolvo_otbora:=0;
end if;

   DBMS_OUTPUT.put_line(  '  почти конец ' );   

end loop;

update  RABAEV.RRL_OTHOD_NAKLAD set condition = 2  where ID = naklad_num;
   DBMS_OUTPUT.put_line(  '  СОВСЕМ конец ' );   




   RETURN 'ok';
END RRL_CLOSE_OTHOD_NAKLAD;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        RRL_INFO_PALLET_RESTS
(
    pallet_id varchar2 
)

 RETURN varchar2 IS
tmpVar varchar(50);

cursor rrrr is select cell , remain from rrl_remains where uid_poleta=pallet_id;
                                                                                
                                                                                
BEGIN
tmpVar := '';
                    
for ddd in rrrr loop

tmpVar := concat( concat( concat( concat( tmpVar , ddd.Cell ) , '=' ) , to_char( ddd.remain )  ) , '; ' ) ;

--tmpVar :=    concat( tmpVar , pallet_id )    ;
                                                                    
end loop;


   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
      RETURN  'no rest';
     WHEN OTHERS THEN
       RETURN 'error';
END  RRL_INFO_PALLET_RESTS;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        ADD_SFERA_EAN2 (

    TMC_UID IN VARCHAR2,
      EAN_SHT      VARCHAR2 ,
  EAN_BL       VARCHAR2 ,
  EAN_KOR      VARCHAR2 ,
  MANUALENTER  CHAR,
  SHT_IN_BL    INTEGER,
  BL_IN_KOR    INTEGER,
  NAME         VARCHAR2   
) return int
IS
row_uid int;

BEGIN
    INSERT INTO RABAEV.SFERA_EAN (
      УИД,
      TMC_UID    , 
      EAN_SHT    ,
      EAN_BL      , 
      EAN_KOR     ,
      MANUALENTER  ,
      SHT_IN_BL   ,
      BL_IN_KOR    ,
      NAME    
  ) VALUES (
          RABAEV.SFERA_EAN_ID.NEXTVAL,
          TMC_UID     ,
          EAN_SHT    ,
          EAN_BL      , 
          EAN_KOR     ,
          MANUALENTER  ,
          SHT_IN_BL   ,
          BL_IN_KOR    ,
          NAME    
    );
    
    
    SELECT SFERA_EAN_ID.CURRVAL INTO row_uid FROM DUAL;
    return row_uid;
END  ADD_SFERA_EAN2;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        ADD_RRL_PRIH_NAKLAD_ROW (
    NAKLAD_ID int,
    articul string,
    expiury_date date ,
    count1 NUMBER ,
    price Number
) return int
IS
ID int;

BEGIN

    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD_ROWS (
    ORDID ,
    ARTICUL ,
    EXPIRY_DATE,
    count1 ,
    price ,
    ID  
  ) VALUES (
    NAKLAD_ID ,
    articul , 
    expiury_date ,
    count1 ,
    price ,
    RABAEV.RRL_ORDER_ROW_SEQ.NEXTVAL
    );
    
    SELECT RRL_ORDER_ROW_SEQ.CURRVAL INTO ID FROM DUAL;
    return ID;
END  ADD_RRL_PRIH_NAKLAD_ROW;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION RRL_ACCEPT_ORDER ( order_id int )

RETURN NUMBER 
IS
tmpVar NUMBER;

cursor dddd is
   SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID   FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL  where ORDID=order_id;
   
   
BEGIN
   tmpVar := 0;
   
   update RABAEV.RRL_PRIHOD_NAKLAD  set  condition=1  where ID = order_id  ;
   delete from RABAEV.RRL_PALLETS   where PRIHOD_NAKLAD_ID = order_id  ;
   
 
   -- Каждую строчку накладной : Создать множество паллет, 
   -- По каждой паллете сделать проводку, поместив ее в зону "ПРИЕМКИ".
   
   
   
              
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       NULL;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_ACCEPT_ORDER;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION RRL_TIME_FOR_RESERV RETURN int IS

BEGIN
   RETURN 12;
END RRL_TIME_FOR_RESERV;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        RRL_GET_CELL_REMAIN( cell_id varchar2 )
 RETURN NUMBER IS 
tmpVar NUMBER;
BEGIN
   tmpVar := 0;
   select sum( REMAIN ) into tmpVar from RRL_REMAINS where CELL = cell_id group by CELL;
   if(tmpVar is null) then
   tmpVar:=0;
   end if;
   
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN 0;
     WHEN OTHERS THEN
       -- Consider logging the error and then re-raise
       RAISE;
END RRL_GET_CELL_REMAIN;
/

SHOW ERRORS;


CREATE OR REPLACE function        RRL_GIVE_DESTINATION_CELL2 (
-- ДАННАЯ ПРОЦЕДУРА ПРЕДЛАГАЕТ ЯЧЕЙКУ ДЛЯ РАЗМЕЩЕНИЯ. ЕСЛИ ТОВАР РАЗМЕЩЕН, УКАЗЫВАЕТ КУДА.
 pallet_uid varchar2 , 
 ware_id1 int



 ) return varchar2
is


cell_destination  varchar2(50) ;
tmpVar NUMBER;
PX int; 
PY int;
PZ int;
m_RRL_TIME_FOR_RESERV int;
error_name  varchar2(250) ;
debug_mode int;
 
cursor ddd is 
select cell from RRL_CELLS where UID_POLETA_FOR_BLOCK = pallet_uid and TIME_FOR_BLOCK >=    SYSTIMESTAMP  ;

cursor pallet_row is 
select * from RRL_PALLETS where UID_PALLET = pallet_uid    ;


cursor cell_for_pick is
select c1.*  from RABAEV.RRL_CELLS c1, RABAEV.RRL_ARTICULS , RABAEV.RRL_PALLETS   where
    RRL_ARTICULS.CELL = C1.CELL and RRL_PALLETS.ARTICUL= RRL_ARTICULS.ACTICUL
    and RRL_PALLETS.UID_PALLET = pallet_uid 
    and (     (( UID_POLETA_FOR_BLOCK is null ) or ( TIME_FOR_BLOCK < SYSTIMESTAMP ))  );


BEGIN

--m_RRL_TIME_FOR_RESERV:=RRL_TIME_FOR_RESERV();
debug_mode:=1;

    if(debug_mode=1) then
        DBMS_OUTPUT.put_line( ' Hello 1 ');
    end if;


error_name:='';
cell_destination:='NONE';
-- Если существует паллето-место, куда указан резерв на данный паллет 
-- (и время ожидания не истекло), выбирается первое паллето-место. 
for fff in  ddd loop
    cell_destination:=fff.cell;
            if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Выбрана ячейка, назначенная раннее ');
            end if;
    return cell_destination;
end loop;

begin
-- ЕСЛИ ДАННЫЙ ПАЛЛЕТ ИМЕЕТ ОСТАТКИ В ЗОНЕ ХРАНЕНИЯ, ВЫДАЕМ ЭТОТ CELL 
    select C.CELL into cell_destination from RABAEV.RRL_REMAINS R , RABAEV.RRL_CELLS C 
        where R.CELL=C.CELL and R.UID_POLETA=pallet_uid 
        and R.REMAIN>0 and C.BLOCKED_FOR_REMAINS=0 and C.BLOCKED_FOR_POPOLNENIE=0 ;

    return cell_destination;
exception
        WHEN NO_DATA_FOUND THEN
        cell_destination:='NONE1';
         WHEN OTHERS THEN
         cell_destination:='NONE2';
end;

--Иначе, выбирается ячеека отбора для данного артикула  , если она с нулевыми (или меньшими)
-- остатками, и на которую нет действующего резерва другого паллета.
for cell_for_pick1 in cell_for_pick loop

PX:=cell_for_pick1.X;
PY:=cell_for_pick1.Y;
PZ:=cell_for_pick1.Z;



--  select sum(REMAIN) into tmpVar from RRL_REMAINS where cell = cell_for_pick1.cell group by cell ;

tmpVar:=RRL_GET_CELL_REMAIN( cell_for_pick1.cell);
    -- определяем остатки в ячейке отбора 

    if( ( (tmpVar) is null) or (tmpVar=0)  ) then
    
        cell_destination:=cell_for_pick1.cell;
        -- ФИКСИРУЕМ РЕЗЕРВ В ТАБЛИЦЕ ЯЧЕЕК 
        update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '30' minute
        where RRL_CELLS.CELL = cell_for_pick1.cell ;
        
            if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Выбрана свободная ячейка пикинга ');
            end if;
        
        return cell_destination;
    
    end if;
   
end loop;



--Если свободной ячейки отбора нет, среди всех ячеек хранения отбираем свободную 
--не зарезервированную ячейку с наименьшим весом. Вес определяется как расстояние 
--от ячейки отбора данного паллета. 
--Если такой ячейки нет, помещаем паллет в зону переполнения.
--ВЕС: пусть X - ячейки по горизонтали Y - вертикаль  Z  - параллельные ряды.   
-- расстояние между 2-мя ячейками = abs( X1 - X2 ) + 2* abs(Y1-Y2) + 20 * abs(Z1-Z2)




    begin

        select CELL into cell_destination from 
        RRL_CELLS where (BLOCKED_FOR_ACCEPT=0) and (OTBOR=0) and ( ( TIME_FOR_BLOCK is null ) or (TIME_FOR_BLOCK <=    SYSTIMESTAMP )) 
        and RRL_GET_CELL_REMAIN(CELL)=0  and ROWNUM <=1   and ware_id=ware_id1 
        order by 4*abs(PX-X)+abs(PY-Y)+40*abs(PZ-Z);
        
        -- фиксируем наш выбор на 12 минут.
        --update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '12' minute
        --where RRL_CELLS.CELL = cell_destination ;

            if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Найдена свободная ячейка хранения ');
            end if;

        
    EXCEPTION
         WHEN NO_DATA_FOUND THEN
            cell_destination:='OVERFLOW';
         WHEN OTHERS THEN
            cell_destination:='OVERFLOW2';
    end;



if( (cell_destination<>'OVERFLOW' ) and (cell_destination<>'OVERFLOW2' )  ) then
   update RRL_CELLS set UID_POLETA_FOR_BLOCK=pallet_uid , TIME_FOR_BLOCK = SYSTIMESTAMP + interval '30' minute
   where RRL_CELLS.CELL = cell_destination ;

end if;

   
    if(debug_mode=1) then
                DBMS_OUTPUT.put_line( ' Результат зафиксирован ');
    end if;  
     

return cell_destination;

end;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        ADD_RRL_PRIH_NAKLAD (

    NAKLAD_NUMBER varchar2,
    DATE_OF_NAKLAD date,
    DATE_OF_ACCEPT date,
    POSTAVSHIK_NAME varchar2,
    SM_NAKLAD_NUMBER varchar2
) return int
IS
ID int;

BEGIN
    INSERT INTO RABAEV.RRL_PRIHOD_NAKLAD (
      ID,
    NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER
      
  ) VALUES (
          RABAEV.RRL_PRIH_ORD_ID.NEXTVAL,
           NAKLAD_NUMBER ,
    DATE_OF_NAKLAD,
    DATE_OF_ACCEPT,
    POSTAVSHIK_NAME,
    SM_NAKLAD_NUMBER
  
    );
    
    SELECT RRL_PRIH_ORD_ID.CURRVAL INTO ID FROM DUAL;
    return ID;
END  ADD_RRL_PRIH_NAKLAD;
/

SHOW ERRORS;


CREATE OR REPLACE FUNCTION        RRL_ADD_INV_LINE
(

    CELL5         varchar2 , 
    articul5      varchar2 ,
    COUNT15        number ,
    date_of_expire5  date ,
    PRICE5  number ,
    inventory_id  int , 
    iser_id5 varchar2

)
 RETURN varchar2 IS
tmpVar varchar2(150);
tmp_uid_pallet varchar2(150);
new_event_id int ;

BEGIN

   tmpVar := '';
   -- СОЗДАЕМ НОВЫЙ ПАЛЛЕТ С АРТИКУЛОМ И СРОКОМ ГОДНОСТИ
   
  tmp_uid_pallet := concat( concat( concat( concat (concat( 'P_' ,articul5) ,'_G' ) , inventory_id ) , '_' ) , CELL5 )  ;
   
 /*
  begin 
  
    select UID_PALLET into tmpVar from RABAEV.RRL_PALLETS  where  UID_PALLET = tmp_uid_pallet ;


  exception
  
  WHEN NO_DATA_FOUND THEN
      */
        insert into RABAEV.RRL_PALLETS
          (
              UID_PALLET        ,
              ARTICUL           ,
              CREATION_DATE     ,
              EXPIRY_DATE       ,
              UNIT_COUNT        ,
              PRICE             ,
              PRIHOD_NAKLAD_ID  )  values 
          (
              tmp_uid_pallet , 
              articul5,
              SYSTIMESTAMP ,
              date_of_expire5 ,
              COUNT15 ,
              PRICE5 , 
              -1* inventory_id
          )  ;
  
  --end;




   -- ЗАПИСЫВАЕМ ЕГО КОЛИЧЕСТВо В ЯЧЕЙКУ
   
    SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_id FROM dual;

                    insert into RABAEV.RRL_EVENTS ( ID_EVENT , 
                          CELL_FROM      ,
                          CELL_TO  ,
                          DATE_EVENT  ,
                          COUNT_EVENT ,
                          TYPE_EVENT ,
                          UID_POLETA ,
                          USER_ID    ,
                          OTHOD_NAKL_ID       
                      ) values ( 
                      new_event_id ,
                      'INVENT',
                      cell5,
                      SYSTIMESTAMP , 
                      COUNT15 ,
                      1,
                      tmp_uid_pallet ,
                      iser_id5 ,
                      ( -1* inventory_id )
                      ) ;
    
   
   -- ***************************************************
   
   
   RETURN tmpVar;
  
       
END RRL_ADD_INV_LINE;
/

SHOW ERRORS;


CREATE OR REPLACE VIEW ОШИБКИСБОРКИ
AS 
SELECT 
          ORDER_NUMBER , CONDITION
          
   FROM rabaev.ORDER_AUDIT
   WHERE CONDITION = 'ЗОНА_ОШИБОК';


CREATE OR REPLACE VIEW ALT_PRODUCT_BARCODE
AS 
SELECT "TMC_UID",
          "EAN_SHT",
          "EAN_BL",
          "EAN_KOR",
          "MANUALENTER",
          "SHT_IN_BL",
          "BL_IN_KOR",
          УИД ,
          Name 
          
   FROM rabaev.sfera_ean
   WHERE manualenter = 'Y';


CREATE OR REPLACE VIEW RRL_PRIHOD_NAKLAD_ROWS_WITH
AS 
SELECT RRL_PRIHOD_NAKLAD_ROWS.ARTICUL , RRL_PRIHOD_NAKLAD_ROWS.COUNT1 , RRL_PRIHOD_NAKLAD_ROWS.PRICE ,
  RRL_PRIHOD_NAKLAD_ROWS.EXPIRY_DATE , RRL_PRIHOD_NAKLAD_ROWS.ID  , RRL_ARTICULS.NORMA_UKLADKI , 
  RRL_ARTICULS.CELL  ,  ORDID
  
    FROM rabaev.RRL_PRIHOD_NAKLAD_ROWS
   left join rabaev.RRL_ARTICULS  on  RRL_PRIHOD_NAKLAD_ROWS.ARTICUL = RRL_ARTICULS.ACTICUL;


CREATE OR REPLACE TRIGGER SFERA_EAN_TRG
BEFORE INSERT 
ON SFERA_EAN FOR EACH ROW
DECLARE
BEGIN


if :New.УИД is null then
  SELECT SFERA_EAN_ID.NEXTVAL
    INTO :New.УИД
    FROM dual;
    end if;
    



END;
/
SHOW ERRORS;


CREATE OR REPLACE TRIGGER ORDER_MOV_HIST_TRG
BEFORE INSERT 
ON ORDER_MOV_HIST FOR EACH ROW
DECLARE
BEGIN

if :New.ID is null then

  SELECT RABAEV.ORDER_MOV_HIST_ID.NEXTVAL
    INTO :New.ID 
        FROM dual;
        
end if;
    
 

END;
/
SHOW ERRORS;


CREATE OR REPLACE TRIGGER RRL_t_event_update_remain
  AFTER INSERT
  ON RRL_EVENTS   for each row
declare
  vRemain number;
  procedure UpRemain
    -- Процедура увеличивает остаток в ячейке :new.cell_to на :new.count_event
  is

  begin
    -- смотрим, что лежит в новой ячейке
    -- проверяем только наличие по текущей полете... Хорошо было бы проверить эту ячейку на
    -- наличие в ней чего-нить от других полет и сделать какие-нибудь выводы ...
    select sum(remain) into vRemain
    from RRL_remains
    where cell = :new.cell_to
    and uid_poleta = :new.uid_poleta;

    if vRemain is null then
      -- в ячейке таких полет не обнаружено. добавляем запись
     insert into RRL_remains (uid_poleta, cell, remain , othod_nakl_id ) 
     values (:new.uid_poleta, :new.cell_to, :new.count_event , :new.othod_nakl_id  );
    else
      -- есть какой-то остаток
      update RRL_remains
      set remain = remain+:new.count_event , othod_nakl_id =  :new.othod_nakl_id 
      where cell = :new.cell_to
      and uid_poleta = :new.uid_poleta;
    end if;   
    
  end;


  
  
  
  
  procedure DownRemain
    -- Процедура уменьшает остаток в ячейке :new.cell_from на :new.count_event
  is
  begin
    select sum(remain) into vRemain -- на всякий случай сделали сумму
    from RRL_remains
    where cell = :new.cell_from
    and uid_poleta = :new.uid_poleta;

    if vRemain is null then 
      -- странно, однако, в ячейке не та полета, или ячейка совсем пустая...
      -- запишем отрицательный остаток 
      insert into RRL_remains(uid_poleta, cell, remain  ) 
      values (:new.uid_poleta , :new.cell_from, -:new.count_event  );
    elsif vRemain = :new.count_event then
      -- из ячейки все будет выбрано подчистую, она останется пустая.
      -- поэтому наверно остаток можно удалить
      delete from RRL_remains
      where cell = :new.cell_from
      and uid_poleta = :new.uid_poleta;
    else
      -- остаток какой-то не нулевой остается (может быть и отрицательный)
      -- проапдейтим остаток
      update RRL_remains
      set remain = remain-:new.count_event
      where cell = :new.cell_from
      and uid_poleta = :new.uid_poleta;
    end if;   
  end;  

begin

    if(:new.count_event<>0) then
      if :new.type_event = 1 then  
        -- если событие это приемка
        -- добавляем запись в таблицу остатков
        UpRemain;
      elsif :new.type_event = 2 then  
        -- если событие это перемещение
        -- меняем данные в таблице остатков
        DownRemain;
        UpRemain;
      elsif :new.type_event = 3 then  
        -- если событие это отбор
        DownRemain;
      end if;
    end if;
  
end;
/
SHOW ERRORS;


CREATE OR REPLACE TRIGGER RRL_PRIHOD_NAKLAD_TRG
BEFORE INSERT 
ON RRL_PRIHOD_NAKLAD FOR EACH ROW
DECLARE
BEGIN


if :New.ID is null then
  SELECT RRL_PRIH_ORD_ID.NEXTVAL
    INTO :New.ID
    FROM dual;
    end if;
    



END;
/
SHOW ERRORS;

ALTER TRIGGER RRL_PRIHOD_NAKLAD_TRG DISABLE;


ALTER TABLE RRL_INVETARIZ ADD (
  CONSTRAINT RRL_INVETARIZ_PK
 PRIMARY KEY
 (ID));

ALTER TABLE RRL_INVENTARIZ_LINES ADD (
  CONSTRAINT RRL_INVENTARIZ_LINES_PK
 PRIMARY KEY
 (ID_LINE));

ALTER TABLE ORDER_AUDIT_ERROR_LINES ADD (
  CONSTRAINT ORDER_AUDIT_LINES_PK
 PRIMARY KEY
 (ORDER_NUMBER, UID1));

ALTER TABLE RUSERS ADD (
  CONSTRAINT RUSERS_PK
 PRIMARY KEY
 (ID));

ALTER TABLE TZS ADD (
  CONSTRAINT TZS_PK
 PRIMARY KEY
 (КОД));

ALTER TABLE LOT_AUDIT ADD (
  CONSTRAINT LOT_AUDIT_PK
 PRIMARY KEY
 (SSCC));

ALTER TABLE ORDER_MOV_HIST ADD (
  CONSTRAINT ORDER_MOV_HIST_PK
 PRIMARY KEY
 (ID));

ALTER TABLE RRL_EVENTS ADD (
  CONSTRAINT RRL_EVENTS_PK
 PRIMARY KEY
 (ID_EVENT));

ALTER TABLE RRL_PALLETS ADD (
  CONSTRAINT RRL_PALLETS_PK
 PRIMARY KEY
 (UID_PALLET));

ALTER TABLE RRL_ARTICULS ADD (
  CONSTRAINT RRL_ARTICULS_PK
 PRIMARY KEY
 (ACTICUL));

ALTER TABLE RRL_CELLS ADD (
  CONSTRAINT RRL_CELLS_PK
 PRIMARY KEY
 (CELL));

ALTER TABLE RRL_PRIHOD_NAKLAD ADD (
  CONSTRAINT RRL_PRIHOD_NAKLAD_PK
 PRIMARY KEY
 (SM_NAKLAD_NUMBER));

ALTER TABLE RRL_PRIHOD_NAKLAD_ROWS ADD (
  CONSTRAINT RRL_PRIHOD_NAKLAD_ROWS_PK
 PRIMARY KEY
 (ID));

ALTER TABLE RRL_OTHOD_NAKLAD ADD (
  CONSTRAINT RRL_OTHOD_NAKLAD_PK
 PRIMARY KEY
 (ID));

ALTER TABLE RRL_OTHOD_NAKLAD_ROWS ADD (
  CONSTRAINT RRL_OTHOD_NAKLAD_ROWS_PK
 PRIMARY KEY
 (ID));

