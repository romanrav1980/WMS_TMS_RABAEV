 function instant(p_wall date,p_zone varchar2)return date is v_result date;v_count number;
 begin
  select count(distinct candidate),min(candidate) into v_count,v_result from (
   select p_wall-offset_days candidate from (
    select distinct cast(from_tz(cast(p_wall+(level-49)/24 as timestamp),'UTC') at time zone (p_zone) as date)
     -(p_wall+(level-49)/24) offset_days from dual connect by level<=97))
   where cast(from_tz(cast(candidate as timestamp),'UTC')at time zone(p_zone)as date)=p_wall;
  if v_count!=1 then raise_application_error(-20886,'STORE_WINDOW_DST_AMBIGUOUS_OR_NONEXISTENT');end if;
  return v_result;
 end;
