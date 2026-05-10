prompt Applying supplemental legacy objects for WindowsApplication2 xp12
set define off

--  New table rrl_constants  --
-------------------------------
-- Create table
create table RRL_CONSTANTS
(
  name  VARCHAR2(50),
  value VARCHAR2(255)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
-- Create/Recreate indexes 
create index RRL_CONSTANTS_I1 on RRL_CONSTANTS (NAME)
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

-----------------------------------------

--  New table rrl_object  --
----------------------------
-- Create table
create table RRL_OBJECT
(
  object_name    VARCHAR2(255) not null,
  business_field VARCHAR2(255),
  parent_object  VARCHAR2(255),
  comment1       VARCHAR2(1024),
  type1          VARCHAR2(50) default 'TABLE',
  article1       VARCHAR2(255)
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );
-- Create/Recreate primary, unique and foreign key constraints 
alter table RRL_OBJECT
  add constraint RRL_OBJECT_PK primary key (OBJECT_NAME)
  using index 
  tablespace USERS
  pctfree 10
  initrans 2
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

------------------------------

--  New table rrl_ware_masks  --
--------------------------------
-- Create table
create table RRL_WARE_MASKS
(
  ware_mask     VARCHAR2(255),
  ware_mask_ids VARCHAR2(255),
  ord_id        INTEGER
)
tablespace USERS
  pctfree 10
  initrans 1
  maxtrans 255
  storage
  (
    initial 64K
    minextents 1
    maxextents unlimited
  );

---------------------------

--  New function rrl_tranport_task_history_add  --
--------------------------------------------------
CREATE OR REPLACE FUNCTION RRL_TRANPORT_TASK_HISTORY_ADD (
 TT_ID int, 
 TRANSTYPE1 varchar2, 
 TRANSPORT1 varchar2, 
 ROUTETYPE1 varchar2, 
 WAVE1 varchar2, 
 SHIPMENT_DATE1 date, 
 VODITEL_ID1 int, 
 PRIMECHANIE1 varchar2,
 DOCK1 varchar2,
 user_id1 varchar2 ,
 OPERATION1 varchar2
 )
 RETURN varchar2 
 IS 
 next_hist_id  int;
begin

 SELECT RRL_TRANSPORT_TASK_HISTORY_SQ.NEXTVAL INTO next_hist_id FROM DUAL;

 insert into    RRL_TRANSPORT_TASK_HISTORY  ( id , ttask_id , TRANSTYPE  ,  TRANSPORT   , ROUTETYPE   , SHIPMENT_TIME   ,
        SHIPMENT_DATE , VODITEL_ID  , PRIMECHANIE , DOCK , user_id , OPERATION , event_time ) values 
        ( next_hist_id , TT_ID , TRANSTYPE1 , TRANSPORT1 , ROUTETYPE1 , WAVE1 , SHIPMENT_DATE1 , 
        VODITEL_ID1 , PRIMECHANIE1 ,DOCK1 ,user_id1 , OPERATION1 , systimestamp ) ;
 
 return 'ok';
 
 END RRL_TRANPORT_TASK_HISTORY_ADD ;
/

----------------------------------------------

--  New function rrl_auth3  --
------------------------------
CREATE OR REPLACE FUNCTION RRL_AUTH3
(
    login varchar2 , 
    pass1 varchar2 ,
    version1 varchar2 ,
    ip_addr1 varchar2 
    
)
 RETURN int
  IS
tmpVar int;
RRL_LOGIN_HISTORY_ID int;
BEGIN

begin

select RRL_LOGIN_HISTORY_SQ.Nextval into RRL_LOGIN_HISTORY_ID from dual;

insert into RABAEV.RRL_LOGIN_HISTORY
(
  ID , NAME ,
  START_TIME , IP_ADDR ,
  VERSION , PASS , SUCCSESS    
) values ( RRL_LOGIN_HISTORY_ID , login , systimestamp , ip_addr1 , version1 , pass1 , 0 );



select V.ALLOW into tmpVar  from RABAEV.RRL_VERSIONS V where V.VERSION = version1 and V.ALLOW=1;
EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -3;
     WHEN OTHERS THEN
           return -4;
       RAISE;
   
end;

   select  ware_id into tmpVar  from RABAEV.RUSERS where ID = login and  PASS = pass1 and  DELETED=0 and PRAVO_ADMIN_LOGIN=1;
    update RABAEV.RRL_LOGIN_HISTORY set SUCCSESS=1 where ID=RRL_LOGIN_HISTORY_ID;
   
   RETURN tmpVar;
   
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
           return -1;
     WHEN OTHERS THEN
           return -2;
       RAISE;
       
END RRL_AUTH3;
/

----------------------------------------

--  New package pk_pivot  --
----------------------------
create or replace package pk_pivot
--AUTHID CURRENT_USER
as
  --code based on famous Tom Kyte's books examples
  --but not copy-pasted from there

  type refcursor is ref cursor;

  type array is table of varchar2(30);

  type array_varchar2 is table of varchar2(255);

  function pivotsql( p_query in varchar2, --query string which returns data you want to make crosstab on
                     p_rowfields in varchar2, --row fields separated by comma
                     p_columnfield in varchar2, --one column field
                     p_function in varchar2, --aggregate function ('SUM','AVG','COUNT','MIN','MAX')
                     p_functionfield in varchar2, --field for aggregate function
                     p_page in number default 1 --page from right to left (not all columns can be shown on one page)
                   ) return varchar2;                                                                                                 --returns query text for crosstab
/*
example:
SELECT PK_CROSSTAB.PivotSQL('SELECT * FROM scott.emp','empno','job','sum','sal') FROM SYS.DUAL

--------
SELECT deptno
,sum(DECODE(job,'BOSS',sal,null)) as BOSS
,sum(DECODE(job,'FIN',sal,null)) as FIN
,sum(DECODE(job,'HR',sal,null)) as HR
,sum(DECODE(job,'Sales',sal,null)) as Sales
FROM (SELECT * FROM scott.emp)
GROUP BY deptno
ORDER BY deptno
*/

end;
/

--------------------------

--  New package revizion  --
----------------------------
create or replace package REVIZION is

  -- Author  : RRABAEV
  -- Created : 15.06.2011 10:04:49
  -- Purpose : пїЅпїЅпїЅпїЅпїЅпїЅпїЅ
  
function revision_cond( rev_id int ) return int ;
function clear_cell2( cell1 varchar2     ) return int;
function clear_cell( cell1 varchar2 , puid varchar2   ) return int ;
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int;
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int ;
function revision_cell_kor( cell1 varchar2 , revision_id1 int ,  count2 number , user_id3 varchar2 ) return varchar2 ;
function add_row_2_reviz_type_art( cell1 varchar2 , revision_id1 int   ) return int;
function  RRL_REVIZION_CELL_PALL( articul1 varchar2, CELL1 varchar2 , count_pal int , 
   revision_row_id1 int , user_id1 varchar2 ) return varchar2 ;
   
function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int ;
function articul_name( art varchar2 ) return varchar2;
function update_revision_row( cell1 varchar2 , articul2 varchar2 ,  revision_rowid int ,  rev_id2 int   ) return int;
function CreateNaklad_2_revizion( rev_id1 int ) return int ;
function revision_cell_sht_deleted( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 ;
function  RRL_REVIZION_CELL_SHT( articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , user_id1 varchar2 ) return varchar2;
function  RRL_REVIZION_CLEAR_MINUS( revision_id1 int , user_id1 varchar2 ) return int ;

FUNCTION  RRL_INV_CREATE_LINE5 
( 
    cell1 varchar2 ,
    articul2 varchar2,
    count1 NUMBER ,
    expiury_date date ,
    fasovka_id1 int ,
    brak_perc1 number ,
    pall_weight1 number , 
    pall_n int ,
    tn_weight1 number ,
    count_kor1 number ,
    user_id2 varchar2 , 
    NAKLAD_ID int
) return varchar2;

function rev_create_snap_shot_after( rev_id int ) return int ;
function rev_create_snap_shot_before( rev_id int ) return int ;
FUNCTION  close_revision( rev_id int ) return int;

function remain_after( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number  ;
function remain_before( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number  ;


end REVIZION;
/

----------------------------------

--  New package transport_task  --
----------------------------------
create or replace package TRANSPORT_TASK is

 
  function PRINT_PALLET_WEIGHT( PALLET_UID2  varchar2 ) return varchar2;

  -- Public function and procedure declarations
  function can_print( tt_id int , user_id1 varchar2 ) return varchar2 ;
  function pallet_count( tt_id int ) return number;
function tt_wares( tt_id int ) return varchar2 ;
function stoim_pall_sb( pall_uid1 varchar2 ) return number ;
function stoim_tt( tt_id int )  return number ;
function test1 return int;
FUNCTION TT_UNREADY_COUNT( IDTT int ) RETURN number ;
FUNCTION TT_READY_PERC( IDTT int ) RETURN number ;
function tt_unready_wares( tt_id int ) return varchar2;
FUNCTION TT_VODITEL_TEL( VODITEL_ID1 int ) RETURN varchar2;
FUNCTION TT_REORDER_ADR( IDTT int ) RETURN number ;

end TRANSPORT_TASK;
/

---------------------------------

--  New package body pk_pivot  --
---------------------------------
create or replace package body pk_pivot
as
  procedure formatparam(var_data in varchar2, var_type in number, out_decode in out varchar2, out_col in out varchar2);


  function pivotsql(p_query in varchar2, p_rowfields in varchar2, p_columnfield in varchar2, p_function in varchar2, p_functionfield in varchar2
, p_page in number default 1 )
    return varchar2
  as
    l_max_cols        number;
    l_query           long;
    l_columnnames     array_varchar2 := array_varchar2();
    l_cursor          refcursor;
    tmp               long;
    --dbms_sql types:
    l_thecursor       integer default dbms_sql.open_cursor ;                                                                           --get col types
    l_colcnt          number default 0 ;
    l_desctbl         dbms_sql.desc_tab;
    col_num           number;
    l_columnfieldtype number;
    --decode names
    o_decode          varchar2(50);
    o_col             varchar2(50);
    l_cols_per_page   number := 50;
    l_begcol          number;
    l_endcol          number;
  begin
    --check params
    if instr(p_columnfield, ',') > 0
    then
      raise_application_error(-20001, 'Can use only 1 columnfield');
    elsif upper(p_function) not in ('SUM', 'AVG', 'COUNT', 'MIN', 'MAX')
    then
      raise_application_error(-20001, 'Can use only standard aggregate functions');
    end if;


    /* analyse query */
    dbms_sql.parse(l_thecursor, p_query, dbms_sql.native);
    /* get described columns for analysed query */
    dbms_sql.describe_columns(l_thecursor, l_colcnt, l_desctbl);

    /* Tom Kyte:
    * Following loop could simply be for j in 1..col_cnt loop.


    Here we are simply illustrating some of the PL/SQL table
    features.
    */
    col_num := l_desctbl.first;

    loop
      exit when (col_num is null);

      --find column field type
      if l_desctbl(col_num).col_name = upper(p_columnfield)
      then
        l_columnfieldtype := l_desctbl(col_num).col_type;
      --dbms_output.put_line('Col#:'||col_num||' Name:'||l_descTbl(col_num).col_name||' Type:'||l_descTbl(col_num).col_type);
      end if;

      col_num := l_desctbl.next(col_num);
    end loop;

    --return 'test ok';

    -- figure out the column names we must support for horizontal cross
    if (p_columnfield is not null)
    then
      tmp :=
           'SELECT DISTINCT '
        || p_columnfield
        || ' FROM ('
        || p_query
        || ') ORDER BY '
        || p_columnfield;

      -- dbms_output.put_line('columns cursor:'||tmp);
      open l_cursor for tmp;

      loop
        l_columnnames.extend;

        fetch l_cursor into l_columnnames(l_columnnames.count);

        --dbms_output.put_line('l_columnnames:'||l_columnnames(l_columnnames.COUNT));
        exit when l_cursor%notfound;
      end loop;

      close l_cursor;
    -- execute immediate 'SELECT DISTINCT ' || p_columnfield || ' FROM (' || p_query || ')' bulk collect into l_columnnames ;

    else
      raise_application_error(-20001, 'Cannot figure out max cols');
    end if;

    -- Now, construct the query that can answer the question for us...
    l_query :=
      'SELECT '
      || p_rowfields;


    l_begcol :=
      l_cols_per_page
      * (p_page
         - 1)
      + 1;
    l_endcol :=
      l_cols_per_page
      * p_page;


    if l_begcol > l_columnnames.count
                  - 1
    then
      l_begcol :=
        l_columnnames.count
        - 1;
    end if;


    if l_endcol > l_columnnames.count
                  - 1
    then
      l_endcol :=
        l_columnnames.count
        - 1;
    end if;


    --for i in 1 .. l_columnnames.count-1 loop
    for i in l_begcol .. l_endcol
    loop
      formatparam(l_columnnames(i), l_columnfieldtype, o_decode, o_col);                                                               --format params
      l_query :=
           l_query
        || ','
        || p_function
        || '(DECODE('
        || p_columnfield
        || ','
        || o_decode
        || ','
        || p_functionfield
        || ',null)) as "'
        || o_col
        || '" ';                                                                                                             --" пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ
    end loop;

    l_query :=
         l_query
      || ' FROM ('
      || p_query
      || ')';


    l_query :=
         l_query
      || ' GROUP BY '
      || p_rowfields
      || ' ORDER BY '
      || p_rowfields;


    /* close cursor */
    dbms_sql.close_cursor(l_thecursor);


    return l_query;
  exception
    when others
    then
      /* close cursor */
      dbms_sql.close_cursor(l_thecursor);
      raise_application_error(-20001, 'Error in PivotSQL:'
                                      || sqlerrm);
  end;

  --=========================


  procedure formatparam(var_data in varchar2, var_type in number, out_decode in out varchar2, out_col in out varchar2)
  --format parameter based on its type - for PivotSQL
  --get parameter and its type
  -- return strings for decode function and column name
  /* dbms_sql.describe_columns types:
  DATE Type:12
  Varchar2 Type:1
  Number Type:2
  */
  is
  begin
    if var_data is null
    then
      out_decode := 'NULL';
      out_col := '==NULL==';
    elsif var_type = 1
    then                                                                                                                                   -- Varchar2
      out_decode :=
           ''''
        || var_data
        || '''';                                                                                                                          --add quotes
      out_col := substr(var_data, 1, 30);
    elsif var_type = 2
    then                                                                                                                                      --Number
      out_decode := var_data;                                                                                                             --do nothing
      out_col := substr(var_data, 1, 30);
    elsif var_type = 12
    then                                                                                                                                        --DATE
      out_decode :=
           'to_date('''
        || var_data
        || ''')';                                                                                                            --format as internal date
      out_col := to_char(to_date(var_data), 'YYYY-MM-DD');
    else
      out_decode :=
        '== UNDEFINED TYPE:'
        || var_type;
      out_col := '== UNDEFINED TYPE';
    end if;
  exception
    when others
    then
      raise_application_error(-20001, 'Error in FormatParam:'
                                      || sqlerrm);
  end;
end;
/

-------------------------------

--  New package body revizion  --
---------------------------------
create or replace package body REVIZION is

 
function revision_cond( rev_id int ) return int is
  ret int;
begin 
  select rr.condition into ret from rrl_revizion rr where id= rev_id;
  return ret;       
exception
         when no_data_found then return -1;
end;

 --- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int is
id1 int;    

  begin
      insert into RABAEV.RRL_REVIZION
      (
        WARE_ID     ,
        CREATE_DATE  ,
        CONDITION   ,
        USER_ID    
      )values (  ware_id1, sysdate  , 0 , user_id1  ) ;
      select RABAEV.RRL_REVISION_SQ.Currval into id1 from dual;

    return id1;
  end;

-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ
function clear_cell( cell1 varchar2 , puid varchar2   ) return int is  
begin

delete from rrl_remains rr where   rr.cell=cell1 and rr.uid_poleta= puid;
return  1;
exception
  when others then null;
end;

-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ
function clear_cell2( cell1 varchar2     ) return int is  
begin
delete from rrl_remains rr where   rr.cell=cell1  ;
return  1;
exception
  when others then null;
end;

-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ 
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor sss is 
       select  rm.cell , pts.articul 
       from rrl_remains rm , rrl_pallets pts where 
       rm.cell=cell1 and pts.uid_pallet=rm.uid_poleta
       group by rm.cell , pts.articul ;

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;
  
  delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  and CELL= cell1;
  
  
  for s in sss loop
    
      insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , s.cell , sysdate , s.articul );
      select RRL_REVISION_ROW_SQ.Currval  into id1 from dual;

  end loop;


  return id1;
end;


-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ 
function add_row_2_reviz_type_art( cell1 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor rema is 
select distinct pl.articul  from rrl_remains rems, rrl_pallets pl 
   where rems.uid_poleta=pl.uid_pallet and  rems.cell=cell1 ; 

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;
-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ 
-- пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ . 
   for rr in rema loop
       delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  
       and CELL= cell1 and articul1=rr.articul ;
       insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , cell1 , sysdate , rr.articul );
       
   end loop;

  return id1;
end;


-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ 
function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor rema is 
select distinct pl.articul  from rrl_remains rems, rrl_pallets pl 
   where rems.uid_poleta=pl.uid_pallet and  rems.cell=cell1 and pl.articul=articul2 ; 

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;
-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ 
-- пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ . 
   for rr in rema loop
       delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  
       and CELL= cell1 and articul1=rr.articul ;
       insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , cell1 , sysdate , rr.articul );
       
   end loop;

  return id1;
end;



-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ 
function update_revision_row( cell1 varchar2 , articul2 varchar2 ,  revision_rowid int ,  rev_id2 int   ) return int is
   

revision_id1 int ;
row_ret int;
begin
  
    if(  revision_rowid > 0 ) then

          select rr.revision_id into revision_id1 from 
                 rrl_revision_row rr where id = revision_rowid;
    
          if revision_cond(revision_id1)>1 then
            return 0;
          end if;  
        -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ 
        -- пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ . 
          update    RABAEV.RRL_REVISION_ROW rr set  rr.cell=cell1 , rr.articul1=articul2 
                    where id=revision_rowid ; 
          return revision_id1;
      else

      insert into RABAEV.RRL_REVISION_ROW  ( REVISION_ID , CELL , ARTICUL1      ) values 
           (rev_id2 , cell1 , articul2 );
           select RRL_REVISION_ROW_SQ.CURRVAL into row_ret from dual;
           return  row_ret;
      
    end if;
  
  --exception
  --  when no_data_found then return -1;
  --  when others then return -2;
  
end;




function articul_name( art varchar2 ) return varchar2 is
  ret varchar2(255);
  begin
    select name into ret from rrl_articuls where acticul=art;
    return ret;
    exception
      when no_data_found then return '';
      when others then return '';
  end;

function revision_cell_kor( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 is
rem5  varchar2(1024);
rem4  varchar2(255);
revision_row_id2 int;
condition2 int;
begin 

      begin  -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ ---  
         select rev.condition into condition2 from rrl_revizion rev where rev.id= revision_id1;
         if( condition2=2 ) then
             return 'пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ';
         end if;
         exception 
           when no_data_found then return 'пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅ';
      end;  -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ --- 
  
      begin  -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ ---      
           select id  into revision_row_id2 from RABAEV.RRL_REVISION_ROW where cell=cell1 and REVISION_ID = revision_id1  and rownum<=1 ;  
           exception 
             when no_data_found then revision_row_id2:=add_row_2_revizion(cell1 , revision_id1 ) ;
      end;  -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ --- 
      
      
    rem4 := RABAEV.RRL_REVIZION_CELL_KOR( CELL1  ,    count2 ,    user_id3 )  ;
    
    rem5 :=concat( concat( ' пїЅпїЅпїЅ=' , to_char(count2) ) , concat( 'пїЅпїЅпїЅ. пїЅпїЅпїЅпїЅпїЅ=' , to_char( sysdate )  ));
    update RABAEV.RRL_REVISION_ROW set remark1= concat (remark1 , concat(rem5, rem4) )   , 
      count_kor=count2
     where id=revision_row_id2 ;
     return rem4;
      

end;



function revision_cell_sht_deleted( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ) return varchar2 is
rem5  varchar2(1026);
rem4  varchar2(255);
revision_row_id2 int;
condition2 int;
begin 

      begin  -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ ---  
         select rev.condition into condition2 from rrl_revizion rev where rev.id= revision_id1;
         if( condition2=2 ) then
             return 'пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ';
         end if;
         exception 
           when no_data_found then return 'пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅ';
      end;  -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ --- 
  
      begin  -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ ---      
           select id  into revision_row_id2 from RABAEV.RRL_REVISION_ROW where cell=cell1 and REVISION_ID = revision_id1  and rownum<=1 ;  
           exception 
             when no_data_found then revision_row_id2:=add_row_2_revizion(cell1 , revision_id1 ) ;
      end;  -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ --- 
      
      
    rem4 := RABAEV.RRL_REVIZION_CELL( CELL1  ,    count2 ,    user_id3 )  ;
    
    rem5 :=concat( concat( ' пїЅпїЅпїЅ=' , to_char(count2) ) , concat( 'sht. пїЅпїЅпїЅпїЅпїЅ=' , to_char( sysdate )  ));
    update RABAEV.RRL_REVISION_ROW set remark1= concat (remark1 , concat(rem5, rem4) )   , 
      count_kor=count2
     where id=revision_row_id2 ;
     return rem4;
      

end;


-- ============================================================================================

function  RRL_REVIZION_CELL_PALL( 
   articul1 varchar2, CELL1 varchar2 , count_pal int , revision_row_id1 int , 
    user_id1 varchar2 ) return varchar2

 -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ. пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ. 
-- пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅ.
--    пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ. 
is
new_event_uid int;
tmp varchar2 (250);
count_pal_fixed int;
counter_invent_p int;
/*cursor rema_in_p  is -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ.
  select sum(rm.REMAIN) as RM1 , count( DISTINCT rm.UID_POLETA ) kk , 
  rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA
    and    pal.ARTICUL=articul1  and rm.REMAIN>0
  order by    pal.EXPIRY_DATE asc; */

-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ.
rows_cnt int;
cursor rema is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL=CELL1 and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

cursor rema_invent_p  is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

begin
count_pal_fixed:=0;
rows_cnt:=0;

-- пїЅпїЅ пїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ 
for rrow in rema loop
  rows_cnt:=rows_cnt+1;
    count_pal_fixed:=count_pal_fixed+1;
    if(count_pal_fixed>count_pal) then -- пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ
        tmp := RABAEV.RRL_INTERNAL_MOVE2(
            rrow.UID_POLETA ,  'INVENT_P' ,
            rrow.remain , user_id1 );
     end if;
end loop;

if( count_pal_fixed>count_pal  ) then
tmp:= concat( 'пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ ' , concat( to_char( count_pal_fixed-count_pal ) , ' пїЅпїЅпїЅпїЅпїЅпїЅ'));
end if;

if( count_pal_fixed < count_pal  ) then
tmp:= concat( 'пїЅпїЅпїЅпїЅпїЅпїЅпїЅ ' , concat( to_char(count_pal- count_pal_fixed ) , ' пїЅпїЅпїЅпїЅпїЅпїЅ'));
counter_invent_p:=0;
      for rrow2 in rema_invent_p loop -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ.
          counter_invent_p:=counter_invent_p+1;    
          if(  counter_invent_p<=count_pal-count_pal_fixed ) then
          
           SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;
           
           insert into rrl_events ( ID_EVENT  ,  cell_from ,cell_to , date_event ,count_event,
           type_event,uid_poleta,user_id ) 
           values (new_event_uid, 'INVENT_P' , CELL1 , systimestamp , 
           rrow2.remain ,2 ,rrow2.uid_poleta, user_id1 );
          
          end if;
      end loop;
end if;

if( count_pal_fixed = count_pal  ) then
 tmp:= 'ok';
end if;
 
update RRL_REVISION_ROW set REMARK1 = tmp , NUM_OF_PALL=count_pal  where id=revision_row_id1;
commit;
return tmp;

exception 
       when no_data_found then  return 'neok';
       when others then raise;


END;


-- пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ.
function  RRL_REVIZION_CLEAR_MINUS( revision_id1 int , user_id1 varchar2 ) return int is
 new_event_uid int;
 cell4 varchar2(255);
 tmp varchar2(255);
 articul5 varchar2(255);
 
 cursor cells1  is select distinct rr.cell , rr.articul1 from rrl_revision_row rr 
 where rr.revision_id=revision_id1 ;

 cursor min_rem is select rem1.cell , rem1.uid_poleta , rem1.remain 
        from rrl_remains rem1 , rrl_pallets pts where pts.uid_pallet=rem1.uid_poleta and
        pts.articul = articul5 and  rem1.cell=cell4 and rem1.remain<0;

begin

    for cell3 in cells1 loop
    cell4:=cell3.cell;    
    articul5:=cell3.articul1;
        for rrow in min_rem loop   
           SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;           
           insert into rrl_events ( ID_EVENT  ,  cell_from ,cell_to , date_event ,count_event,
           type_event,uid_poleta,user_id ) 
           values (new_event_uid , CELL4 , 'INVENT_P'  , systimestamp , 
           rrow.remain ,2 ,rrow.uid_poleta, user_id1 );
        end loop;
        
    end loop;
    commit;
return 1;
end;

function  RRL_REVIZION_CELL_SHT( 
   articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , 
    user_id1 varchar2 ) return varchar2

 -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ. пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ. 
-- пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅ.
--    пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ. 
is
new_event_uid int;
tmp varchar2 (250);
counter_invent_p number;
to_spis number;

-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ.

cursor rema is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL=CELL1 and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

cursor rema_invent_p  is select  rm.REMAIN   , rm.UID_POLETA 
  from rrl_remains rm , rrl_pallets pal 
  where rm.CELL='INVENT_P' and pal.UID_PALLET=rm.UID_POLETA and  pal.ARTICUL=articul1 
    and  rm.REMAIN  >0 
  order by pal.EXPIRY_DATE desc;

count_sht_rem number;
how_many_return number;

begin


count_sht_rem:= 0;
to_spis:=0;

-- пїЅпїЅ пїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ 
for rrow in rema loop
--   пїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ  пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ, пїЅпїЅ 
--        пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ, пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ= пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ
--        пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ := 0
     count_sht_rem:=count_sht_rem+rrow.remain;
    if( count_sht_rem>count_sht ) then
        if( count_sht_rem-count_sht>rrow.remain ) then
                   tmp := RABAEV.RRL_INTERNAL_MOVE2(
                      rrow.UID_POLETA ,  'INVENT_P' ,
                      rrow.remain , user_id1 );
            else
                   tmp := RABAEV.RRL_INTERNAL_MOVE2(
                      rrow.UID_POLETA ,  'INVENT_P' ,
                      count_sht_rem-count_sht , user_id1 );
        end if;
    end if;
   
              
end loop;


if( count_sht_rem=count_sht  ) then
    tmp:= 'ok';
end if;


if( count_sht_rem-count_sht>0  ) then
tmp:= concat( 'пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ ' , concat( to_char( count_sht_rem-count_sht ) , ' пїЅпїЅ'));
end if;

if( count_sht_rem-count_sht<0  ) then
tmp:= concat( 'пїЅпїЅпїЅпїЅпїЅпїЅпїЅ ' , concat( to_char( -count_sht_rem+count_sht ) , ' пїЅпїЅ'));
counter_invent_p:=0;
how_many_return:=-count_sht_rem+count_sht;

      for rrow2 in rema_invent_p loop -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ.
          counter_invent_p:=counter_invent_p+rrow2.remain;
          if( how_many_return>0 ) then        
              if( rrow2.remain>how_many_return ) then
                  to_spis:=how_many_return;
                  how_many_return:=0;
              else
                  to_spis:=rrow2.remain;
                  how_many_return:=how_many_return-rrow2.remain;
              end if;

           SELECT RABAEV.RRL_EVENT_ID_SQ.NEXTVAL INTO new_event_uid  FROM dual;           
           insert into rrl_events ( ID_EVENT  ,  cell_from ,cell_to , date_event ,count_event,
           type_event,uid_poleta,user_id ) 
           values (new_event_uid, 'INVENT_P' , CELL1 , systimestamp , 
          /* rrow2.remain */ to_spis ,2 ,rrow2.uid_poleta, user_id1 );

          end if;
      end loop;
      
end if;


 
update RRL_REVISION_ROW set REMARK1 = tmp , count1=count_sht  where id=revision_row_id1;
commit;
return tmp;

exception 
       when no_data_found then  return 'neok';
       when others then raise;


END;



function CreateNaklad_2_revizion( rev_id1 int ) return int is
         rev_naklad_id1 int;
         ret int;
         ware_id3 int;
begin

  select r.rev_naklad_id , ware_id into rev_naklad_id1 , ware_id3 from rrl_revizion r where id= rev_id1;
  if( not rev_naklad_id1 is null ) and (  rev_naklad_id1 >0 ) then
      return rev_naklad_id1;
  end if;

  ret:=ADD_RRL_PRIH_NAKLAD2( NAKLAD_NUMBER => concat( 'INV_' , to_char(rev_id1) ) , 
                         DATE_OF_NAKLAD => sysdate ,DATE_OF_ACCEPT => sysdate,
                         POSTAVSHIK_NAME => 'INV', 
                         SM_NAKLAD_NUMBER => concat( 'INV_' , to_char(rev_id1) ) ,
                         ZAKAZ_NUMBER1 => concat( 'INV_' , to_char(rev_id1) ) ,
                         ware_id1 => ware_id3 );
               
  if( ret>0 ) then
      update RABAEV.RRL_PRIHOD_NAKLAD set condition=2 where id=ret;
      update  rrl_revizion set rev_naklad_id=ret where id= rev_id1;
  end if;
            
  return ret;
exception
  when no_data_found then return -1;
  when others then return -2;
end;

-- ============================================================================================


FUNCTION  RRL_INV_CREATE_LINE5 
( 
    cell1 varchar2 ,
    articul2 varchar2,
    count1 NUMBER ,
    expiury_date date ,
    fasovka_id1 int ,
    brak_perc1 number ,
    pall_weight1 number , 
    pall_n int ,
    tn_weight1 number ,
    count_kor1 number ,
    user_id2 varchar2 , 
    NAKLAD_ID int
)
    RETURN varchar2 IS 
    price Number;
    ret2 varchar2(255);
    event_id int;
    pallet_name varchar2(255);


BEGIN
-- =================================================
pallet_name:= CONCAT( Concat( Concat( Concat('P_' , articul2 ) , '_G3_') , cell1) , concat( '_' ,to_char(pall_n) ) ) ;
pallet_name:=replace(pallet_name , 'пїЅ' ,'T' );
begin
        insert into RABAEV.RRL_PALLETS
        (
          UID_PALLET       ,
          ARTICUL           ,
          CREATION_DATE     ,
          EXPIRY_DATE       ,
          UNIT_COUNT        ,
          PRICE             ,
          PRIHOD_NAKLAD_ID  
        )values
        (
            pallet_name , 
            articul2 ,
            sysdate ,
            expiury_date ,
            count1 , 
            1,
            NAKLAD_ID
        );
        exception
          when others then return 'EXISTS';
end;
-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅ

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
          CELL1 ,
          expiury_date , 
          expiury_date , 
          count1 , 
          1 ,
          pallet_name ,
          user_id2 ,
          NAKLAD_ID 
            );
    
    ret2:=RABAEV.RRL_PRIHODPALLET_CHANGE(PALLET_UID1 => pallet_name ,art => articul2 ,
        UNIT_COUNT1 => count1 ,DEFECT_PERC1 => brak_perc1 ,COUNT_KOR1 => count_kor1 ,
        WEIGHT_BRUTTO1 => pall_weight1 , WEIGHT_TN1 => tn_weight1 ,MOD_ID1 => fasovka_id1 );

return pallet_name;
-- =================================================
END ;



FUNCTION  close_revision( rev_id int ) return int is
  tmp int;
begin
  
  tmp:= REVIZION.rev_create_snap_shot_after( rev_id );
  update rrl_revizion rev set rev.condition=2 where rev.id=rev_id;
  
  return 1;
end;


-- пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ
-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ.
function rev_create_snap_shot_before( rev_id int ) return int is
    snap_id1 int;
    tmp int;
    cursor sss is select rs.cell , rs.articul1  
     from rrl_revision_row rs where rs.revision_id = rev_id ;
begin
 
  select rv.SNAPSHOT_BEFORE into snap_id1 
         from rrl_revizion rv where id= rev_id;
  if( snap_id1 is null ) then
  update rrl_revizion set condition=1 where ID= rev_id;
  
      snap_id1 := REMAINS.create_snapshot(type2 => 1);
      update rrl_revizion set SNAPSHOT_BEFORE=snap_id1 where  id= rev_id;
      for s in sss loop
          tmp:=REMAINS.add_row_2_snapshot(snap_shot_id1 => snap_id1 ,cell1 => s.cell ,articul1 => s.articul1);
      end loop;
      
      return snap_id1;
  else
      return snap_id1;
  end if;
return snap_id1;
end;
-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ.


function rev_create_snap_shot_after( rev_id int ) return int is
    snap_id1 int;
    tmp int;
    cursor sss is select rs.cell , rs.articul1  
     from rrl_revision_row rs where rs.revision_id = rev_id ;
begin
 
  select rv.SNAPSHOT_AFTER into snap_id1 
         from rrl_revizion rv where id= rev_id;
  if( snap_id1 is null ) then
      snap_id1 := REMAINS.create_snapshot(type2 => 2);
      update rrl_revizion set SNAPSHOT_AFTER=snap_id1 where  id= rev_id;
      for s in sss loop
          tmp:=REMAINS.add_row_2_snapshot(snap_shot_id1 => snap_id1 ,cell1 => s.cell ,articul1 => s.articul1);
      end loop;
      
      return snap_id1;
  else
      return snap_id1;
  end if;
return snap_id1;
end;


function remain_before( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number is
 snap_before int;
 snap_after int;
ret number;
begin

    select rr.snapshot_before , rr.snapshot_after 
    into snap_before ,  snap_after
     from rrl_revizion rr 
    where rr.id=rev_id;
    
    
  select sum(rsr.remain) into ret from rrl_remain_snapshot_rows rsr where rsr.snap_shot_id = snap_before and 
  rsr.articul = articul1 and rsr.cell=cell1 ;
return ret;
exception     
       when no_data_found then return null;
       when others then return -9999;
end;


function remain_after( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number is
 snap_before int;
 snap_after int;
ret number;
begin

    select rr.snapshot_before , rr.snapshot_after 
    into snap_before ,  snap_after
     from rrl_revizion rr 
    where rr.id=rev_id;

  select sum(rsr.remain) into ret from rrl_remain_snapshot_rows rsr where rsr.snap_shot_id = snap_after and 
  rsr.articul = articul1 and rsr.cell=cell1 ;
return ret;
exception     
       when no_data_found then return null;
       when others then return -9999;
end;



begin
null;
end REVIZION;
/

---------------------------------------

--  New package body transport_task  --
---------------------------------------
create or replace package body TRANSPORT_TASK is
 

function PRINT_PALLET_WEIGHT( PALLET_UID2  varchar2 ) return varchar2 is
         ret number;
         ware_id1 int;
         count_kor1 int;
         count_rs int;
         articul1 varchar2(255);
         sum_q number;
begin
  
      select round( TRIAL_WEIGHT , 2 ) ,  pts.ware_id into ret ,  ware_id1 
      from rrl_sborka_pallets pts 
      where pts.pallet_uid=PALLET_UID2;
      if( ret>0 )  then 
          return to_char(ret); 
      end if;
      
      if ware_id1 = 5 then  -- пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅ 
         select sum( rs.pack_count ) into  count_kor1
         from rrl_sborka_pallet_rows rs where rs.pallet_uid = PALLET_UID2;
         return concat( to_char( count_kor1 ) , ' пїЅпїЅпїЅ.' );
      end if; -- пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅ
      
      select count( rs.id ) , sum( rs.pack_count ) , sum( rs.quantity ) 
      into count_rs , count_kor1 , sum_q
             from rrl_sborka_pallet_rows rs 
             where rs.pallet_uid = PALLET_UID2;
       if( count_rs=1 ) then -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ
             select rs.articul into  articul1 
             from rrl_sborka_pallet_rows rs  where rs.pallet_uid = PALLET_UID2;
             if( articul1='пїЅ0000012233' ) then
                  return concat( to_char( count_kor1 ) , ' пїЅпїЅпїЅ.' );
             end if;
       end if;
      
      return to_char(ret);      
exception 
  when no_data_found then return '-';
end;

  -- Function and procedure implementations
function can_print( tt_id int , user_id1 varchar2 ) return varchar2 is
    tmp varchar2(255) ;
    ml int;
    cnt_pt int;
  begin
  
     select type1.min_pallet_load into ml                                             
     from rrl_transport_task tt , rrl_tr_vehicle  veh , rrl_transport_type type1        
         where   tt.id=tt_id and veh.num=tt.transport and veh.tr_type = type1.transporttype ;   
  
     select count( pts.pallet_uid ) into cnt_pt from rrl_sborka_pallets pts 
            where  pts.transtask_id=tt_id;

       if( cnt_pt < ml ) then 
           
          if( rrl_has_wright( user_id1 , 'SEND_EMPTY_TRUCK'  )=1 ) then 
              return 'ok';
          end if;
           return concat( 'пїЅпїЅпїЅ пїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ. пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ ' , concat( to_char(cnt_pt) , concat( ' пїЅпїЅпїЅпїЅпїЅпїЅпїЅ=' ,  to_char( ml) )  ) )  ;
       end if;
  return 'ok';
  exception 
         when no_data_found then  return 'ok';
         when others then return 'ok';
    
    return tmp;
  end;


-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ 
function pallet_count( tt_id int ) return number is
         tmp number;
begin
         
   select count( pts.id ) into tmp from rrl_sborka_pallets pts where pts.transtask_id = tt_id;         
   return tmp;    
exception
   when no_data_found then
         return 0; 
end;

-- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ 
function stoim_pall_sb( pall_uid1 varchar2 ) return number is
  price1 number;
  total1 number;
  stoim_of_current_row number;
  cursor ss is
     select * from rrl_sborka_pallet_rows rs where rs.pallet_uid = pall_uid1;
begin
  total1:=0;
     for r in ss loop
       stoim_of_current_row:=0;
         if not r.prihod_pallet_uid is null then -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ
         begin
            select pts.price into price1 from rrl_pallets pts where pts.uid_pallet=r.prihod_pallet_uid ;
         stoim_of_current_row:=r.quantity*price1;
         exception
           when no_data_found then
             null;
         end;
         end if;
         
         if stoim_of_current_row=0 then -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ
            begin
            
                  select art.last_price into price1  from rrl_articuls art where art.acticul=r.articul  ;
                  stoim_of_current_row:=r.quantity*price1;
                  
            exception
              when no_data_found then stoim_of_current_row:=1;
            end;

         end if;
         total1:=total1+stoim_of_current_row;
     end loop;
     return total1;
end ;

function stoim_tt( tt_id int )  return number is
  total1 number;
begin
  select sum( stoim_pall_sb( pts.pallet_uid ) ) into total1 
         from  rrl_sborka_pallets pts where pts.transtask_id=tt_id;
  return total1;
end;

-- пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ 
function tt_wares( tt_id int ) return varchar2 is
    tmp varchar2(1024);
    cursor sss is 
    select distinct RRL_SKLADNAME_BY_ID( pts.ware_id ) g
       from rrl_sborka_pallets pts where pts.transtask_id = tt_id;         

begin
  tmp:='';
  
           for i in sss loop         
               tmp:= concat( tmp , concat( to_char(i.g) ,' ' ) );
           end loop;             
    return tmp;    
exception
   when no_data_found then
         return ''; 
   when others then return tmp;
end;

function test1 return int is
curr_pr number;
cursor arts is 
select acticul from rrl_articuls ;
begin 
       for a in arts loop
        begin
         select price into curr_pr from (
             select pts.articul , pts.price 
                    from rrl_pallets pts where pts.articul=a.acticul 
                    and price>0 order by pts.creation_date desc
             ) where rownum<=1;
        update rrl_articuls set last_price=curr_pr where acticul=a.acticul;
        exception
          when no_data_found then null;
        end;   
       end loop;
       return 1;
end;


FUNCTION TT_READY_PERC( IDTT int ) RETURN number IS 
  tmpVar number;
  itogo int;
  sobrano int;
BEGIN
   -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ 
   tmpVar := 0;
    -- пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ
    select count(ID)  into itogo from RABAEV.RRL_SBORKA_PALLETS where  TRANSTASK_ID  = IDTT;
    -- пїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ, пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ , пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅ пїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ
    select count(ID)  into sobrano from RABAEV.RRL_SBORKA_PALLETS P   where  TRANSTASK_ID  = IDTT 
        and ( P.prooved=1 or P.prooved_by_scan=1 or P.condition=2 );  
    tmpVar:= sobrano / itogo ; 
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
END;

FUNCTION TT_UNREADY_COUNT( IDTT int ) RETURN number IS 
  tmpVar number;
  itogo int;
  sobrano int;
BEGIN
   tmpVar := 0;
    select count(ID)  into itogo from RABAEV.RRL_SBORKA_PALLETS where  TRANSTASK_ID  = IDTT;
    select count(ID)  into sobrano from RABAEV.RRL_SBORKA_PALLETS P   where  TRANSTASK_ID  = IDTT 
        and ( P.prooved=1 or P.prooved_by_scan=1 or P.condition=2 );  
    tmpVar:=   itogo - sobrano; 
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN -1;
END;

-- пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅпїЅпїЅ 
function tt_unready_wares( tt_id int ) return varchar2 is
    tmp varchar2(1024);
    cursor sss is 
    select  RRL_SKLADNAME_BY_ID( pts.ware_id ) g , count(pts.pallet_uid) cnt
       from rrl_sborka_pallets pts where pts.transtask_id = tt_id  
       and not ( prooved=1 or prooved_by_scan=1 or condition=2 )
           group by  RRL_SKLADNAME_BY_ID( pts.ware_id ) ;         

begin
  tmp:='';
  
           for i in sss loop         
               tmp:= concat( tmp , concat( to_char(i.g) , concat('=[' , concat( to_char( i.cnt) , '] ') ) ) );
           end loop;             
    return tmp;    
exception
   when no_data_found then
         return '!'; 
   when others then return tmp;
end;



FUNCTION TT_VODITEL_TEL( VODITEL_ID1 int ) RETURN varchar2 IS 
    tmpVar varchar2(255);
BEGIN
   tmpVar := 0;
   select VV.Tel into tmpVar 
          from RABAEV.RRL_TR_VODITEL VV where  ID = VODITEL_ID1 ;
 
   RETURN tmpVar;
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       RETURN '';
END ;

FUNCTION TT_REORDER_ADR( IDTT int ) RETURN number IS
BEGIN
   RETURN RABAEV.RRL_TT_REORDER_ADR( IDTT );
EXCEPTION
   WHEN NO_DATA_FOUND THEN
      RETURN 0;
END TT_REORDER_ADR;


begin
  -- Initialization
  null;
end TRANSPORT_TASK;
/

--------------------------------------

--  New trigger rrl_object_trg  --
----------------------------------
CREATE OR REPLACE TRIGGER RRL_OBJECT_TRG
BEFORE UPDATE
ON RABAEV.RRL_OBJECT 
REFERENCING NEW AS NEW OLD AS OLD
FOR EACH ROW
BEGIN
  -- your code here 
  -- (Trigger template "Default" could not be loaded.)            
  if( :New.parent_object = :new.object_name ) then 
       
   RAISE_APPLICATION_ERROR(-21000 , 'пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅ пїЅпїЅпїЅпїЅпїЅпїЅ пїЅпїЅпїЅпїЅ');
  end if;
  
END;
/

---------------------------------------------

