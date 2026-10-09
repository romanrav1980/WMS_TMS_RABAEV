create or replace package REVIZION is

  
  
  
  
function revision_cond( rev_id int ) return int ;
function clear_cell2( cell1 varchar2     ) return int;
function clear_cell( cell1 varchar2 , puid varchar2   ) return int ;
function add_row_2_revizion( cell1 varchar2 , revision_id1 int   ) return int;
function create_revizion( ware_id1 int , user_id1 varchar2 ) return int ;
function revision_cell_kor( cell1 varchar2 , revision_id1 int ,  count2 number , user_id3 varchar2 ,p_operation_id varchar2 default null) return varchar2 ;
function add_row_2_reviz_type_art( cell1 varchar2 , revision_id1 int   ) return int;
function  RRL_REVIZION_CELL_PALL( articul1 varchar2, CELL1 varchar2 , count_pal int , 
   revision_row_id1 int , user_id1 varchar2 ) return varchar2 ;
   
function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int ;
function articul_name( art varchar2 ) return varchar2;
function update_revision_row( cell1 varchar2 , articul2 varchar2 ,  revision_rowid int ,  rev_id2 int   ) return int;
function CreateNaklad_2_revizion( rev_id1 int ) return int ;
function revision_cell_sht_deleted( cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2 ,p_operation_id varchar2 default null) return varchar2 ;
function  RRL_REVIZION_CELL_SHT( articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , user_id1 varchar2 ,p_operation_id varchar2 default null) return varchar2;
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
,p_operation_id varchar2 default null) return varchar2;

function rev_create_snap_shot_after( rev_id int ) return int ;
function rev_create_snap_shot_before( rev_id int ) return int ;
FUNCTION  close_revision( rev_id int ) return int;

function remain_after( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number  ;
function remain_before( rev_id int ,articul1 varchar2 , cell1 varchar2  ) return number  ;


end REVIZION;

/
create or replace package body REVIZION is

 
function revision_cond( rev_id int ) return int is
  ret int;
begin 
  select rr.condition into ret from rrl_revizion rr where id= rev_id;
  return ret;       
exception
         when no_data_found then return -1;
end;

 
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
function clear_cell(cell1 varchar2 , puid varchar2) return int is
 state varchar2(20);row_id number;other_row number;article varchar2(160);facts json_object_t:=json_object_t();
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return REVIZION_SP_OLD.clear_cell(cell1,puid);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'INVENTORY_MEASURED_COUNT_REQUIRED: inventory-count.html');
end;
function clear_cell2(cell1 varchar2) return int is
 state varchar2(20);row_id number;other_row number;article varchar2(160);facts json_object_t:=json_object_t();
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return REVIZION_SP_OLD.clear_cell2(cell1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'INVENTORY_MEASURED_COUNT_REQUIRED: inventory-count.html');
end;


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



function add_row_2_reviz_type_art( cell1 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor rema is 
select distinct pl.articul  from rrl_remains rems, rrl_pallets pl 
   where rems.uid_poleta=pl.uid_pallet and  rems.cell=cell1 ; 

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;


   for rr in rema loop
       delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  
       and CELL= cell1 and articul1=rr.articul ;
       insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , cell1 , sysdate , rr.articul );
       
   end loop;

  return id1;
end;



function add_row_2_reviz_type_art2( cell1 varchar2 , articul2 varchar2 , revision_id1 int   ) return int is
id1 int;    

cursor rema is 
select distinct pl.articul  from rrl_remains rems, rrl_pallets pl 
   where rems.uid_poleta=pl.uid_pallet and  rems.cell=cell1 and pl.articul=articul2 ; 

begin
  if revision_cond(revision_id1)>1 then
    return 0;
  end if;


   for rr in rema loop
       delete from RABAEV.RRL_REVISION_ROW where REVISION_ID = revision_id1  
       and CELL= cell1 and articul1=rr.articul ;
       insert into  RABAEV.RRL_REVISION_ROW (REVISION_ID ,CELL , REV_DATE , ARTICUL1 )
       values ( revision_id1 , cell1 , sysdate , rr.articul );
       
   end loop;

  return id1;
