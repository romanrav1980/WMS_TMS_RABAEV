
create function fff ( iddoc varchar2 )
int
as 
declare cntPos1 number;
begin
 mon_st_baseinsert(cntPos1 ,iddoc ) ;
 return cntPos1;
end;




