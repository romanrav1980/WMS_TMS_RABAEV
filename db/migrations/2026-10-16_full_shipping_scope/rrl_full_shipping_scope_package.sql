create or replace package RRL_FULL_SHIPPING_SCOPE authid definer as
 procedure assert_hu(p_uid varchar2,p_actor varchar2);
 procedure assert_shipment(p_identifier varchar2,p_actor varchar2);
 procedure assert_trip(p_trip number,p_actor varchar2);
 procedure assert_request(p_request clob,p_actor varchar2);
end;
/
