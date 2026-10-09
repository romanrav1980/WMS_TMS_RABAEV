create or replace FUNCTION        RRL_REVIZION_CELL_SP_OLD

(
    CELL1 varchar2 ,
    count1 number ,
    user_id1 varchar2
) return varchar2 accessible by(function RRL_REVIZION_CELL)
 
 
 
 
 
 
 
 
 
 
 
 
 
is

cursor rema is select rm.REMAIN , rm.UID_POLETA from rrl_remains rm  where rm.CELL=CELL1 and   rm.REMAIN>0 
order by  rm.TIME_OF_LAST_UPDATE desc;

tmp varchar2(255);
to_spis number;
ostatok number;
begin
ostatok:=count1;

for  rr in rema  loop

    if(ostatok>=rr.REMAIN) then
    
        null;

    else 
         

        if(rr.REMAIN<ostatok) then
            to_spis:=rr.REMAIN;
        else
            to_spis:=rr.REMAIN-ostatok ;
        end if;

        tmp := RABAEV.RRL_INTERNAL_MOVE2(
        rr.UID_POLETA , 
        'INVENT' ,
        to_spis ,
        user_id1 );


    end if;

ostatok:=ostatok- rr.REMAIN;
end loop;



 


if( ostatok > 0  ) then 
null;

    return 'neok';
else 
 
    return 'ok';
end if;


return 'ok';

exception 
when no_data_found then  return 'neok';
when others then raise;


END RRL_REVIZION_CELL_SP_OLD;
/
