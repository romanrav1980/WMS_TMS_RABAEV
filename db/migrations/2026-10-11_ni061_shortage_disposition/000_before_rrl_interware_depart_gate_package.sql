create or replace package RRL_INTERWARE_DEPART_GATE authid definer as 
 function promises(p_trip number)return clob; 
 procedure assert_ready(p_promises clob); 
end;
/
