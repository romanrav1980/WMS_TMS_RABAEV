create or replace package RRL_YARD_VISIT_API authid definer as
 -- Yard visit of one TRADECASE site: EXPECTED -> ARRIVED (queue) -> AT_DOCK -> WORKING -> WORK_DONE -> DEPARTED, CANCELLED before work.
 -- No stock, reservation or loading effect: the loading/departure facts stay in their own commands.
 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob);
 function visits(p_ware number,p_actor varchar2,p_active number)return clob;
 -- Visits touching [p_from,p_to) with their immutable event times, for the resource timeline (times YYYY-MM-DDTHH:MI:SS+TZH:TZM).
 function history(p_ware number,p_actor varchar2,p_from varchar2,p_to varchar2)return clob;
 -- 1 when every source owner of the trip is readable by the actor; used inside SQL so hidden visits are filtered before any limit.
 function visit_visible(p_actor varchar2,p_ware number,p_visit number)return number;
 function trip_visible(p_actor varchar2,p_ware number,p_trip varchar2)return number;
end;
/