end;




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
        
        
          update    RABAEV.RRL_REVISION_ROW rr set  rr.cell=cell1 , rr.articul1=articul2 
                    where id=revision_rowid ; 
          return revision_id1;
      else

      insert into RABAEV.RRL_REVISION_ROW  ( REVISION_ID , CELL , ARTICUL1      ) values 
           (rev_id2 , cell1 , articul2 );
           select RRL_REVISION_ROW_SQ.CURRVAL into row_ret from dual;
           return  row_ret;
      
    end if;
  
  
  
  
  
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
function revision_cell_kor(cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2,p_operation_id varchar2 default null) return varchar2 is
 state varchar2(20);row_id number;other_row number;article varchar2(160);facts json_object_t:=json_object_t();
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return REVIZION_SP_OLD.revision_cell_kor(cell1,revision_id1,count2,user_id3);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 return RRL_STOCK_REVISION_ENTRY.count_document(cell1,revision_id1,count2,'BOX',user_id3,p_operation_id);
end;
function revision_cell_sht_deleted(cell1 varchar2 , revision_id1 int , count2 number , user_id3 varchar2,p_operation_id varchar2 default null) return varchar2 is
 state varchar2(20);row_id number;other_row number;article varchar2(160);facts json_object_t:=json_object_t();
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return REVIZION_SP_OLD.revision_cell_sht_deleted(cell1,revision_id1,count2,user_id3);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 return RRL_STOCK_REVISION_ENTRY.count_document(cell1,revision_id1,count2,'EA',user_id3,p_operation_id);
end;
function RRL_REVIZION_CELL_PALL(articul1 varchar2, CELL1 varchar2 , count_pal int , revision_row_id1 int , 
    user_id1 varchar2) return varchar2 is
 state varchar2(20);row_id number;other_row number;article varchar2(160);facts json_object_t:=json_object_t();
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return REVIZION_SP_OLD.RRL_REVIZION_CELL_PALL(articul1,CELL1,count_pal,revision_row_id1,user_id1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'PALLET_COUNT_IS_NOT_MEASURED_QUANTITY: inventory-count.html');
end;
function RRL_REVIZION_CLEAR_MINUS(revision_id1 int , user_id1 varchar2) return int is
 state varchar2(20);row_id number;other_row number;article varchar2(160);facts json_object_t:=json_object_t();
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return REVIZION_SP_OLD.RRL_REVIZION_CLEAR_MINUS(revision_id1,user_id1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 raise_application_error(-20886,'NEGATIVE_STOCK_REQUIRES_EXPLICIT_CORRECTION: inventory-count.html');
end;
function RRL_REVIZION_CELL_SHT(articul1 varchar2, CELL1 varchar2 , count_sht number , revision_row_id1 int , 
    user_id1 varchar2,p_operation_id varchar2 default null) return varchar2 is
 state varchar2(20);row_id number;other_row number;article varchar2(160);facts json_object_t:=json_object_t();
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return REVIZION_SP_OLD.RRL_REVIZION_CELL_SHT(articul1,CELL1,count_sht,revision_row_id1,user_id1);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 return RRL_STOCK_REVISION_ENTRY.count_row(articul1,CELL1,count_sht,'EA',revision_row_id1,user_id1,p_operation_id);
end;



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
function RRL_INV_CREATE_LINE5(cell1 varchar2 ,
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
    NAKLAD_ID int,p_operation_id varchar2 default null) return varchar2 is
 state varchar2(20);row_id number;other_row number;article varchar2(160);facts json_object_t:=json_object_t();
begin
 select STATE into state from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if state='PREPARED' then return REVIZION_SP_OLD.RRL_INV_CREATE_LINE5(cell1,articul2,count1,expiury_date,fasovka_id1,brak_perc1,pall_weight1,pall_n,tn_weight1,count_kor1,user_id2,NAKLAD_ID);end if;
 if state!='ACTIVE' then raise_application_error(-20885,'STOCK_RELEASE_NOT_ACTIVE');end if;
 facts.put('article',articul2);facts.put('cell',cell1);facts.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(count1));
 facts.put('expiry_date',to_char(expiury_date,'YYYY-MM-DD'));facts.put('mod_id',fasovka_id1);
 facts.put('defect_percent',brak_perc1);facts.put('gross_weight',pall_weight1);facts.put('net_weight',tn_weight1);
 facts.put('box_count',count_kor1);facts.put('pallet_number',pall_n);facts.put('receipt_document_id',NAKLAD_ID);
 return RRL_STOCK_REVISION_ENTRY.birth_legacy(facts.to_clob,user_id2,p_operation_id);
end;



FUNCTION  close_revision( rev_id int ) return int is
  tmp int;
begin
  
  tmp:= REVIZION.rev_create_snap_shot_after( rev_id );
  update rrl_revizion rev set rev.condition=2 where rev.id=rev_id;
  
  return 1;
end;




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
