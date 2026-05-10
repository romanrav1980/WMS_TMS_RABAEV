
CREATE PACKAGE BODY RABAEV.GOODS_TO_PICK
is
 
function add_summary_task( ware_id1 int ) return int
is

    select RRL_SUMMARY_PICK_LIST_SQ.Nextval into id1 from dual;
    insert into  RABAEV.RRL_SUMMARY_PICK_LIST (ID ,CREATEDATE , CONDITION , ware_id) values  ( id1  , systimestamp  , 0 , ware_id1 );
return id1;
end add_summary_task;



-- янгдюмхе ясллюпмнцн яанпнвмнцн кхярю 
function add_pallet_2_summary_task(  PUID varchar2 , summary_task_id1 int ) return int;
is

   select condition into tmp from from RABAEV.RRL_SUMMARY_PICK_LIST where id=summary_task_id1 and condition=0;
    update  RABAEV.RRL_SBORKA_PALLETS  set summary_task_id  = summary_task_id1 where PALLET_UID=PUID and summary_task_id  is null;
 return 1;
 exception when no_data_found then return 0;

end add_pallet_2_summary_task;

 -- онксвхрэ оепбши янгдюммши х мегюбепьеммши ясллюпмши яанпнвмши кхяр 
function get_opened_summary_task(ware_id1 int) return int
is
begin

    begin 
        select  min(ID) into id1 from RABAEV.RRL_SUMMARY_PICK_LIST where condition=0 and ware_id=ware_id1 order by CREATEDATE desc  ;
        return id1;
    exception 
        when no_data_found then  return add_summary_task( ware_id1  );
    end ;
    return add_summary_task( ware_id1  );
end get_opened_summary_task;


-- янгдюрэ гюдювх дкъ бндхрекеи   пхврпюйю 
function create_wtasks( summary_task_id1 int )
declare
cursor sss is
 select RS.ARTICUL , sum( RS.QUANTITY ) from RABAEV.RRL_SBORKA_PALLETS PAL , 
RABAEV.RRL_SBORKA_PALLET_ROWS RS
 where PAL.SUMMARY_TASK_ID = summary_task_id1 and
 PAL.PALLET_UID=RS.PALLET_UID group by RS.ARTICUL; -- order by ОНПЪДНЙ ЯАНПЙХ 
  ;
begin
select condition into tmp from RABAEV.RRL_SUMMARY_PICK_LIST where id=summary_task_id1;
    if(tmp<>0) then
     return 0;    
    end if;
    
    for ss in sss loop
         DBMS_OUTPUT.put_line(  ss.ARTICUL );  
    
    end loop;
    
    update  RABAEV.RRL_SUMMARY_PICK_LIST  set condition=1 where id=summary_task_id1;
retun 1;
end ;


END GOODS_TO_PICK;


