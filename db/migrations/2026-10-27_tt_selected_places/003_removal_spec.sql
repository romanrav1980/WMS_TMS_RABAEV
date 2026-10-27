create or replace package RRL_TT_PLACE_REMOVAL_API authid definer as
 -- C-0176: remove selected places of one assembly from a trip through RRL_TT_ADD_PALL(0,st,id); one transaction, journalled.
 -- The version of the assembly's membership on the trip: every place (id, trip, condition, active load) and the trip header.
 function source_hash(p_trip number,p_st varchar2) return varchar2;
 procedure remove(p_request clob,p_actor varchar2,p_result out clob);
end;
/
